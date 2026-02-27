/** 商机相关类型定义 */

/** 商机状态 */
export type OpportunityStatus = 'open' | 'won' | 'lost' | 'abandoned'

/** 优先级 */
export type Priority = 'high' | 'medium' | 'low'

/** 销售阶段 */
export interface Stage {
  id: number
  stage_name: string
  stage_code: string
  stage_order: number
  stage_type: 'normal' | 'won' | 'lost'
  probability: number
  weight?: number
  duration_days?: number
  description?: string
  internal_code?: string
  customer_journey?: string
  technical_support?: string
  sales_process?: string
  stage_criteria?: string
  is_active: boolean
}

/** 商机信息 */
export interface Opportunity {
  id: number
  opportunity_no: string
  opportunity_name: string
  customer_id: number
  customer_name?: string
  primary_contact_id?: number
  estimated_amount?: number
  actual_amount?: number
  currency: string
  stage_id: number
  stage_name?: string
  stage_order?: number
  expected_close_date?: string
  actual_close_date?: string
  win_probability: number
  priority: Priority
  owner_id?: number
  owner_name?: string
  status: OpportunityStatus
  risk_level?: string
  days_in_stage: number
  is_stagnant: boolean
  activity_count: number
  last_activity_at?: string
  created_at: string
  updated_at: string
  products?: OpportunityProduct[]
  tags?: string[]
  lead_source?: string
  description?: string
  lost_reason?: string
}

/** 产品信息 */
export interface OpportunityProduct {
  name: string
  quantity: number
  price: number
  amount: number
}

/** 创建商机请求 */
export interface OpportunityCreate {
  opportunity_name: string
  customer_id: number
  primary_contact_id?: number
  estimated_amount?: number
  currency?: string
  stage_id: number
  expected_close_date?: string
  win_probability?: number
  priority?: Priority
  owner_id?: number
  lead_source?: string
  description?: string
  tags?: string[]
  products?: OpportunityProduct[]
}

/** 更新商机请求 */
export interface OpportunityUpdate {
  opportunity_name?: string
  primary_contact_id?: number
  estimated_amount?: number
  currency?: string
  expected_close_date?: string
  win_probability?: number
  priority?: Priority
  owner_id?: number
  lead_source?: string
  description?: string
  tags?: string[]
  products?: OpportunityProduct[]
}

/** 商机分页参数 */
export interface OpportunityPageParams {
  page?: number
  page_size?: number
  keyword?: string
  customer_id?: number
  stage_id?: number
  status?: OpportunityStatus
  owner_id?: number
  priority?: Priority
  start_date?: string
  end_date?: string
  min_amount?: number
  max_amount?: number
  is_stagnant?: boolean
}

/** 商机统计 */
export interface OpportunityStatistics {
  total_count: number
  open_count: number
  won_count: number
  lost_count: number
  stagnant_count: number
  total_amount: number
}

/** 销售漏斗数据 */
export interface FunnelData {
  funnel: FunnelStage[]
  summary: FunnelSummary
  conversion_rates: ConversionRates
  conversion_stages?: StageConversion[]
  stage_health?: StageHealth[]
  win_loss?: {
    won_count: number
    lost_count: number
  }
  recommendations?: FunnelRecommendation[]
}

/** 漏斗阶段 */
export interface FunnelStage {
  stage_id: number
  stage_name: string
  stage_order: number
  count: number
  amount: number
  probability: number
  weighted_amount: number
}

/** 漏斗汇总 */
export interface FunnelSummary {
  total_count: number
  total_amount: number
  weighted_amount: number
  avg_amount: number
}

/** 转化率 */
export type ConversionRates = Record<string, number>

export interface StageConversion {
  key: string
  from_stage_code: string
  from_stage_name: string
  to_stage_code: string
  to_stage_name: string
  rate: number
  from_count: number
  to_count: number
}

export interface StageHealth {
  stage_id: number
  stage_name: string
  stage_code: string
  count: number
  avg_days_in_stage: number
  stagnant_count: number
  stagnant_rate: number
}

export interface FunnelRecommendation {
  type: string
  priority: 'high' | 'medium' | 'low'
  title: string
  action: string
}

/** 阶段变更请求 */
export interface StageChangeRequest {
  to_stage_id: number
  notes?: string
}

/** 赢单请求 */
export interface OpportunityWonRequest {
  actual_amount: number
  actual_close_date: string
  notes?: string
}

/** 输单请求 */
export interface OpportunityLostRequest {
  lost_reason: string
  competitor?: string
  notes?: string
}

/** 竞争对手 */
export interface Competitor {
  id: number
  opportunity_id: number
  competitor_name: string
  strength?: string
  weakness?: string
  price_offer?: number
  threat_level?: number
}

/** 添加竞争对手请求 */
export interface CompetitorCreate {
  competitor_name: string
  strength?: string
  weakness?: string
  price_offer?: number
  threat_level?: number
}

/** 商机联系人 */
export interface OpportunityContact {
  id: number
  contact_id: number
  contact_name?: string
  contact_title?: string
  role?: string
  influence_level?: number
  is_primary: boolean
}

export interface StageHistory {
  id: number
  from_stage_id?: number
  from_stage_name?: string
  to_stage_id: number
  to_stage_name: string
  stage_duration?: number
  changed_at: string
  changed_by?: number
  changed_by_name?: string
  notes?: string
}

/** 看板数据 */
export interface KanbanData {
  stage_id: number
  stage_name: string
  stage_order: number
  probability: number
  opportunities: Opportunity[]
}
