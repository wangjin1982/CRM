# CRM 对标研究与漏斗优化说明

## 1. 目标

基于你提供的外部 CRM 报表数据与销售阶段定义，完成以下工作：

1. 导入并打通客户、商机、活动记录数据。
2. 优化销售阶段与销售漏斗逻辑（含 `Lead -> ... -> Closed Won -> Closed Lost`）。
3. 引入“动态分析 + 下一步建议”能力，避免 CRM 仅停留在静态台账。

---

## 2. 外部 CRM 产品对标（3个）

### 2.1 Salesforce（官方文档）

- 核心参考：Opportunity Stages / Sales Pipeline / Forecasting
- 可借鉴点：
  1. 阶段标准化（每个阶段有明确概率和业务定义）
  2. 机会推进与预测联动（阶段、金额、赢率共同影响预测）
  3. 以 Opportunity 为中心串联活动、联系人、任务

参考：
- [Salesforce Help - Opportunity Stages](https://help.salesforce.com/s/articleView?id=sales.opportunities_stages.htm&type=5)
- [Salesforce - Pipeline Management](https://www.salesforce.com/au/sales/pipeline-management/)

### 2.2 HubSpot（官方文档）

- 核心参考：Deal Stage 与 Probability、Closed Won / Closed Lost 阶段
- 可借鉴点：
  1. 阶段属性可配置概率，便于漏斗计算
  2. 结束态（Won/Lost）分离，便于复盘
  3. 交易看板与漏斗视图并存

参考：
- [HubSpot Knowledge Base - Set up and customize deal stages](https://knowledge.hubspot.com/object-settings/set-up-and-customize-deal-stages-and-pipeline)
- [HubSpot Developers - Deal stage guide](https://developers.hubspot.com/docs/api-reference/crm-deals-v3/guide)

### 2.3 Zoho CRM（官方文档）

- 核心参考：Stage-Probability Mapping、Forecast Category
- 可借鉴点：
  1. 阶段与概率映射可直接服务预测
  2. 支持按 Pipeline 视角做团队管理
  3. Forecast 视角支持管理层决策

参考：
- [Zoho CRM - Mapping sales stages and probability](https://help.zoho.com/portal/en/kb/crm/customize-crm-account/customizing-modules/articles/mapping-sales-stages-and-probability)

---

## 3. CRM 论文对标（3篇）

### 3.1 CRM 文献综述（理论框架）

- Greve, N. (2021). *Customer relationship management and organizational innovation: A literature review*.
- 结论要点：CRM 不应仅记录客户数据，而要嵌入组织流程与创新机制；数据与业务动作要闭环。

参考：
- [Journal of Business Research (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0148296321003151)

### 3.2 B2B 销售预测模型（漏斗预测方法）

- Wirth et al. (2020). *A Predictive Model for Evaluating B2B Sales Pipeline Opportunities*.
- 结论要点：通过机器学习可显著提升机会赢单预测质量，优于仅凭经验概率设置。

参考：
- [Forecasting, 2020 (MDPI)](https://www.mdpi.com/2571-9394/2/4/28)

### 3.3 流失预测算法研究（客户风险识别）

- Zdravev et al. (2024). *A Comparison of Machine Learning Algorithms in Customer Churn Prediction*.
- 结论要点：流失/风险识别可通过特征工程 + 模型比较落地，为 CRM 增加预警能力。

参考：
- [Algorithms, 2024 (MDPI)](https://www.mdpi.com/1999-4893/17/9/427)

---

## 4. 本系统已落地优化

## 4.1 阶段体系优化

- 新增并启用 `Lead` 阶段，阶段顺序更新为：
  `Lead -> Prospect -> Qualify -> Need -> Upside -> Endorse -> Stretch -> Commit -> Deliver -> Closed Won -> Closed Lost`
- 每个阶段补充了：
  - 概率（probability）
  - 建议停留天数（duration_days）
  - 技术动作、销售动作、判定标准

## 4.2 漏斗分析优化

- 转化率改为动态计算（按实际阶段代码自动生成）
- 新增阶段健康度指标：
  - 平均停留天数
  - 停滞率
  - 停滞数量
- 新增“下一步建议”：
  - 转化率缺口建议
  - 停滞风险建议

## 4.3 商机详情联动销售行为

- 在商机详情中新增“活动记录”标签：
  - 拜访
  - 跟进
  - 任务
  - 日程
- 后端任务/日程接口支持按 `opportunityId` 过滤，实现商机级联动查看。

## 4.4 外部报表导入能力

- 新增脚本：
  - `backend/scripts/import_external_reports.py`
  - `scripts/import_reports.sh`
- 支持导入：
  - 客户（AllAccounts / Top客户 / 客户服务情况）
  - 商机（AllPipeline / Top机会 / Renew+Pipeline / Sleeper2026 / 客户启航 / 商机明细）
  - 活动（活动记录）
- 支持增量去重与关联：
  - 客户名去重
  - 商机（客户 + 商机名）去重
  - 活动 ID 去重（Visit/Follow/Task）

---

## 5. 数据导入执行方式

在项目根目录执行：

```bash
./scripts/import_reports.sh
```

演练模式（不写入数据库）：

```bash
./scripts/import_reports.sh --dry-run
```

---

## 6. 下一阶段建议

1. 引入“商机赢单概率模型”（基于历史阶段流转 + 活动密度 + 停留时长）
2. 增加“客户流失风险模型”（结合拜访频次、跟进间隔、历史赢单）
3. 将 `TO / TBM / RTM / ISM` 角色映射到组织与权限模型，形成责任闭环
4. 增加导入任务日志页面（显示每次导入成功/失败明细）

