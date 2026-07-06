import { api } from "./client";

export const dashboardV2Api = {
  getOverview: (period) => api.get("/dashboard/overview", { params: { period } }),
  getAnalytics: (period) => api.get("/dashboard/analytics", { params: { period } }),
  getSpending: (category, period) => api.get("/dashboard/spending", { params: { category, period } }),
  getCashflow: (months) => api.get("/dashboard/cashflow", { params: { months } }),
  getMonthly: (months) => api.get("/dashboard/monthly", { params: { months } }),
  getBudgets: (period) => api.get("/dashboard/budgets", { params: { period } }),
  getInsights: () => api.get("/dashboard/insights"),
  getNotifications: (unreadOnly, limit, offset) =>
    api.get("/dashboard/notifications", { params: { unread_only: unreadOnly, limit, offset } }),
  getUnreadCount: () => api.get("/dashboard/notifications/unread-count"),
  markRead: (id) => api.post(`/dashboard/notifications/${id}/read`),
  markAllRead: () => api.post("/dashboard/notifications/read-all"),
  getActivity: () => api.get("/dashboard/activity"),
  getWidgets: (widgets, period) =>
    api.get("/dashboard/widgets", { params: { widget: widgets, period } }),
  subscribe: () => api.post("/ws/dashboard/subscribe"),
};
