"""AI增强服务"""
from __future__ import annotations

import json
import re
import uuid
from decimal import Decimal, InvalidOperation
from datetime import date, datetime, timedelta
from html import unescape
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import settings
from app.models.activity import TaskInfo, VisitRecord
from app.models.ai import (
    AIAnalysisResult,
    AIConfig,
    AIPromptTemplate,
    AIRequestLog,
    AIRiskAlert,
    AISearchHistory,
)
from app.models.customer import CustomerInfo, ContactInfo
from app.models.opportunity import OpportunityInfo, StageDef


class AIService:
    """AI增强服务（当前为规则+启发式实现，后续可替换LLM）"""

    ENRICH_SUPPORTED_FIELDS = {
        "website",
        "address",
        "product_info",
        "company_info",
        "industry",
        "legal_person",
        "registered_capital",
        "establish_date",
        "company_size",
        "source",
        "remarks",
    }

    ENRICH_FIELD_LABELS = {
        "website": "网址",
        "address": "地址",
        "product_info": "产品信息",
        "company_info": "公司信息",
        "industry": "行业",
        "legal_person": "法人代表",
        "registered_capital": "注册资本",
        "establish_date": "成立日期",
        "company_size": "公司规模",
        "source": "客户来源",
        "remarks": "备注",
    }

    @staticmethod
    async def _ensure_default_config(db: AsyncSession) -> AIConfig:
        result = await db.execute(select(AIConfig).order_by(AIConfig.id.asc()).limit(1))
        config = result.scalar_one_or_none()
        if config:
            return config

        config = AIConfig(
            provider="glm",
            model_name="glm-4-flash",
            api_base="https://open.bigmodel.cn/api/paas/v4/chat/completions",
            temperature=0.3,
            max_tokens=1500,
            timeout_seconds=30,
            is_enabled=True,
            remark="默认GLM配置",
        )
        db.add(config)
        await db.flush()
        return config

    @staticmethod
    def _mask_api_key(api_key: Optional[str]) -> Optional[str]:
        if not api_key:
            return None
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

    @staticmethod
    def _extract_json_block(content: str) -> Dict[str, Any]:
        text = (content or "").strip()
        if not text:
            return {}

        fenced = re.search(r"```json\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
        if fenced:
            text = fenced.group(1).strip()

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(text[start:end + 1])
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    return {}
        return {}

    @staticmethod
    def _clean_html_text(raw: Optional[str]) -> str:
        if not raw:
            return ""
        text = re.sub(r"<[^>]+>", " ", raw)
        text = unescape(text)
        text = text.replace("\xa0", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _extract_first_by_keys(info: Dict[str, str], keys: List[str]) -> str:
        for k in keys:
            if k in info and info[k]:
                return info[k]
        return ""

    @staticmethod
    def _parse_registered_capital(raw: str) -> Optional[Decimal]:
        if not raw:
            return None
        text = str(raw).replace(",", "")
        matched = re.search(r"(\d+(?:\.\d+)?)", text)
        if not matched:
            return None
        value = Decimal(matched.group(1))
        unit_factor = Decimal("1")
        if "亿" in text:
            unit_factor = Decimal("100000000")
        elif "万" in text:
            unit_factor = Decimal("10000")
        elif "千" in text:
            unit_factor = Decimal("1000")
        try:
            return value * unit_factor
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _parse_establish_date(raw: str) -> Optional[date]:
        if not raw:
            return None
        text = str(raw).strip()
        text = text.replace("年", "-").replace("月", "-").replace("日", "")
        text = re.sub(r"[/.]", "-", text)
        text = re.sub(r"\s+", "", text)
        patterns = ("%Y-%m-%d", "%Y-%m", "%Y")
        for fmt in patterns:
            try:
                parsed = datetime.strptime(text, fmt)
                if fmt == "%Y":
                    return date(parsed.year, 1, 1)
                if fmt == "%Y-%m":
                    return date(parsed.year, parsed.month, 1)
                return parsed.date()
            except ValueError:
                continue
        m = re.search(r"(19|20)\d{2}-\d{1,2}-\d{1,2}", text)
        if m:
            try:
                return datetime.strptime(m.group(0), "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    @staticmethod
    async def _fetch_baike_profile(customer_name: str) -> Dict[str, Any]:
        """优先从百度百科抓取客户资料，失败时返回空结果。"""
        candidate_names = [customer_name.strip()]
        if customer_name and not customer_name.endswith("公司"):
            candidate_names.append(f"{customer_name.strip()}公司")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        for name in candidate_names:
            url = f"https://baike.baidu.com/item/{quote(name)}"
            try:
                async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
                    resp = await client.get(url)
                if resp.status_code != 200:
                    continue
                html = resp.text or ""
                if not html or ("百度百科" not in html and "baike.baidu.com" not in str(resp.url)):
                    continue

                summary = ""
                for pattern in [
                    r'<div[^>]*class="[^"]*lemma-summary[^"]*"[^>]*>(.*?)</div>',
                    r'<div[^>]*class="[^"]*J-summary[^"]*"[^>]*>(.*?)</div>',
                    r'<meta\s+name="description"\s+content="([^"]+)"',
                ]:
                    matched = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
                    if matched:
                        summary = AIService._clean_html_text(matched.group(1))
                        if summary:
                            break

                basic_info: Dict[str, str] = {}
                dt_dd_pairs = re.findall(
                    r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>",
                    html,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                for dt_raw, dd_raw in dt_dd_pairs:
                    key = AIService._clean_html_text(dt_raw).rstrip("：:")
                    value = AIService._clean_html_text(dd_raw)
                    if key and value and key not in basic_info:
                        basic_info[key] = value

                if not basic_info:
                    th_td_pairs = re.findall(
                        r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>",
                        html,
                        flags=re.IGNORECASE | re.DOTALL,
                    )
                    for th_raw, td_raw in th_td_pairs:
                        key = AIService._clean_html_text(th_raw).rstrip("：:")
                        value = AIService._clean_html_text(td_raw)
                        if key and value and key not in basic_info:
                            basic_info[key] = value

                if not summary and not basic_info:
                    continue

                title = ""
                title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = AIService._clean_html_text(title_match.group(1))

                return {
                    "source": "baidu_baike",
                    "url": str(resp.url),
                    "title": title,
                    "summary": summary,
                    "basic_info": basic_info,
                }
            except Exception:
                continue
        return {}

    @staticmethod
    def _map_baike_profile_to_fields(profile: Dict[str, Any]) -> Dict[str, Any]:
        if not profile:
            return {"suggestions": {}, "evidence": {}}

        info = profile.get("basic_info") or {}
        summary = profile.get("summary") or ""
        suggestions: Dict[str, Any] = {}
        evidence: Dict[str, Any] = {}

        website = AIService._extract_first_by_keys(info, ["官方网站", "官网", "网站"])
        if website:
            suggestions["website"] = website

        address = AIService._extract_first_by_keys(info, ["总部地点", "总部地址", "公司地址", "注册地址", "办公地址"])
        if address:
            suggestions["address"] = address

        industry = AIService._extract_first_by_keys(info, ["所属行业", "行业"])
        if industry:
            suggestions["industry"] = industry

        legal_person = AIService._extract_first_by_keys(info, ["法定代表人", "法人代表", "法人"])
        if legal_person:
            suggestions["legal_person"] = legal_person

        company_size = AIService._extract_first_by_keys(info, ["员工人数", "员工规模", "人员规模"])
        if company_size:
            suggestions["company_size"] = company_size

        establish = AIService._extract_first_by_keys(info, ["成立时间", "成立日期", "创立时间", "创办时间"])
        parsed_establish = AIService._parse_establish_date(establish)
        if parsed_establish:
            suggestions["establish_date"] = parsed_establish

        capital = AIService._extract_first_by_keys(info, ["注册资本", "注册资金"])
        parsed_capital = AIService._parse_registered_capital(capital)
        if parsed_capital is not None:
            suggestions["registered_capital"] = parsed_capital

        product_info = AIService._extract_first_by_keys(info, ["经营范围", "主营业务", "业务范围", "主要业务", "产品服务"])
        if product_info:
            suggestions["product_info"] = product_info

        company_info_parts = []
        if summary:
            company_info_parts.append(summary)
        for key in ["企业类型", "公司类型", "统一社会信用代码", "曾用名"]:
            value = info.get(key)
            if value:
                company_info_parts.append(f"{key}：{value}")
        if company_info_parts:
            suggestions["company_info"] = "；".join(company_info_parts)[:1000]

        if profile.get("url"):
            suggestions["source"] = "百度百科"
            remark_items = []
            for key in ["企业资质", "发展历程", "历史沿革"]:
                if info.get(key):
                    remark_items.append(f"{key}：{info[key]}")
            remark_text = "；".join(remark_items)
            if remark_text:
                suggestions["remarks"] = f"来源：百度百科 {profile['url']}；{remark_text}"[:1000]
            else:
                suggestions["remarks"] = f"来源：百度百科 {profile['url']}"

        evidence["url"] = profile.get("url")
        evidence["summary"] = summary
        evidence["basic_info"] = info
        return {
            "suggestions": suggestions,
            "evidence": evidence,
        }

    @staticmethod
    async def _call_glm_for_customer_enrich(
        *,
        config: AIConfig,
        customer: CustomerInfo,
        target_fields: List[str],
        external_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        api_key = (config.api_key or settings.ZHIPUAI_API_KEY or "").strip()
        if not api_key:
            raise ValueError("未配置GLM API Key")

        endpoint = (config.api_base or "https://open.bigmodel.cn/api/paas/v4/chat/completions").strip()
        model_name = (config.model_name or "glm-4-flash").strip()

        existing_context = {
            "customer_name_cn": customer.customer_name,
            "customer_name_en": customer.customer_name_en,
            "region": customer.region,
            "industry": customer.industry,
            "website": customer.website,
            "address": customer.address,
            "legal_person": customer.legal_person,
            "registered_capital": str(customer.registered_capital) if customer.registered_capital is not None else "",
            "establish_date": str(customer.establish_date) if customer.establish_date else "",
            "company_size": customer.company_size,
            "source": customer.source,
            "company_info": customer.company_info,
            "product_info": customer.product_info,
            "remarks": customer.remarks,
            "external_profile": external_profile or {},
        }
        field_desc = {
            "website": "公司官网URL，必须是https://开头，无法确认时留空字符串",
            "address": "公司地址（城市+详细地址）",
            "product_info": "公司主营产品/方案简介（50-200字）",
            "company_info": "公司简介（50-200字）",
            "industry": "所属行业（例如：汽车制造/工业自动化/新能源）",
            "legal_person": "法定代表人/法人姓名",
            "registered_capital": "注册资本，输出纯数字或可解析金额，例如 5000000",
            "establish_date": "成立日期，格式 YYYY-MM-DD",
            "company_size": "公司规模/员工人数描述",
            "source": "客户来源（例如：展会获客/存量客户/渠道推荐）",
            "remarks": "补全备注",
        }

        target_desc = {k: field_desc.get(k, k) for k in target_fields}
        system_prompt = (
            "你是企业CRM数据补全助手。"
            "根据客户名称与上下文，给出尽可能准确的企业资料补全建议。"
            "只输出JSON对象，不要输出任何解释。"
            "如果无法确定某字段，请返回空字符串。"
        )
        user_prompt = (
            f"目标字段: {json.dumps(target_desc, ensure_ascii=False)}\n"
            f"客户上下文: {json.dumps(existing_context, ensure_ascii=False)}\n"
            "输出格式示例:\n"
            "{\n"
            '  "website": "https://example.com",\n'
            '  "address": "上海市浦东新区xx路xx号",\n'
            '  "legal_person": "张三",\n'
            '  "registered_capital": "5000000",\n'
            '  "establish_date": "2012-06-15",\n'
            '  "product_info": "主营...",\n'
            '  "company_info": "公司成立于...",\n'
            '  "industry": "工业自动化",\n'
            '  "source": "存量客户"\n'
            "}"
        )

        payload = {
            "model": model_name,
            "temperature": float(config.temperature) if config.temperature is not None else 0.2,
            "max_tokens": config.max_tokens or 1200,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        timeout_seconds = config.timeout_seconds or 45
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            response_json = response.json()

        content = (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        parsed = AIService._extract_json_block(content)
        if not parsed:
            raise ValueError("GLM返回结果无法解析为JSON")

        normalized: Dict[str, Any] = {}
        for field in target_fields:
            value = parsed.get(field)
            if isinstance(value, str):
                normalized[field] = value.strip()
            elif value is None:
                normalized[field] = ""
            else:
                normalized[field] = str(value).strip()
        return normalized

    @staticmethod
    async def enrich_customer_profile(
        db: AsyncSession,
        *,
        customer_id: int,
        target_fields: Optional[List[str]],
        overwrite: bool,
        user_id: int,
    ) -> Dict[str, Any]:
        preview = await AIService.preview_customer_enrich_profile(
            db,
            customer_id=customer_id,
            target_fields=target_fields,
            overwrite=overwrite,
            user_id=user_id,
        )
        proposed_updates = preview.get("proposed_updates") or {}
        if not proposed_updates:
            return {
                "customer_id": preview["customer_id"],
                "customer_name": preview["customer_name"],
                "message": "没有可写入的补全建议",
                "updated_fields": {},
                "applied_count": 0,
                "request_id": preview.get("request_id"),
            }
        return await AIService.apply_customer_enrich_profile(
            db,
            customer_id=customer_id,
            updates=proposed_updates,
            request_id=preview.get("request_id"),
            user_id=user_id,
        )

    @staticmethod
    async def preview_customer_enrich_profile(
        db: AsyncSession,
        *,
        customer_id: int,
        target_fields: Optional[List[str]],
        overwrite: bool,
        user_id: int,
    ) -> Dict[str, Any]:
        """生成客户属性补全建议（不写入业务数据）"""
        customer = (await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_id, CustomerInfo.deleted_at.is_(None))
        )).scalar_one_or_none()
        if not customer:
            raise ValueError("客户不存在")

        requested_fields = target_fields or list(AIService.ENRICH_SUPPORTED_FIELDS)
        requested_fields = [f for f in requested_fields if f in AIService.ENRICH_SUPPORTED_FIELDS]
        if not requested_fields:
            raise ValueError("未指定可补全字段")

        missing_fields: List[str] = []
        for field in requested_fields:
            current_value = getattr(customer, field, None)
            if overwrite or current_value is None or str(current_value).strip() == "":
                missing_fields.append(field)

        suggestions: Dict[str, Any] = {}
        baike_profile: Dict[str, Any] = {}
        baike_suggestions: Dict[str, Any] = {}
        llm_suggestions: Dict[str, Any] = {}
        input_payload = {
            "customer_id": customer.id,
            "customer_name": customer.customer_name,
            "target_fields": requested_fields,
            "missing_fields": missing_fields,
            "overwrite": overwrite,
        }
        if missing_fields:
            config = await AIService._ensure_default_config(db)
            if not config.is_enabled:
                raise ValueError("AI配置已禁用，请先启用后重试")

            try:
                # 1) 优先抓取百度百科结构化信息
                baike_profile = await AIService._fetch_baike_profile(customer.customer_name)
                baike_result = AIService._map_baike_profile_to_fields(baike_profile)
                baike_suggestions = baike_result.get("suggestions") or {}
                for field in missing_fields:
                    if field in baike_suggestions and baike_suggestions[field]:
                        suggestions[field] = baike_suggestions[field]

                # 2) 剩余字段再走GLM补齐
                need_llm_fields = [field for field in missing_fields if not suggestions.get(field)]
                provider = (config.provider or "").lower()
                if need_llm_fields and provider in {"glm", "zhipuai"}:
                    llm_suggestions = await AIService._call_glm_for_customer_enrich(
                        config=config,
                        customer=customer,
                        target_fields=need_llm_fields,
                        external_profile=baike_profile,
                    )
                    for field, value in llm_suggestions.items():
                        if field in missing_fields and value:
                            suggestions[field] = value
                elif need_llm_fields:
                    raise ValueError("当前AI提供商不是GLM，请在AI配置中设置 provider=glm")
            except Exception as exc:
                await AIService._log_request(
                    db,
                    scene="customer_enrich_preview",
                    input_payload=input_payload,
                    output_payload=None,
                    status="failed",
                    error_message=str(exc),
                    created_by=user_id,
                )
                raise ValueError(f"客户补全失败: {exc}") from exc

        field_status: Dict[str, Dict[str, Any]] = {}
        proposed_updates: Dict[str, str] = {}
        skipped_fields: List[str] = []
        for field in requested_fields:
            current_value = getattr(customer, field, None)
            current_text = str(current_value).strip() if current_value is not None else ""
            current_display = current_text if current_text else ""
            candidate_raw = suggestions.get(field, "")
            candidate_text = str(candidate_raw).strip() if candidate_raw is not None else ""
            is_empty = current_text == ""
            candidate_eligible = overwrite or is_empty
            will_update = bool(candidate_text) and candidate_eligible

            if will_update:
                proposed_updates[field] = candidate_text
            else:
                skipped_fields.append(field)

            if not candidate_eligible and not overwrite:
                reason = "已有值且未开启覆盖"
            elif not candidate_text:
                reason = "模型未返回有效建议"
            else:
                reason = "可写入"

            field_status[field] = {
                "field": field,
                "label": AIService.ENRICH_FIELD_LABELS.get(field, field),
                "current_value": current_display,
                "is_empty": is_empty,
                "candidate_value": candidate_text,
                "candidate_eligible": candidate_eligible,
                "will_update": will_update,
                "reason": reason,
            }

        output = {
            "customer_id": customer.id,
            "customer_name": customer.customer_name,
            "target_fields": requested_fields,
            "missing_fields": missing_fields,
            "data_sources": {
                "baidu_baike": {
                    "matched": bool(baike_profile),
                    "url": baike_profile.get("url"),
                    "title": baike_profile.get("title"),
                },
                "glm": {
                    "provider": "glm",
                    "used": bool(llm_suggestions),
                },
            },
            "external_profile": baike_profile,
            "field_status": field_status,
            "proposed_updates": proposed_updates,
            "skipped_fields": skipped_fields,
            "preview_count": len(proposed_updates),
        }
        request_log = await AIService._log_request(
            db,
            scene="customer_enrich_preview",
            input_payload=input_payload,
            output_payload=output,
            status="success",
            created_by=user_id,
        )
        output["request_id"] = request_log.request_id
        await db.flush()
        return output

    @staticmethod
    async def apply_customer_enrich_profile(
        db: AsyncSession,
        *,
        customer_id: int,
        updates: Dict[str, Any],
        request_id: Optional[str],
        user_id: int,
    ) -> Dict[str, Any]:
        """确认写入客户属性补全结果"""
        customer = (await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_id, CustomerInfo.deleted_at.is_(None))
        )).scalar_one_or_none()
        if not customer:
            raise ValueError("客户不存在")

        preview_output: Dict[str, Any] = {}
        if request_id:
            request_log = (await db.execute(
                select(AIRequestLog).where(
                    AIRequestLog.request_id == request_id,
                    AIRequestLog.scene == "customer_enrich_preview",
                )
            )).scalar_one_or_none()
            if not request_log:
                raise ValueError("补全预览请求不存在，请重新生成建议")
            payload = request_log.input_payload or {}
            if int(payload.get("customer_id") or 0) != customer_id:
                raise ValueError("补全请求与当前客户不匹配，请重新生成建议")
            preview_output = request_log.output_payload or {}

        normalized_updates: Dict[str, Any] = {}
        for field, value in (updates or {}).items():
            if field not in AIService.ENRICH_SUPPORTED_FIELDS:
                continue
            if value is None:
                continue
            normalized_value: Any = value
            if isinstance(value, str):
                normalized_value = value.strip()
            if field == "registered_capital":
                if isinstance(normalized_value, Decimal):
                    pass
                else:
                    parsed_capital = AIService._parse_registered_capital(str(normalized_value))
                    if parsed_capital is None:
                        continue
                    normalized_value = parsed_capital
            elif field == "establish_date":
                if isinstance(normalized_value, date):
                    pass
                else:
                    parsed_date = AIService._parse_establish_date(str(normalized_value))
                    if parsed_date is None:
                        continue
                    normalized_value = parsed_date
            elif isinstance(normalized_value, str) and not normalized_value:
                continue

            normalized_updates[field] = normalized_value

        if not normalized_updates:
            raise ValueError("没有可确认写入的字段")

        change_details: List[Dict[str, Any]] = []
        updated_fields: Dict[str, Any] = {}
        for field, new_value in normalized_updates.items():
            old_raw = getattr(customer, field, None)
            old_value = str(old_raw).strip() if old_raw is not None else ""
            new_value_text = str(new_value).strip() if new_value is not None else ""
            if old_value == new_value_text:
                continue
            setattr(customer, field, new_value)
            updated_fields[field] = new_value_text
            change_details.append({
                "field": field,
                "label": AIService.ENRICH_FIELD_LABELS.get(field, field),
                "old_value": old_value,
                "new_value": new_value_text,
            })

        if not updated_fields:
            return {
                "customer_id": customer.id,
                "customer_name": customer.customer_name,
                "message": "没有发生字段变更",
                "updated_fields": {},
                "applied_count": 0,
                "request_id": request_id,
            }

        customer.updated_by = user_id
        customer.updated_at = datetime.utcnow()
        customer.data_completed_at = datetime.utcnow()
        company_summary = customer.company_info
        product_summary = customer.product_info
        if company_summary or product_summary:
            customer.ai_summary = "；".join(
                [part for part in [company_summary, product_summary] if part]
            )

        # 回填外部来源资料到 ai_insights，便于后续查看（不覆盖已有洞察）
        external_profile = preview_output.get("external_profile") if isinstance(preview_output, dict) else None
        if external_profile:
            insights_obj: Dict[str, Any] = {}
            if customer.ai_insights:
                try:
                    loaded = json.loads(customer.ai_insights)
                    if isinstance(loaded, dict):
                        insights_obj = loaded
                except (TypeError, json.JSONDecodeError):
                    insights_obj = {}
            insights_obj["baidu_baike_profile"] = external_profile
            customer.ai_insights = json.dumps(insights_obj, ensure_ascii=False)

        output = {
            "customer_id": customer.id,
            "customer_name": customer.customer_name,
            "request_id": request_id,
            "updated_fields": updated_fields,
            "change_details": change_details,
            "applied_count": len(updated_fields),
        }
        request_log = await AIService._log_request(
            db,
            scene="customer_enrich_apply",
            input_payload={
                "customer_id": customer_id,
                "request_id": request_id,
                "updates": normalized_updates,
            },
            output_payload=output,
            status="success",
            created_by=user_id,
        )
        db.add(AIAnalysisResult(
            scene="customer_enrich_apply",
            related_type="customer",
            related_id=customer.id,
            level="info",
            summary=f"客户属性确认写入完成，更新字段数：{len(updated_fields)}",
            result_data=output,
            request_log_id=request_log.id,
        ))
        await db.flush()
        return output

    @staticmethod
    async def _log_request(
        db: AsyncSession,
        *,
        scene: str,
        input_payload: Dict[str, Any],
        output_payload: Optional[Dict[str, Any]],
        status: str = "success",
        error_message: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> AIRequestLog:
        request_log = AIRequestLog(
            scene=scene,
            request_id=uuid.uuid4().hex,
            input_payload=input_payload,
            output_payload=output_payload,
            prompt="rule-engine",
            model_name="rule-engine-v1",
            status=status,
            latency_ms=0,
            tokens=0,
            error_message=error_message,
            created_by=created_by,
        )
        db.add(request_log)
        await db.flush()
        return request_log

    @staticmethod
    async def smart_complete(
        db: AsyncSession,
        *,
        entity_type: str,
        entity_id: int,
        missing_fields: List[str],
        context: Dict[str, Any],
        user_id: int,
    ) -> Dict[str, Any]:
        """信息智能补全（返回建议，不直接覆盖业务字段）"""
        suggestions: Dict[str, Any] = {}
        entity_snapshot: Dict[str, Any] = {"entity_type": entity_type, "entity_id": entity_id}

        if entity_type == "customer":
            customer = (await db.execute(
                select(CustomerInfo).where(CustomerInfo.id == entity_id, CustomerInfo.deleted_at.is_(None))
            )).scalar_one_or_none()
            if not customer:
                raise ValueError("客户不存在")
            entity_snapshot["name"] = customer.customer_name

            for field in missing_fields:
                if field == "industry":
                    suggestions[field] = context.get("industry") or "通用制造"
                elif field == "level":
                    suggestions[field] = context.get("level") or "C"
                elif field == "source":
                    suggestions[field] = context.get("source") or "线索导入"
                elif field == "remarks":
                    suggestions[field] = f"建议补充：{customer.customer_name} 的采购周期、决策链、预算信息。"

        elif entity_type == "contact":
            contact = (await db.execute(
                select(ContactInfo).where(ContactInfo.id == entity_id, ContactInfo.deleted_at.is_(None))
            )).scalar_one_or_none()
            if not contact:
                raise ValueError("联系人不存在")
            entity_snapshot["name"] = contact.name
            for field in missing_fields:
                if field == "title":
                    suggestions[field] = context.get("title") or "待确认"
                elif field == "department":
                    suggestions[field] = context.get("department") or "技术部"
                elif field == "influence_level":
                    suggestions[field] = context.get("influence_level") or 3

        elif entity_type == "opportunity":
            opportunity = (await db.execute(
                select(OpportunityInfo).where(OpportunityInfo.id == entity_id, OpportunityInfo.deleted_at.is_(None))
            )).scalar_one_or_none()
            if not opportunity:
                raise ValueError("商机不存在")
            entity_snapshot["name"] = opportunity.opportunity_name
            for field in missing_fields:
                if field == "expected_close_date":
                    suggestions[field] = str(date.today() + timedelta(days=30))
                elif field == "win_probability":
                    suggestions[field] = opportunity.win_probability or 50
                elif field == "description":
                    suggestions[field] = f"建议补充：{opportunity.opportunity_name} 的痛点、预算、决策流程。"
        else:
            raise ValueError(f"不支持的实体类型: {entity_type}")

        output = {
            "entity": entity_snapshot,
            "suggestions": suggestions,
            "completed_fields": list(suggestions.keys()),
        }
        request_log = await AIService._log_request(
            db,
            scene="smart_complete",
            input_payload={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "missing_fields": missing_fields,
                "context": context,
            },
            output_payload=output,
            created_by=user_id,
        )

        result = AIAnalysisResult(
            scene="smart_complete",
            related_type=entity_type,
            related_id=entity_id,
            level="info",
            summary=f"已生成{len(suggestions)}项补全建议",
            result_data=output,
            request_log_id=request_log.id,
        )
        db.add(result)
        await db.flush()
        return output

    @staticmethod
    async def analyze_opportunity_risk(
        db: AsyncSession,
        *,
        opportunity_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """单商机风险分析"""
        opportunity = (await db.execute(
            select(OpportunityInfo).where(OpportunityInfo.id == opportunity_id, OpportunityInfo.deleted_at.is_(None))
        )).scalar_one_or_none()
        if not opportunity:
            raise ValueError("商机不存在")

        factors: List[str] = []
        score = 0

        if (opportunity.days_in_stage or 0) >= 30:
            factors.append("阶段停滞超过30天")
            score += 35
        if (opportunity.win_probability or 0) < 40:
            factors.append("成交概率低于40%")
            score += 25
        if not opportunity.last_activity_at or opportunity.last_activity_at < datetime.utcnow() - timedelta(days=14):
            factors.append("近14天无有效活动")
            score += 20
        if not opportunity.expected_close_date:
            factors.append("缺少预计成交日期")
            score += 10
        if not opportunity.owner_id:
            factors.append("缺少明确负责人")
            score += 10

        if score >= 70:
            level = "high"
        elif score >= 40:
            level = "medium"
        else:
            level = "low"

        suggestions = []
        if level in {"high", "medium"}:
            suggestions.extend([
                "补充关键决策人信息并安排高层对齐会议",
                "明确下一阶段门槛动作与完成时间",
            ])
        if "近14天无有效活动" in factors:
            suggestions.append("3个工作日内安排一次客户跟进")

        output = {
            "opportunity_id": opportunity.id,
            "opportunity_name": opportunity.opportunity_name,
            "risk_level": level,
            "risk_score": score,
            "factors": factors,
            "suggestions": suggestions,
        }
        request_log = await AIService._log_request(
            db,
            scene="opportunity_risk",
            input_payload={"opportunity_id": opportunity_id},
            output_payload=output,
            created_by=user_id,
        )

        analysis_result = AIAnalysisResult(
            scene="opportunity_risk",
            related_type="opportunity",
            related_id=opportunity.id,
            score=score,
            level=level,
            summary="；".join(factors) if factors else "风险较低",
            result_data=output,
            request_log_id=request_log.id,
        )
        db.add(analysis_result)

        opportunity.risk_level = level
        opportunity.risk_factors = factors
        opportunity.ai_suggestions = "；".join(suggestions)
        opportunity.last_ai_analysis = datetime.utcnow()

        if level in {"high", "medium"}:
            alert = AIRiskAlert(
                alert_type="opportunity_risk",
                alert_level=level,
                related_type="opportunity",
                related_id=opportunity.id,
                title=f"商机风险预警：{opportunity.opportunity_name}",
                content="；".join(factors) if factors else "检测到潜在风险",
                suggestion="；".join(suggestions) if suggestions else None,
                status="new",
            )
            db.add(alert)

        await db.flush()
        return output

    @staticmethod
    async def batch_risk_scan(
        db: AsyncSession,
        *,
        opportunity_ids: Optional[List[int]],
        threshold_days: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """批量风险扫描"""
        stmt = select(OpportunityInfo).where(
            OpportunityInfo.deleted_at.is_(None),
            OpportunityInfo.status == "open",
        )
        if opportunity_ids:
            stmt = stmt.where(OpportunityInfo.id.in_(opportunity_ids))
        opportunities = (await db.execute(stmt)).scalars().all()

        scanned = 0
        high_risk = 0
        medium_risk = 0
        details: List[Dict[str, Any]] = []

        for opp in opportunities:
            scanned += 1
            result = await AIService.analyze_opportunity_risk(
                db,
                opportunity_id=opp.id,
                user_id=user_id,
            )
            details.append(result)
            if result["risk_level"] == "high":
                high_risk += 1
            elif result["risk_level"] == "medium":
                medium_risk += 1

            if (opp.days_in_stage or 0) >= threshold_days and result["risk_level"] == "low":
                opp.risk_level = "medium"
                opp.risk_factors = (opp.risk_factors or []) + [f"阶段停留超过阈值{threshold_days}天"]
                medium_risk += 1

        output = {
            "scanned": scanned,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "details": details,
        }
        await AIService._log_request(
            db,
            scene="risk_batch_scan",
            input_payload={"opportunity_ids": opportunity_ids, "threshold_days": threshold_days},
            output_payload={k: v for k, v in output.items() if k != "details"},
            created_by=user_id,
        )
        return output

    @staticmethod
    async def summarize_visit(
        db: AsyncSession,
        *,
        visit_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """拜访纪要AI总结"""
        visit = (await db.execute(
            select(VisitRecord).where(VisitRecord.id == visit_id)
        )).scalar_one_or_none()
        if not visit:
            raise ValueError("拜访记录不存在")

        summary_parts = [
            f"拜访主题：{visit.purpose or '未填写'}",
            f"客户反馈：{visit.customer_feedback or '未填写'}",
            f"下一步：{visit.next_plan or '建议补充明确下一步计划'}",
        ]
        action_items = []
        if visit.next_plan:
            action_items.append({"item": visit.next_plan, "owner": "销售负责人", "due_in_days": 3})
        else:
            action_items.append({"item": "补充拜访后的下一步行动", "owner": "销售负责人", "due_in_days": 1})

        summary = "；".join(summary_parts)
        visit.ai_summary = summary
        visit.ai_action_items = str(action_items)

        output = {
            "visit_id": visit_id,
            "summary": summary,
            "action_items": action_items,
        }
        request_log = await AIService._log_request(
            db,
            scene="visit_summary",
            input_payload={"visit_id": visit_id},
            output_payload=output,
            created_by=user_id,
        )
        db.add(AIAnalysisResult(
            scene="visit_summary",
            related_type="visit",
            related_id=visit_id,
            level="info",
            summary=summary,
            result_data=output,
            request_log_id=request_log.id,
        ))
        await db.flush()
        return output

    @staticmethod
    async def analyze_funnel(
        db: AsyncSession,
        *,
        owner_id: Optional[int],
        user_id: int,
    ) -> Dict[str, Any]:
        """销售漏斗智能分析"""
        stage_rows = (await db.execute(
            select(
                OpportunityInfo.stage_name,
                func.count(OpportunityInfo.id),
                func.coalesce(func.sum(OpportunityInfo.estimated_amount), 0),
                func.avg(func.coalesce(OpportunityInfo.days_in_stage, 0)),
            )
            .where(
                OpportunityInfo.deleted_at.is_(None),
                OpportunityInfo.status == "open",
                *( [OpportunityInfo.owner_id == owner_id] if owner_id else [] ),
            )
            .group_by(OpportunityInfo.stage_name)
            .order_by(desc(func.count(OpportunityInfo.id)))
        )).all()

        stage_summary = [
            {
                "stage_name": row[0] or "未知阶段",
                "count": row[1],
                "amount": float(row[2] or 0),
                "avg_days_in_stage": round(float(row[3] or 0), 2),
            }
            for row in stage_rows
        ]

        bottleneck = None
        if stage_summary:
            bottleneck = max(stage_summary, key=lambda x: x["avg_days_in_stage"])

        insights = []
        if bottleneck and bottleneck["avg_days_in_stage"] >= 20:
            insights.append(f"{bottleneck['stage_name']}阶段平均停留{bottleneck['avg_days_in_stage']}天，存在明显堵点")
        if stage_summary and stage_summary[0]["count"] > 0:
            insights.append("建议优先处理高金额且高风险商机，提升短期转化效率")

        output = {
            "stage_summary": stage_summary,
            "bottleneck_stage": bottleneck,
            "insights": insights,
        }
        await AIService._log_request(
            db,
            scene="funnel_analysis",
            input_payload={"owner_id": owner_id},
            output_payload=output,
            created_by=user_id,
        )
        return output

    @staticmethod
    async def natural_language_query(
        db: AsyncSession,
        *,
        query: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """自然语言查询（规则解析）"""
        normalized = query.lower()
        intent = "unknown"
        sql_text = ""
        answer = "暂时无法识别该问题，请尝试询问：高风险商机、本月新增客户、待办任务。"
        result_count = 0

        if "高风险" in query and "商机" in query:
            intent = "high_risk_opportunity"
            sql_text = "SELECT opportunity_name FROM crm_opportunity_info WHERE risk_level='high' AND status='open'"
            rows = (await db.execute(
                select(OpportunityInfo.opportunity_name)
                .where(
                    OpportunityInfo.deleted_at.is_(None),
                    OpportunityInfo.status == "open",
                    OpportunityInfo.risk_level == "high",
                )
                .limit(10)
            )).all()
            names = [row[0] for row in rows]
            result_count = len(names)
            answer = f"当前高风险商机共{result_count}个：{', '.join(names) if names else '暂无'}"

        elif "本月" in query and "新增客户" in query:
            intent = "monthly_new_customer"
            first_day = date.today().replace(day=1)
            sql_text = "SELECT count(*) FROM crm_customer_info WHERE created_at >= first_day"
            result_count = (await db.execute(
                select(func.count(CustomerInfo.id))
                .where(
                    CustomerInfo.deleted_at.is_(None),
                    func.date(CustomerInfo.created_at) >= first_day,
                )
            )).scalar() or 0
            answer = f"本月新增客户 {result_count} 个。"

        elif "待办" in query or "任务" in query:
            intent = "pending_tasks"
            sql_text = "SELECT count(*) FROM crm_task_info WHERE status in ('pending','in_progress')"
            result_count = (await db.execute(
                select(func.count(TaskInfo.id))
                .where(TaskInfo.status.in_(["pending", "in_progress"]))
            )).scalar() or 0
            answer = f"当前待办任务 {result_count} 个。"

        history = AISearchHistory(
            query_text=query,
            intent=intent,
            sql_text=sql_text,
            answer=answer,
            result_count=result_count,
            created_by=user_id,
        )
        db.add(history)

        output = {
            "intent": intent,
            "answer": answer,
            "result_count": result_count,
            "sql": sql_text,
        }
        await AIService._log_request(
            db,
            scene="nl_query",
            input_payload={"query": query},
            output_payload=output,
            created_by=user_id,
        )
        await db.flush()
        return output

    @staticmethod
    async def list_alerts(
        db: AsyncSession,
        *,
        status: Optional[str] = None,
        level: Optional[str] = None,
        related_type: Optional[str] = None,
    ) -> List[AIRiskAlert]:
        """预警列表"""
        stmt = select(AIRiskAlert).order_by(AIRiskAlert.created_at.desc())
        conditions = []
        if status:
            conditions.append(AIRiskAlert.status == status)
        if level:
            conditions.append(AIRiskAlert.alert_level == level)
        if related_type:
            conditions.append(AIRiskAlert.related_type == related_type)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        *,
        alert_id: int,
        user_id: int,
    ) -> Optional[AIRiskAlert]:
        """确认预警"""
        alert = (await db.execute(select(AIRiskAlert).where(AIRiskAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            return None
        alert.status = "acknowledged"
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        return alert

    @staticmethod
    async def resolve_alert(
        db: AsyncSession,
        *,
        alert_id: int,
        user_id: int,
    ) -> Optional[AIRiskAlert]:
        """解决预警"""
        alert = (await db.execute(select(AIRiskAlert).where(AIRiskAlert.id == alert_id))).scalar_one_or_none()
        if not alert:
            return None
        alert.status = "resolved"
        alert.resolved_by = user_id
        alert.resolved_at = datetime.utcnow()
        return alert

    @staticmethod
    async def get_config(db: AsyncSession) -> AIConfig:
        """获取AI配置"""
        return await AIService._ensure_default_config(db)

    @staticmethod
    async def update_config(db: AsyncSession, payload: Dict[str, Any]) -> AIConfig:
        """更新AI配置"""
        config = await AIService._ensure_default_config(db)
        for key, value in payload.items():
            if key == "api_key" and isinstance(value, str):
                value = value.strip()
            setattr(config, key, value)
        return config

    @staticmethod
    async def list_prompt_templates(db: AsyncSession, scene: Optional[str] = None) -> List[AIPromptTemplate]:
        """获取提示词模板列表"""
        stmt = select(AIPromptTemplate).order_by(AIPromptTemplate.created_at.desc())
        if scene:
            stmt = stmt.where(AIPromptTemplate.scene == scene)
        return list((await db.execute(stmt)).scalars().all())

    @staticmethod
    async def create_prompt_template(db: AsyncSession, payload: Dict[str, Any]) -> AIPromptTemplate:
        """创建提示词模板"""
        template = AIPromptTemplate(**payload)
        db.add(template)
        await db.flush()
        return template

    @staticmethod
    async def update_prompt_template(
        db: AsyncSession,
        template_id: int,
        payload: Dict[str, Any],
    ) -> Optional[AIPromptTemplate]:
        """更新提示词模板"""
        template = (await db.execute(
            select(AIPromptTemplate).where(AIPromptTemplate.id == template_id)
        )).scalar_one_or_none()
        if not template:
            return None
        for key, value in payload.items():
            setattr(template, key, value)
        return template
