import request from './request'

export const activityApi = {
  // 拜访记录
  getVisits: (params?: any) => request.get('/activity/visits', { params }),
  getVisit: (id: number) => request.get(`/activity/visits/${id}`),
  createVisit: (data: any) => request.post('/activity/visits', data),
  updateVisit: (id: number, data: any) => request.put(`/activity/visits/${id}`, data),
  deleteVisit: (id: number) => request.delete(`/activity/visits/${id}`),

  // 跟进记录
  getFollows: (params?: any) => request.get('/activity/follows', { params }),
  getFollow: (id: number) => request.get(`/activity/follows/${id}`),
  createFollow: (data: any) => request.post('/activity/follows', data),
  updateFollow: (id: number, data: any) => request.put(`/activity/follows/${id}`, data),
  deleteFollow: (id: number) => request.delete(`/activity/follows/${id}`),

  // 任务管理
  getTasks: (params?: any) => request.get('/activity/tasks', { params }),
  getTask: (id: number) => request.get(`/activity/tasks/${id}`),
  createTask: (data: any) => request.post('/activity/tasks', data),
  updateTask: (id: number, data: any) => request.put(`/activity/tasks/${id}`, data),
  completeTask: (id: number, completion_note?: string) =>
    request.post(`/activity/tasks/${id}/complete`, { completion_note }),
  cancelTask: (id: number, cancel_reason?: string) =>
    request.post(`/activity/tasks/${id}/cancel`, { cancel_reason }),
  deleteTask: (id: number) => request.delete(`/activity/tasks/${id}`),

  // 日程管理
  getSchedules: (params?: any) => request.get('/activity/schedules', { params }),
  createSchedule: (data: any) => request.post('/activity/schedules', data),
  updateSchedule: (id: number, data: any) => request.put(`/activity/schedules/${id}`, data),
  deleteSchedule: (id: number) => request.delete(`/activity/schedules/${id}`),

  // 统计
  getStatistics: (params?: any) => request.get('/activity/statistics', { params }),
}
