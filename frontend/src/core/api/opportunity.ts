import request from './request'
import type {
  Opportunity,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunityPageParams,
  OpportunityStatistics,
  Stage,
  FunnelData,
  KanbanData,
  ConversionRates,
  StageChangeRequest,
  OpportunityWonRequest,
  OpportunityLostRequest,
  CompetitorCreate,
  Competitor,
  OpportunityContact,
  StageHistory,
} from '../types/opportunity'
import type { PageResponse } from '../types/common'

export const opportunityApi = {
  // 获取商机列表
  getOpportunities: (params: OpportunityPageParams) =>
    request.get<any, PageResponse<Opportunity>>('/opportunities', { params }),

  // 获取商机统计
  getStatistics: (ownerId?: number) =>
    request.get<any, OpportunityStatistics>('/opportunities/statistics', {
      params: { owner_id: ownerId },
    }),

  // 获取商机详情
  getOpportunity: (id: number) =>
    request.get<any, Opportunity>(`/opportunities/${id}`),

  // 获取阶段历史
  getStageHistory: (id: number) =>
    request.get<any, StageHistory[]>(`/opportunities/${id}/stage-history`),

  // 创建商机
  createOpportunity: (data: OpportunityCreate) =>
    request.post('/opportunities', data),

  // 更新商机
  updateOpportunity: (id: number, data: OpportunityUpdate) =>
    request.put(`/opportunities/${id}`, data),

  // 删除商机
  deleteOpportunity: (id: number) => request.delete(`/opportunities/${id}`),

  // 转移商机
  transferOpportunity: (id: number, toUserId: number, remark?: string) =>
    request.post(`/opportunities/${id}/transfer`, { to_user_id: toUserId, remark }),

  // 推进阶段
  changeStage: (id: number, data: StageChangeRequest) =>
    request.post(`/opportunities/${id}/stage`, data),

  // 标记赢单
  markAsWon: (id: number, data: OpportunityWonRequest) =>
    request.post(`/opportunities/${id}/won`, data),

  // 标记输单
  markAsLost: (id: number, data: OpportunityLostRequest) =>
    request.post(`/opportunities/${id}/lost`, data),

  // 关联联系人
  addContacts: (id: number, contactIds: number[], role?: string, influenceLevel?: number) =>
    request.post(`/opportunities/${id}/contacts`, { contact_ids: contactIds, role, influence_level }),

  // 获取商机关联联系人
  getContacts: (id: number) =>
    request.get<any, OpportunityContact[]>(`/opportunities/${id}/contacts`),

  // 移除联系人关联
  removeContact: (id: number, contactId: number) =>
    request.delete(`/opportunities/${id}/contacts/${contactId}`),

  // 添加竞争对手
  addCompetitor: (id: number, data: CompetitorCreate) =>
    request.post(`/opportunities/${id}/competitors`, data),
}

export const stageApi = {
  // 获取所有阶段
  getStages: (isActive = true) =>
    request.get<any, Stage[]>('/stages', { params: { is_active: isActive } }),

  // 获取阶段详情
  getStage: (id: number) => request.get<any, Stage>(`/stages/${id}`),

  // 创建阶段
  createStage: (data: Partial<Stage>) => request.post('/stages', data),

  // 更新阶段
  updateStage: (id: number, data: Partial<Stage>) => request.put(`/stages/${id}`, data),

  // 删除阶段
  deleteStage: (id: number) => request.delete(`/stages/${id}`),
}

export const funnelApi = {
  // 获取销售漏斗数据
  getFunnel: (ownerId?: number, startDate?: string, endDate?: string) =>
    request.get<any, FunnelData>('/funnel', {
      params: { owner_id: ownerId, start_date: startDate, end_date: endDate },
    }),

  // 获取看板数据
  getKanbanBoard: (ownerId?: number) =>
    request.get<any, KanbanData[]>('/funnel/board', {
      params: { owner_id: ownerId },
    }),

  // 获取转化率
  getConversionRates: (ownerId?: number) =>
    request.get<any, ConversionRates>('/funnel/conversion', {
      params: { owner_id: ownerId },
    }),
}
