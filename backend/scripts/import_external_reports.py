"""导入外部CRM Excel报表到本系统数据库。

用法:
    cd backend
    venv/bin/python scripts/import_external_reports.py

可选参数:
    --workspace-root /Users/xxx/Documents/Tools/CRM
    --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# 添加项目路径
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config.database import async_session_maker, init_db  # noqa: E402
from app.core.security import jwt_manager  # noqa: E402
from app.core.utils.helpers import generate_customer_no  # noqa: E402
from app.models.activity import FollowRecord, Schedule, TaskInfo, VisitRecord  # noqa: E402
from app.models.customer import CustomerInfo  # noqa: E402
from app.models.opportunity import OpportunityInfo, StageDef  # noqa: E402
from app.models.sys import Role, User, UserRole  # noqa: E402
from app.services.opportunity.stage_service import StageService  # noqa: E402


CUSTOMER_FILES = [
    "AllAccounts_2026-02-26.xlsx",
    "Top客户_2026-02-26.xlsx",
    "客户服务情况_2026-02-26.xlsx",
]

OPPORTUNITY_FILES = [
    "AllPipeline_2026-02-26.xlsx",
    "Top机会_2026-02-26.xlsx",
    "Renew+Pipeline_2026-02-26.xlsx",
    "Sleeper2026_2026-02-26.xlsx",
    "客户启航_2026-02-26.xlsx",
    "商机明细_2026-02-26.xlsx",
]

ACTIVITY_FILE = "活动记录_2026-02-26.xlsx"


SALES_COLUMNS = {"3#负责人", "客户负责人", "机会负责人", "负责人", "Eplan销售", "发布人"}
TECH_COLUMNS = {"5#技术负责人", "EPLAN技术人员"}


@dataclass
class ImportStats:
    users_created: int = 0
    users_updated: int = 0
    customers_created: int = 0
    customers_updated: int = 0
    opportunities_created: int = 0
    opportunities_updated: int = 0
    visits_created: int = 0
    follows_created: int = 0
    tasks_created: int = 0
    schedules_created: int = 0
    rows_skipped: int = 0


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() == "nan" or text == "--"


def clean_text(value: Any) -> Optional[str]:
    if is_empty(value):
        return None
    text = str(value).strip()
    return text if text else None


def normalize_name(value: Any) -> Optional[str]:
    text = clean_text(value)
    if not text:
        return None
    text = text.replace("（", "(").replace("）", ")")
    text = re.sub(r"\s+", "", text)
    return text.lower()


def parse_int(value: Any) -> Optional[int]:
    if is_empty(value):
        return None
    try:
        return int(float(str(value).replace(",", "").strip()))
    except Exception:
        return None


def parse_amount(value: Any) -> Optional[float]:
    if is_empty(value):
        return None
    raw = str(value).strip().replace(",", "")
    raw = raw.replace("¥", "").replace("￥", "")
    try:
        return float(raw)
    except Exception:
        return None


def parse_date(value: Any) -> Optional[date]:
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    ts = pd.to_datetime(text, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.date()


def parse_datetime(value: Any) -> Optional[datetime]:
    if is_empty(value):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time(9, 0, 0))
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.to_pydatetime()


def map_customer_level(level_3: Optional[str], level: Optional[str]) -> str:
    if level:
        upper = level.upper()
        if upper in {"A", "B", "C", "D"}:
            return upper
    if level_3:
        mapping = {"1": "A", "2": "B", "3": "C", "4": "D"}
        return mapping.get(level_3.strip(), "C")
    return "C"


STAGE_ALIAS_MAP = {
    "pending": "lead",
    "lead": "lead",
    "aware": "lead",
    "attract": "lead",
    "寻找客户": "lead",
    "吸引客户": "lead",
    "线索": "lead",
    "prospect": "prospect",
    "潜在商机": "prospect",
    "qualify": "qualify",
    "qualified": "qualify",
    "客户意向": "qualify",
    "need": "need",
    "需求深入": "need",
    "upside": "upside",
    "项目立项": "upside",
    "endorse": "endorse",
    "方案确认": "endorse",
    "stretch": "stretch",
    "商务谈判": "stretch",
    "commit": "commit",
    "合同成交": "commit",
    "deliver": "deliver",
    "项目执行": "deliver",
    "closed won": "closed_won",
    "closed_won": "closed_won",
    "won": "closed_won",
    "项目完成": "closed_won",
    "closed lost": "closed_lost",
    "closed_lost": "closed_lost",
    "lost": "closed_lost",
    "商机关闭": "closed_lost",
}


def map_stage_code(raw_stage: Any) -> str:
    text = clean_text(raw_stage)
    if not text:
        return "lead"
    norm = text.lower().strip().replace("_", " ")
    if norm in STAGE_ALIAS_MAP:
        return STAGE_ALIAS_MAP[norm]

    for alias, target in STAGE_ALIAS_MAP.items():
        if alias in norm:
            return target
    return "lead"


def pick_value(row: pd.Series, columns: Iterable[str]) -> Optional[Any]:
    for col in columns:
        if col in row and not is_empty(row[col]):
            return row[col]
    return None


class ReportImporter:
    def __init__(self, db: AsyncSession, workspace_root: Path, dry_run: bool = False):
        self.db = db
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.stats = ImportStats()

        self.default_creator_id: int = 1
        self.default_user_role_id: Optional[int] = None

        self.user_by_norm_name: Dict[str, User] = {}
        self.username_set: set[str] = set()

        self.customer_by_norm_name: Dict[str, CustomerInfo] = {}
        self.stage_by_code: Dict[str, StageDef] = {}
        self.opportunity_by_key: Dict[Tuple[int, str], OpportunityInfo] = {}

        self.existing_visit_no: set[str] = set()
        self.existing_follow_no: set[str] = set()
        self.existing_task_no: set[str] = set()
        self.existing_schedule_keys: set[str] = set()

    async def bootstrap(self) -> None:
        await StageService.ensure_default_stages(self.db)

        stage_rows = (await self.db.execute(
            select(StageDef).where(StageDef.is_active.is_(True))
        )).scalars().all()
        self.stage_by_code = {stage.stage_code: stage for stage in stage_rows}

        admin = (await self.db.execute(
            select(User).where(User.username == "admin", User.deleted_at.is_(None))
        )).scalar_one_or_none()
        if admin:
            self.default_creator_id = int(admin.id)

        user_role = (await self.db.execute(
            select(Role).where(Role.code == "user")
        )).scalar_one_or_none()
        self.default_user_role_id = int(user_role.id) if user_role else None

        users = (await self.db.execute(
            select(User).where(User.deleted_at.is_(None))
        )).scalars().all()
        for user in users:
            if user.real_name:
                norm = normalize_name(user.real_name)
                if norm:
                    self.user_by_norm_name[norm] = user
            self.username_set.add(user.username)

        customers = (await self.db.execute(
            select(CustomerInfo).where(CustomerInfo.deleted_at.is_(None))
        )).scalars().all()
        for customer in customers:
            norm = normalize_name(customer.customer_name)
            if norm:
                self.customer_by_norm_name[norm] = customer

        opportunities = (await self.db.execute(
            select(OpportunityInfo).where(OpportunityInfo.deleted_at.is_(None))
        )).scalars().all()
        for opp in opportunities:
            if opp.customer_id and opp.opportunity_name:
                key = (int(opp.customer_id), normalize_name(opp.opportunity_name) or "")
                self.opportunity_by_key[key] = opp

        self.existing_visit_no = set((await self.db.execute(
            select(VisitRecord.visit_no)
        )).scalars().all())
        self.existing_follow_no = set((await self.db.execute(
            select(FollowRecord.follow_no)
        )).scalars().all())
        self.existing_task_no = set((await self.db.execute(
            select(TaskInfo.task_no)
        )).scalars().all())

        schedules = (await self.db.execute(
            select(
                Schedule.customer_id,
                Schedule.opportunity_id,
                Schedule.start_time,
                Schedule.schedule_type,
            )
        )).all()
        for customer_id, opportunity_id, start_time_value, schedule_type in schedules:
            if not start_time_value or not customer_id:
                continue
            key = (
                f"{customer_id}:{opportunity_id or 0}:"
                f"{start_time_value.date().isoformat()}:{schedule_type or ''}"
            )
            self.existing_schedule_keys.add(key)

    def _generate_username(self, name: str) -> str:
        ascii_base = re.sub(r"[^a-z0-9]+", "", name.lower())
        if len(ascii_base) < 3:
            ascii_base = "u" + hashlib.md5(name.encode("utf-8")).hexdigest()[:8]

        candidate = ascii_base[:24]
        seq = 1
        while candidate in self.username_set:
            suffix = f"{seq:02d}"
            candidate = f"{ascii_base[:24-len(suffix)]}{suffix}"
            seq += 1
        self.username_set.add(candidate)
        return candidate

    async def ensure_user(self, raw_name: Any, position_hint: Optional[str] = None) -> Optional[User]:
        name = clean_text(raw_name)
        norm = normalize_name(name)
        if not name or not norm:
            return None

        existing = self.user_by_norm_name.get(norm)
        if existing:
            if position_hint and not existing.position:
                existing.position = position_hint
                self.stats.users_updated += 1
            return existing

        username = self._generate_username(name)
        user = User(
            username=username,
            email=f"{username}@crm.local",
            password_hash=jwt_manager.hash_password("Welcome123!"),
            real_name=name,
            status=1,
            is_admin=False,
            position=position_hint,
        )
        self.db.add(user)
        await self.db.flush()

        if self.default_user_role_id:
            self.db.add(UserRole(
                user_id=user.id,
                role_id=self.default_user_role_id,
                created_at=datetime.utcnow(),
            ))

        self.user_by_norm_name[norm] = user
        self.stats.users_created += 1
        return user

    async def get_or_create_customer(self, customer_name: str) -> CustomerInfo:
        norm = normalize_name(customer_name)
        if not norm:
            raise ValueError("客户名称为空")
        existing = self.customer_by_norm_name.get(norm)
        if existing:
            return existing

        customer = CustomerInfo(
            customer_no=await generate_customer_no(self.db),
            customer_name=customer_name,
            customer_type="enterprise",
            level="C",
            status="active",
            created_by=self.default_creator_id,
            updated_by=self.default_creator_id,
        )
        self.db.add(customer)
        await self.db.flush()
        self.customer_by_norm_name[norm] = customer
        self.stats.customers_created += 1
        return customer

    async def import_users_from_reports(self) -> None:
        name_to_roles: Dict[str, set[str]] = defaultdict(set)
        report_files = CUSTOMER_FILES + OPPORTUNITY_FILES + [ACTIVITY_FILE]
        for filename in report_files:
            path = self.workspace_root / filename
            if not path.exists():
                continue
            df = pd.read_excel(path, sheet_name=0)
            for col in df.columns:
                if col in SALES_COLUMNS or col in TECH_COLUMNS:
                    for value in df[col].tolist():
                        name = clean_text(value)
                        if not name:
                            continue
                        role = "技术" if col in TECH_COLUMNS else "销售"
                        name_to_roles[name].add(role)

        for name, roles in name_to_roles.items():
            if roles == {"销售"}:
                position = "销售"
            elif roles == {"技术"}:
                position = "技术"
            else:
                position = "销售/技术"
            await self.ensure_user(name, position)

    async def import_customers(self) -> None:
        for filename in CUSTOMER_FILES:
            path = self.workspace_root / filename
            if not path.exists():
                continue
            df = pd.read_excel(path, sheet_name=0)

            for _, row in df.iterrows():
                customer_name = clean_text(
                    pick_value(row, ["1#客户名称（中）", "客户名称", "客户"])
                )
                if not customer_name:
                    self.stats.rows_skipped += 1
                    continue

                norm_customer_name = normalize_name(customer_name)
                existed_before = norm_customer_name in self.customer_by_norm_name
                customer = await self.get_or_create_customer(customer_name)

                customer.customer_name_en = clean_text(
                    pick_value(row, ["1#客户名称（EN）", "客户英文名"])
                ) or customer.customer_name_en

                region = clean_text(pick_value(row, ["区域"]))
                province = clean_text(pick_value(row, ["1#省份", "省份"]))
                city = clean_text(pick_value(row, ["1#市", "城市"]))
                district = clean_text(pick_value(row, ["1#区", "区县"]))
                customer.region = region or customer.region or province
                customer.province = province or customer.province
                customer.city = city or customer.city
                customer.district = district or customer.district

                customer.customer_type_3 = clean_text(
                    pick_value(row, ["3#客户类型", "客户类型"])
                ) or customer.customer_type_3
                customer.customer_level_3 = clean_text(
                    pick_value(row, ["3#客户分级"])
                ) or customer.customer_level_3
                deal_customer_5 = parse_int(pick_value(row, ["5#成交客户", "是否为结单客户"]))
                if deal_customer_5 is not None:
                    customer.deal_customer_5 = deal_customer_5
                electrical_engineer_count_5 = parse_int(pick_value(row, ["5#电气工程师人数"]))
                if electrical_engineer_count_5 is not None:
                    customer.electrical_engineer_count_5 = electrical_engineer_count_5

                owner_name_3 = clean_text(pick_value(row, ["3#负责人", "客户负责人"]))
                if owner_name_3:
                    owner_user = await self.ensure_user(owner_name_3, "销售")
                    customer.owner_name_3 = owner_name_3
                    customer.owner_name = owner_name_3
                    if owner_user:
                        customer.owner_id = owner_user.id

                customer.industry = clean_text(pick_value(row, ["3#行业", "所属行业"])) or customer.industry
                customer.source = clean_text(pick_value(row, ["客户来源"])) or customer.source or "外部报表导入"
                customer.address = clean_text(pick_value(row, ["1#办公地址（中）", "详细地址"])) or customer.address

                level = map_customer_level(
                    clean_text(pick_value(row, ["3#客户分级"])),
                    clean_text(pick_value(row, ["客户级别"])),
                )
                customer.level = level
                customer.customer_type = "enterprise"
                customer.updated_by = self.default_creator_id

                if existed_before:
                    self.stats.customers_updated += 1

    async def _next_opportunity_no(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"OPP{today}"
        max_no = (await self.db.execute(
            select(func.max(OpportunityInfo.opportunity_no))
            .where(OpportunityInfo.opportunity_no.like(f"{prefix}%"))
        )).scalar()
        if max_no:
            serial = int(max_no[-4:]) + 1
        else:
            serial = 1
        return f"{prefix}{serial:04d}"

    def _merge_product(self, existing: List[dict], product: dict) -> List[dict]:
        key = f"{product.get('name')}-{product.get('type')}-{product.get('quantity')}-{product.get('amount')}"
        exists = {f"{p.get('name')}-{p.get('type')}-{p.get('quantity')}-{p.get('amount')}" for p in existing}
        if key not in exists:
            existing.append(product)
        return existing

    async def import_opportunities(self) -> None:
        for filename in OPPORTUNITY_FILES:
            path = self.workspace_root / filename
            if not path.exists():
                continue
            df = pd.read_excel(path, sheet_name=0)

            for _, row in df.iterrows():
                opportunity_name = clean_text(
                    pick_value(row, ["商业机会名称", "机会名称", "商机名称"])
                )
                customer_name = clean_text(
                    pick_value(row, ["1#客户名称（中）", "客户名称"])
                )
                if not opportunity_name or not customer_name:
                    self.stats.rows_skipped += 1
                    continue

                customer = await self.get_or_create_customer(customer_name)
                stage_code = map_stage_code(pick_value(row, ["5#销售阶段", "销售阶段"]))
                stage = self.stage_by_code.get(stage_code) or self.stage_by_code.get("lead")
                if not stage:
                    continue

                key = (int(customer.id), normalize_name(opportunity_name) or "")
                opp = self.opportunity_by_key.get(key)
                is_new = opp is None

                owner_name = clean_text(
                    pick_value(row, ["机会负责人", "负责人", "客户负责人", "Eplan销售"])
                )
                owner_user = await self.ensure_user(owner_name, "销售") if owner_name else None

                amount = parse_amount(
                    pick_value(row, ["5#商机金额原币（不含税）", "总价（不含税）", "金额(€)", "服务金额"])
                )
                expected_close = parse_date(
                    pick_value(row, ["5#合同签订日期", "预计成交日期"])
                )

                product_name = clean_text(pick_value(row, ["销售机会明细-产品"]))
                product_type = clean_text(pick_value(row, ["产品类型"]))
                product_qty = parse_int(pick_value(row, ["数量"]))
                product_amount = parse_amount(pick_value(row, ["总价（不含税）", "服务金额"]))
                product_item = None
                if product_name or product_type or product_qty or product_amount:
                    product_item = {
                        "name": product_name or product_type or "未命名产品",
                        "type": product_type,
                        "quantity": product_qty or 1,
                        "price": round((product_amount or 0) / max(product_qty or 1, 1), 2),
                        "amount": round(product_amount or 0, 2),
                    }

                if is_new:
                    opp = OpportunityInfo(
                        opportunity_no=await self._next_opportunity_no(),
                        opportunity_name=opportunity_name,
                        customer_id=customer.id,
                        customer_name=customer.customer_name,
                        estimated_amount=amount,
                        currency="CNY",
                        stage_id=stage.id,
                        stage_name=stage.stage_name,
                        stage_order=stage.stage_order,
                        expected_close_date=expected_close,
                        win_probability=stage.probability,
                        priority="medium",
                        owner_id=owner_user.id if owner_user else None,
                        owner_name=owner_name,
                        lead_source=f"报表导入:{filename}",
                        status="open" if stage.stage_type == "normal" else ("won" if stage.stage_type == "won" else "lost"),
                        created_by=self.default_creator_id,
                        updated_by=self.default_creator_id,
                        products=[product_item] if product_item else [],
                    )
                    if opp.status == "won":
                        opp.actual_close_date = expected_close
                        opp.actual_amount = amount
                    self.db.add(opp)
                    await self.db.flush()
                    self.opportunity_by_key[key] = opp
                    self.stats.opportunities_created += 1
                else:
                    if stage.stage_order >= (opp.stage_order or 0):
                        opp.stage_id = stage.id
                        opp.stage_name = stage.stage_name
                        opp.stage_order = stage.stage_order
                        opp.win_probability = stage.probability
                        opp.status = "open" if stage.stage_type == "normal" else ("won" if stage.stage_type == "won" else "lost")
                    if amount is not None:
                        current_amount = float(opp.estimated_amount) if opp.estimated_amount is not None else None
                        if current_amount is None or amount > current_amount:
                            opp.estimated_amount = amount
                    if expected_close:
                        opp.expected_close_date = expected_close
                    if owner_user:
                        opp.owner_id = owner_user.id
                        opp.owner_name = owner_name
                    if product_item:
                        current_products = list(opp.products or [])
                        opp.products = self._merge_product(current_products, product_item)
                    opp.updated_by = self.default_creator_id
                    self.stats.opportunities_updated += 1

    async def _get_or_create_opportunity_from_activity(
        self,
        customer: CustomerInfo,
        opportunity_name: Optional[str],
        stage_code: str,
        owner_name: Optional[str],
    ) -> Optional[OpportunityInfo]:
        if not opportunity_name:
            return None

        key = (int(customer.id), normalize_name(opportunity_name) or "")
        existing = self.opportunity_by_key.get(key)
        if existing:
            return existing

        stage = self.stage_by_code.get(stage_code) or self.stage_by_code.get("lead")
        owner_user = await self.ensure_user(owner_name, "销售") if owner_name else None

        opp = OpportunityInfo(
            opportunity_no=await self._next_opportunity_no(),
            opportunity_name=opportunity_name,
            customer_id=customer.id,
            customer_name=customer.customer_name,
            currency="CNY",
            stage_id=stage.id if stage else None,
            stage_name=stage.stage_name if stage else "线索识别",
            stage_order=stage.stage_order if stage else 1,
            win_probability=stage.probability if stage else 5,
            priority="medium",
            owner_id=owner_user.id if owner_user else None,
            owner_name=owner_name,
            lead_source="报表导入:活动记录",
            status="open",
            created_by=self.default_creator_id,
            updated_by=self.default_creator_id,
        )
        self.db.add(opp)
        await self.db.flush()
        self.opportunity_by_key[key] = opp
        self.stats.opportunities_created += 1
        return opp

    async def import_activities(self) -> None:
        path = self.workspace_root / ACTIVITY_FILE
        if not path.exists():
            return

        df = pd.read_excel(path, sheet_name=0)

        for idx, row in df.iterrows():
            customer_name = clean_text(
                pick_value(row, ["1#客户名称（中）", "1#客户名称（中）.1", "1#客户名称（中）.2"])
            )
            if not customer_name:
                self.stats.rows_skipped += 1
                continue

            customer = await self.get_or_create_customer(customer_name)

            opportunity_name = clean_text(pick_value(row, ["商业机会名称"]))
            stage_code = map_stage_code(pick_value(row, ["5#销售阶段"]))
            owner_name = clean_text(pick_value(row, ["Eplan销售", "发布人"]))
            opportunity = await self._get_or_create_opportunity_from_activity(
                customer=customer,
                opportunity_name=opportunity_name,
                stage_code=stage_code,
                owner_name=owner_name,
            )

            raw_id = clean_text(pick_value(row, ["ID"])) or f"row{idx+1}"
            publish_dt = parse_datetime(pick_value(row, ["发布时间"])) or datetime.utcnow()
            start_dt = parse_datetime(pick_value(row, ["开始时间"])) or publish_dt
            activity_type = clean_text(pick_value(row, ["活动记录类型"])) or "电话"
            visit_method = clean_text(pick_value(row, ["拜访方式"])) or ""
            content = clean_text(pick_value(row, ["活动记录内容"])) or ""
            creator_name = clean_text(pick_value(row, ["发布人", "Eplan销售", "EPLAN技术人员"]))
            creator_user = await self.ensure_user(creator_name, "销售/技术") if creator_name else None

            technical_name = clean_text(pick_value(row, ["EPLAN技术人员"]))
            sales_name = clean_text(pick_value(row, ["Eplan销售"]))
            participants = [v for v in [technical_name, sales_name, creator_name] if v]
            participant_names = "、".join(dict.fromkeys(participants)) if participants else None

            is_visit = "拜访" in activity_type or "拜访" in visit_method

            if is_visit:
                visit_no = f"V{raw_id}"[:50]
                if visit_no not in self.existing_visit_no:
                    self.existing_visit_no.add(visit_no)
                    visit = VisitRecord(
                        visit_no=visit_no,
                        visit_type="online" if "线上" in visit_method else "onsite",
                        customer_id=customer.id,
                        customer_name=customer.customer_name,
                        opportunity_id=opportunity.id if opportunity else None,
                        participant_names=participant_names,
                        visit_date=start_dt.date(),
                        start_time=start_dt.time() if isinstance(start_dt, datetime) else None,
                        content=content,
                        result_type="positive" if "认可" in content or "签" in content else "neutral",
                        created_by=creator_user.id if creator_user else self.default_creator_id,
                    )
                    self.db.add(visit)
                    self.stats.visits_created += 1
            else:
                follow_no = f"F{raw_id}"[:50]
                if follow_no not in self.existing_follow_no:
                    self.existing_follow_no.add(follow_no)
                    follow = FollowRecord(
                        follow_no=follow_no,
                        customer_id=customer.id,
                        customer_name=customer.customer_name,
                        opportunity_id=opportunity.id if opportunity else None,
                        follow_type="call" if "电话" in activity_type else "other",
                        subject=opportunity_name or f"{customer.customer_name}跟进",
                        content=content,
                        result="positive" if "认可" in content or "推进" in content else "neutral",
                        next_follow_date=(publish_dt + timedelta(days=7)).date(),
                        created_by=creator_user.id if creator_user else self.default_creator_id,
                    )
                    self.db.add(follow)
                    self.stats.follows_created += 1

                task_no = f"T{raw_id}"[:50]
                if task_no not in self.existing_task_no:
                    self.existing_task_no.add(task_no)
                    assignee = await self.ensure_user(owner_name or creator_name, "销售") if (owner_name or creator_name) else None
                    task = TaskInfo(
                        task_no=task_no,
                        task_title=f"跟进任务-{customer.customer_name}",
                        customer_id=customer.id,
                        opportunity_id=opportunity.id if opportunity else None,
                        related_object_type="opportunity" if opportunity else "customer",
                        related_object_id=opportunity.id if opportunity else customer.id,
                        task_type="followup",
                        due_date=(publish_dt + timedelta(days=3)).date(),
                        priority="medium",
                        status="completed" if stage_code in {"closed_won", "closed_lost"} else "pending",
                        description=content[:1000],
                        assigned_to=assignee.id if assignee else self.default_creator_id,
                        created_by=creator_user.id if creator_user else self.default_creator_id,
                    )
                    self.db.add(task)
                    self.stats.tasks_created += 1

            schedule_type = "meeting" if is_visit else "call"
            schedule_key = (
                f"{customer.id}:{opportunity.id if opportunity else 0}:"
                f"{start_dt.date().isoformat()}:{schedule_type}"
            )
            if schedule_key not in self.existing_schedule_keys:
                self.existing_schedule_keys.add(schedule_key)
                schedule = Schedule(
                    schedule_title=(opportunity_name or f"{customer.customer_name}活动")[:200],
                    start_time=start_dt,
                    end_time=start_dt + timedelta(hours=1),
                    customer_id=customer.id,
                    opportunity_id=opportunity.id if opportunity else None,
                    schedule_type=schedule_type,
                    description=content[:1000] if content else None,
                    status="completed",
                    created_by=creator_user.id if creator_user else self.default_creator_id,
                )
                self.db.add(schedule)
                self.stats.schedules_created += 1

    async def refresh_statistics(self) -> None:
        customers = (await self.db.execute(
            select(CustomerInfo).where(CustomerInfo.deleted_at.is_(None))
        )).scalars().all()
        for customer in customers:
            opp_count = (await self.db.execute(
                select(func.count(OpportunityInfo.id)).where(
                    OpportunityInfo.customer_id == customer.id,
                    OpportunityInfo.deleted_at.is_(None),
                )
            )).scalar() or 0
            visit_count = (await self.db.execute(
                select(func.count(VisitRecord.id)).where(VisitRecord.customer_id == customer.id)
            )).scalar() or 0
            last_visit_at = (await self.db.execute(
                select(func.max(VisitRecord.visit_date)).where(VisitRecord.customer_id == customer.id)
            )).scalar()

            customer.opportunity_count = int(opp_count)
            customer.visit_count = int(visit_count)
            customer.last_visit_at = datetime.combine(last_visit_at, time(0, 0)) if last_visit_at else None
            customer.last_activity_at = datetime.utcnow()

        opportunities = (await self.db.execute(
            select(OpportunityInfo).where(OpportunityInfo.deleted_at.is_(None))
        )).scalars().all()
        for opp in opportunities:
            visit_count = (await self.db.execute(
                select(func.count(VisitRecord.id)).where(VisitRecord.opportunity_id == opp.id)
            )).scalar() or 0
            follow_count = (await self.db.execute(
                select(func.count(FollowRecord.id)).where(FollowRecord.opportunity_id == opp.id)
            )).scalar() or 0
            task_count = (await self.db.execute(
                select(func.count(TaskInfo.id)).where(TaskInfo.opportunity_id == opp.id)
            )).scalar() or 0
            opp.activity_count = int(visit_count + follow_count + task_count)
            opp.last_activity_at = datetime.utcnow() if opp.activity_count > 0 else opp.last_activity_at

    async def run(self) -> ImportStats:
        await self.bootstrap()
        await self.import_users_from_reports()
        await self.import_customers()
        await self.import_opportunities()
        await self.import_activities()
        await self.refresh_statistics()

        if self.dry_run:
            await self.db.rollback()
        else:
            await self.db.commit()
        return self.stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入外部CRM报表")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=BACKEND_ROOT.parent,
        help="项目根目录（默认自动推断）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅演练，不写入数据库")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    workspace_root = args.workspace_root.resolve()

    print(f"[INFO] workspace root: {workspace_root}")
    print(f"[INFO] dry run: {args.dry_run}")

    await init_db()
    async with async_session_maker() as session:
        importer = ReportImporter(session, workspace_root, dry_run=args.dry_run)
        stats = await importer.run()

    print("\n=== 导入结果 ===")
    print(f"用户: 新增 {stats.users_created}, 更新 {stats.users_updated}")
    print(f"客户: 新增 {stats.customers_created}, 更新 {stats.customers_updated}")
    print(f"商机: 新增 {stats.opportunities_created}, 更新 {stats.opportunities_updated}")
    print(f"拜访: 新增 {stats.visits_created}")
    print(f"跟进: 新增 {stats.follows_created}")
    print(f"任务: 新增 {stats.tasks_created}")
    print(f"日程: 新增 {stats.schedules_created}")
    print(f"跳过行: {stats.rows_skipped}")


if __name__ == "__main__":
    asyncio.run(main())
