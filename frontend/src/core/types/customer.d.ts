/**
 * 客户资源管理相关类型定义
 */

// ==================== 基础类型 ====================

/** 客户类型 */
export type CustomerType = 'enterprise' | 'individual'

/** 客户级别 */
export type CustomerLevel = 'A' | 'B' | 'C' | 'D'

/** 客户状态 */
export type CustomerStatus = 'active' | 'inactive' | 'pool'

/** 联系人性别 */
export type Gender = 'male' | 'female' | 'other'

/** 标签类型 */
export type TagType = 'system' | 'custom'

// ==================== 客户相关类型 ====================

/** 客户基本信息 */
export interface Customer {
  id: number
  customer_no: string
  customer_name: string
  customer_name_en?: string
  region?: string
  customer_type_3?: string
  customer_level_3?: string
  deal_customer_5?: number
  electrical_engineer_count_5?: number
  owner_name_3?: string
  customer_type: CustomerType
  industry?: string
  company_size?: string
  legal_person?: string
  registered_capital?: number
  establish_date?: string
  province?: string
  city?: string
  district?: string
  address?: string
  website?: string
  company_info?: string
  product_info?: string
  source?: string
  level: CustomerLevel
  status: CustomerStatus
  owner_id?: number
  owner?: OwnerInfo
  tags?: string[]
  remarks?: string
  opportunity_count?: number
  visit_count?: number
  last_visit_at?: string
  last_activity_at?: string
  ai_summary?: string
  ai_insights?: Record<string, any>
  data_completed_at?: string
  created_at: string
  updated_at: string
}

/** 创建客户请求 */
export interface CustomerCreate {
  customer_name: string
  customer_name_en?: string
  region?: string
  customer_type_3?: string
  customer_level_3?: string
  deal_customer_5?: number
  electrical_engineer_count_5?: number
  owner_name_3?: string
  customer_type: CustomerType
  industry?: string
  company_size?: string
  legal_person?: string
  registered_capital?: number
  establish_date?: string
  province?: string
  city?: string
  district?: string
  address?: string
  website?: string
  company_info?: string
  product_info?: string
  source?: string
  level?: CustomerLevel
  owner_id?: number
  tags?: string[]
  remarks?: string
}

/** 更新客户请求 */
export interface CustomerUpdate {
  customer_name?: string
  customer_name_en?: string
  region?: string
  customer_type_3?: string
  customer_level_3?: string
  deal_customer_5?: number
  electrical_engineer_count_5?: number
  owner_name_3?: string
  customer_type?: CustomerType
  industry?: string
  company_size?: string
  legal_person?: string
  registered_capital?: number
  establish_date?: string
  province?: string
  city?: string
  district?: string
  address?: string
  website?: string
  company_info?: string
  product_info?: string
  source?: string
  level?: CustomerLevel
  owner_id?: number
  tags?: string[]
  remarks?: string
}

/** 客户详情 */
export interface CustomerDetail extends Customer {
  contacts: Contact[]
  statistics: CustomerStatistics
}

/** 客户统计信息 */
export interface CustomerStatistics {
  opportunity_count: number
  visit_count: number
  last_visit_at?: string
  last_activity_at?: string
}

/** 负责人信息 */
export interface OwnerInfo {
  id: number
  name?: string
  email?: string
}

/** 客户查询参数 */
export interface CustomerQueryParams {
  keyword?: string
  customer_type?: CustomerType
  level?: CustomerLevel
  status?: CustomerStatus
  owner_id?: number
  tags?: string[]
  region?: string
  industry?: string
  source?: string
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

/** 客户列表响应 */
export interface CustomerListResponse {
  items: Customer[]
  total: number
  page: number
  page_size: number
}

/** 客户转移请求 */
export interface CustomerTransfer {
  to_user_id: number
  remark?: string
}

/** 客户批量操作请求 */
export interface CustomerBatchOperation {
  action: 'transfer' | 'assignTags' | 'changeLevel' | 'changeStatus'
  customer_ids: number[]
  params?: Record<string, any>
}

// ==================== 客户交互记录类型 ====================

/** 交互记录 */
export interface CustomerInteraction {
  id: number
  customer_id: number
  contact_id?: number
  interaction_type: 'call' | 'email' | 'visit' | 'wechat' | 'other'
  direction?: 'inbound' | 'outbound'
  subject?: string
  content?: string
  duration?: number
  attachments?: string[]
  next_follow_at?: string
  next_follow_note?: string
  created_by?: number
  created_at: string
}

/** 创建交互记录请求 */
export interface CustomerInteractionCreate {
  contact_id?: number
  interaction_type: 'call' | 'email' | 'visit' | 'wechat' | 'other'
  direction?: 'inbound' | 'outbound'
  subject?: string
  content?: string
  duration?: number
  attachments?: string[]
  next_follow_at?: string
  next_follow_note?: string
}

/** 交互记录列表响应 */
export interface CustomerInteractionListResponse {
  items: CustomerInteraction[]
  total: number
  page: number
  page_size: number
}

// ==================== 联系人相关类型 ====================

/** 联系人信息 */
export interface Contact {
  id: number
  contact_no: string
  customer_id: number
  name: string
  title?: string
  department?: string
  gender?: Gender
  mobile?: string
  phone?: string
  email?: string
  wechat?: string
  is_decision_maker: boolean
  is_influencer: boolean
  influence_level?: number
  relationship?: string
  preference?: string
  birthday?: string
  hobbies?: string
  linkedin?: string
  weibo?: string
  is_primary: boolean
  remarks?: string
  status: string
  contact_count?: number
  last_contact_at?: string
  created_at: string
  updated_at: string
}

/** 创建联系人请求 */
export interface ContactCreate {
  name: string
  title?: string
  department?: string
  gender?: Gender
  mobile?: string
  phone?: string
  email?: string
  wechat?: string
  is_decision_maker?: boolean
  is_influencer?: boolean
  influence_level?: number
  relationship?: string
  preference?: string
  birthday?: string
  hobbies?: string
  linkedin?: string
  weibo?: string
  is_primary?: boolean
  remarks?: string
}

/** 更新联系人请求 */
export interface ContactUpdate {
  name?: string
  title?: string
  department?: string
  gender?: Gender
  mobile?: string
  phone?: string
  email?: string
  wechat?: string
  is_decision_maker?: boolean
  is_influencer?: boolean
  influence_level?: number
  relationship?: string
  preference?: string
  birthday?: string
  hobbies?: string
  linkedin?: string
  weibo?: string
  is_primary?: boolean
  remarks?: string
}

/** 联系人列表响应 */
export interface ContactListResponse {
  items: Contact[]
  total: number
}

// ==================== 标签相关类型 ====================

/** 客户标签 */
export interface CustomerTag {
  id: number
  tag_name: string
  tag_color?: string
  tag_type: TagType
  sort_order: number
  created_at: string
}

/** 创建标签请求 */
export interface TagCreate {
  tag_name: string
  tag_color?: string
  tag_type?: TagType
  sort_order?: number
}

/** 更新标签请求 */
export interface TagUpdate {
  tag_name?: string
  tag_color?: string
  tag_type?: TagType
  sort_order?: number
}

/** 标签列表响应 */
export interface TagListResponse {
  items: CustomerTag[]
  total: number
}

// ==================== 360度视图相关类型 ====================

/** 时间轴条目 */
export interface TimelineItem {
  type: string
  title: string
  content: string
  created_at: string
  created_by?: string
}

/** 客户360度视图 */
export interface Customer360View {
  customer: CustomerDetail
  contacts: Contact[]
  opportunities: Record<string, any>[]
  visits: Record<string, any>[]
  interactions: Record<string, any>[]
  tasks: Record<string, any>[]
  documents: Record<string, any>[]
  timeline: TimelineItem[]
}

/** 360度视图响应 */
export interface Customer360ViewResponse {
  customer: CustomerDetail
  contacts: Contact[]
  opportunities: Record<string, any>[]
  visits: Record<string, any>[]
  interactions: Record<string, any>[]
  tasks: Record<string, any>[]
  documents: Record<string, any>[]
  timeline: TimelineItem[]
}

// ==================== 导入导出相关类型 ====================

/** 导入结果 */
export interface ImportResult {
  success_count: number
  error_count: number
  errors: ImportErrorItem[]
}

/** 导入错误项 */
export interface ImportErrorItem {
  row: number
  data: Record<string, any>
  error: string
}
