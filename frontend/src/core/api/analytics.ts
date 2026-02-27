import request from './request'

export const analyticsApi = {
  dashboardHome: () => request.get('/analytics/dashboard/home'),
  dashboardSales: (owner_id?: number) => request.get('/analytics/dashboard/sales', { params: { owner_id } }),
  dashboardManagement: () => request.get('/analytics/dashboard/management'),

  customerAnalysis: () => request.get('/analytics/customers'),
  opportunityAnalysis: () => request.get('/analytics/opportunities'),
  activityAnalysis: (start_date?: string, end_date?: string) =>
    request.get('/analytics/activities', { params: { start_date, end_date } }),

  listReports: () => request.get('/analytics/reports'),
  createReport: (data: any) => request.post('/analytics/reports', data),
  executeReport: (id: number, params?: any) => request.get(`/analytics/reports/${id}/execute`, { params }),
  exportReport: (id: number, params?: any) =>
    request.get(`/analytics/reports/${id}/export`, { params, responseType: 'blob' }),
}
