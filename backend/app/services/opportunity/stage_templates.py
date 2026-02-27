"""商机阶段模板（来源: EPLAN Sales Workbook 20230604.xlsx）"""

DEFAULT_STAGE_TEMPLATES = [
    {
        "stage_name": "线索识别",
        "stage_code": "lead",
        "stage_order": 1,
        "stage_type": "normal",
        "probability": 5,
        "weight": 0.05,
        "duration_days": 7,
        "internal_code": "L",
        "customer_journey": "Awareness",
        "description": "线索识别 / Lead（对应 Aware + Attract）",
        "technical_support": (
            "1. 提供行业基准材料与典型应用场景\n"
            "2. 识别客户技术成熟度、数字化基础与软件环境\n"
            "3. 判断是否具备后续技术交流价值"
        ),
        "sales_process": (
            "1. 建立初始联系人与客户画像（行业/规模/组织）\n"
            "2. 明确线索来源与业务触发点\n"
            "3. 完成首轮资格判断并确认是否进入 Prospect"
        ),
        "stage_criteria": (
            "1. 客户信息基本完整且真实\n"
            "2. 存在明确业务问题或升级诉求\n"
            "3. 允许进入下一轮正式沟通"
        ),
    },
    {
        "stage_name": "潜在商机",
        "stage_code": "prospect",
        "stage_order": 2,
        "stage_type": "normal",
        "probability": 10,
        "weight": 0.10,
        "duration_days": 10,
        "internal_code": "P",
        "customer_journey": "Prospect",
        "description": "潜在商机 / Prospect",
        "technical_support": (
            "1. 标准化的EPLAN公司、产品、解决方案、成功案例Presentation\n"
            "2. EPLAN Products Sales Toolkit\n"
            "3. 识别客户是否符合EPLAN理想客户能力培训"
        ),
        "sales_process": (
            "1. 明确客户信息要求：行业、集团/企业架构、客户性质、营收、信息化、电气设计/制造部门\n"
            "2. 明确客户联络人与初步沟通"
        ),
        "stage_criteria": (
            "1. 符合ICP理想客户判断标准\n"
            "2. 客户与EPLAN开始正式交流"
        ),
    },
    {
        "stage_name": "客户意向",
        "stage_code": "qualify",
        "stage_order": 3,
        "stage_type": "normal",
        "probability": 20,
        "weight": 0.20,
        "duration_days": 14,
        "internal_code": "Q",
        "customer_journey": "Qualify",
        "description": "客户意向 / Qualify",
        "technical_support": (
            "1. 准备类似成功案例与相关资料\n"
            "2. 准备客户调研资料（如18问）\n"
            "3. 明确客户痛点与EPLAN方案初步匹配"
        ),
        "sales_process": (
            "1. 收集组织架构、设计人数、项目数量、流程、信息化、痛点与改进期望\n"
            "2. 获取关键人员联系方式\n"
            "3. 识别UB/TB/EB\n"
            "4. 发掘可发展为Coach的对象"
        ),
        "stage_criteria": "有UB/TB公开表达兴趣，并约定下一次交流及参与人。",
    },
    {
        "stage_name": "需求深入",
        "stage_code": "need",
        "stage_order": 4,
        "stage_type": "normal",
        "probability": 30,
        "weight": 0.30,
        "duration_days": 18,
        "internal_code": "N",
        "customer_journey": "Attraction",
        "description": "需求深入 / Need",
        "technical_support": (
            "1. 明确Technical Owner\n"
            "2. 将痛点转化为需求并争取TB/UB认可\n"
            "3. 针对性调研并输出As-Is报告\n"
            "4. 提交专家配置清单并初步确认软件配置数量\n"
            "5. Best Practice Sharing\n"
            "6. 确认To-Be期望"
        ),
        "sales_process": (
            "1. 推动TB/UB交流并引导需求\n"
            "2. 建立Coach\n"
            "3. 做方案与价值呈现，和TB/UB初步达成一致\n"
            "4. 确认采购习惯并初步报价\n"
            "5. TB同意推动立项"
        ),
        "stage_criteria": (
            "1. 已确定EPLAN应用场景与紧急业务问题\n"
            "2. 客户愿意改变现有软件/流程\n"
            "3. TB已反馈并推动立项"
        ),
    },
    {
        "stage_name": "项目立项",
        "stage_code": "upside",
        "stage_order": 5,
        "stage_type": "normal",
        "probability": 40,
        "weight": 0.40,
        "duration_days": 21,
        "internal_code": "U",
        "customer_journey": "Upside",
        "description": "项目立项 / Upside",
        "technical_support": (
            "1. As-Is与To-Be差距分析\n"
            "2. 与TB确认在可接受价格范围内的最佳To-Be及实现路径\n"
            "3. Proposal"
        ),
        "sales_process": (
            "1. TB/UB支持EPLAN\n"
            "2. 有Coach可传递准确信息\n"
            "3. 明确立项流程、预算来源、周期、负责人\n"
            "4. 确认客户采购习惯、采购周期、付款条件"
        ),
        "stage_criteria": (
            "1. 客户对Proposal兴趣高并希望深入沟通\n"
            "2. TB/EB已认可初步Proposal\n"
            "3. 已和EB正式会谈"
        ),
    },
    {
        "stage_name": "方案确认",
        "stage_code": "endorse",
        "stage_order": 6,
        "stage_type": "normal",
        "probability": 50,
        "weight": 0.50,
        "duration_days": 20,
        "internal_code": "E",
        "customer_journey": "Conversion",
        "description": "方案确认 / Endorse",
        "technical_support": (
            "1. 向EB汇报最终To-Be方案与Benefit\n"
            "2. 确定软件配置表\n"
            "3. 完成SOW最终谈判\n"
            "4. 提供实施阶段与收益预期"
        ),
        "sales_process": (
            "1. 明确采购流程与时间（招投标/比价/单一来源）\n"
            "2. 通过Coach获取竞争对手方案和报价\n"
            "3. TB坚挺支持EPLAN，EB认同方案价值"
        ),
        "stage_criteria": (
            "1. POC结束且UB/TB/EB认可验证项\n"
            "2. 技术方案层面已基本胜出\n"
            "3. 招采流程已有明确时间计划"
        ),
    },
    {
        "stage_name": "商务谈判",
        "stage_code": "stretch",
        "stage_order": 7,
        "stage_type": "normal",
        "probability": 70,
        "weight": 0.70,
        "duration_days": 15,
        "internal_code": "S",
        "customer_journey": "Renewal",
        "description": "商务谈判 / Stretch",
        "technical_support": None,
        "sales_process": (
            "1. 确定SOW时间计划，不修改范围\n"
            "2. 通过Coach了解EB价格底线\n"
            "3. 提供协商后最终报价\n"
            "4. 采购周期可控"
        ),
        "stage_criteria": (
            "1. EB/采购对总价有疑问并进行压价\n"
            "2. Coach可传达成交价预期\n"
            "3. TB/UB明确非EPLAN不用\n"
            "4. 采购准备商务合同"
        ),
    },
    {
        "stage_name": "合同成交",
        "stage_code": "commit",
        "stage_order": 8,
        "stage_type": "normal",
        "probability": 90,
        "weight": 0.90,
        "duration_days": 10,
        "internal_code": "C",
        "customer_journey": "Closing",
        "description": "合同成交 / Commit",
        "technical_support": (
            "1. 组建PS服务项目组\n"
            "2. 项目经理及成员深入理解项目目标和计划\n"
            "3. 与客户项目经理反复确认节点、人员、交付物"
        ),
        "sales_process": "1. 双方合同审批与盖章\n2. 销售下单",
        "stage_criteria": "TB或Coach能够协调内部推动项目采购流程。",
    },
    {
        "stage_name": "项目执行",
        "stage_code": "deliver",
        "stage_order": 9,
        "stage_type": "normal",
        "probability": 95,
        "weight": 0.95,
        "duration_days": 30,
        "internal_code": "D",
        "customer_journey": "Onboarding",
        "description": "项目执行 / Deliver",
        "technical_support": (
            "1. 项目开工会\n"
            "2. 要求客户设奖励机制和全职参与人员\n"
            "3. 按计划执行与交付，输出周报，提前识别风险并规避变更影响"
        ),
        "sales_process": (
            "1. 提交项目交接表并提供临时EID\n"
            "2. 邀请EB/TB参加开工会\n"
            "3. 关注项目进度并维护关系预期"
        ),
        "stage_criteria": "客户对软件完成签收。",
    },
    {
        "stage_name": "项目完成",
        "stage_code": "closed_won",
        "stage_order": 10,
        "stage_type": "won",
        "probability": 100,
        "weight": 1.0,
        "duration_days": None,
        "internal_code": "CW",
        "customer_journey": "Closed Won",
        "description": "项目完成 / Closed Won",
        "technical_support": (
            "1. 交付所有交付物\n"
            "2. 提交过程文档（签到、周报、遗留问题清单）\n"
            "3. 组织项目成果回顾并取得验收单"
        ),
        "sales_process": (
            "1. 转正式EID\n"
            "2. 邀请TB参加验收会\n"
            "3. 推动验收、开票、收款与下一期规划"
        ),
        "stage_criteria": (
            "1. 客户完成验收签字\n"
            "2. 客户接收发票\n"
            "3. 客户完成付款"
        ),
    },
    {
        "stage_name": "商机关闭",
        "stage_code": "closed_lost",
        "stage_order": 11,
        "stage_type": "lost",
        "probability": 0,
        "weight": 0.0,
        "duration_days": None,
        "internal_code": "CL",
        "customer_journey": "Closed Lost",
        "description": "商机关闭 / Closed Lost",
        "technical_support": None,
        "sales_process": "商机终止，沉淀输单原因与竞争信息，纳入复盘。",
        "stage_criteria": "客户明确不再推进当前商机。",
    },
]
