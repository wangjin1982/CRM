import request from './request'

export const aiApi = {
  smartComplete: (data: {
    entity_type: string
    entity_id: number
    missing_fields?: string[]
    context?: Record<string, any>
  }) => request.post('/ai/complete', data),

  getCompleteStatus: (taskId: string) => request.get(`/ai/complete/${taskId}`),

  analyzeOpportunityRisk: (opportunityId: number) =>
    request.post(`/ai/risk/opportunity/${opportunityId}`),

  batchRiskScan: (data: { opportunity_ids?: number[]; threshold_days?: number }) =>
    request.post('/ai/risk/batch-scan', data),

  summarizeVisit: (visitId: number) => request.post(`/ai/analyze/visit/${visitId}`),

  analyzeFunnel: (owner_id?: number) => request.get('/ai/analyze/funnel', { params: { owner_id } }),

  nlQuery: (query: string) => request.post('/ai/query', { query }),

  listAlerts: (params?: any) => request.get('/ai/alerts', { params }),
  acknowledgeAlert: (id: number, note?: string) => request.post(`/ai/alerts/${id}/ack`, { note }),
  resolveAlert: (id: number, note?: string) => request.post(`/ai/alerts/${id}/resolve`, { note }),

  getConfig: () => request.get('/ai/config'),
  updateConfig: (data: any) => request.put('/ai/config', data),
  enrichCustomer: (customerId: number, data?: { target_fields?: string[]; overwrite?: boolean }) =>
    request.post(`/ai/customers/${customerId}/enrich`, data || {}),
  previewCustomerEnrich: (customerId: number, data?: { target_fields?: string[]; overwrite?: boolean }) =>
    request.post(`/ai/customers/${customerId}/enrich/preview`, data || {}),
  applyCustomerEnrich: (customerId: number, data: { request_id?: string; updates: Record<string, any> }) =>
    request.post(`/ai/customers/${customerId}/enrich/apply`, data),

  listPrompts: (scene?: string) => request.get('/ai/prompts', { params: { scene } }),
  createPrompt: (data: any) => request.post('/ai/prompts', data),
  updatePrompt: (id: number, data: any) => request.put(`/ai/prompts/${id}`, data),
}
