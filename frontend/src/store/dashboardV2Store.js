import { dashboardV2Api } from "../api/dashboardV2";

let subscribers = [];
let state = {
  overview: null,
  analytics: null,
  budgets: null,
  insights: null,
  notifications: [],
  unreadCount: 0,
  activity: [],
  widgets: {},
  loading: false,
  error: null,
  period: null,
  wsConnected: false,
};

export const dashboardV2Store = {
  subscribe(fn) {
    subscribers.push(fn);
    fn(state);
    return () => {
      subscribers = subscribers.filter((s) => s !== fn);
    };
  },
  getState() {
    return state;
  },
  setPartial(partial) {
    state = { ...state, ...partial };
    subscribers.forEach((fn) => fn(state));
  },
  async fetchOverview(period) {
    state = { ...state, loading: true, error: null, period };
    subscribers.forEach((fn) => fn(state));
    try {
      const res = await dashboardV2Api.getOverview(period);
      state = { ...state, overview: res.data, loading: false };
    } catch {
      state = { ...state, loading: false, error: "Could not load dashboard." };
    }
    subscribers.forEach((fn) => fn(state));
  },
  async fetchAnalytics(period) {
    try {
      const res = await dashboardV2Api.getAnalytics(period);
      state = { ...state, analytics: res.data };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async fetchBudgets(period) {
    try {
      const res = await dashboardV2Api.getBudgets(period);
      state = { ...state, budgets: res.data };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async fetchInsights() {
    try {
      const res = await dashboardV2Api.getInsights();
      state = { ...state, insights: res.data };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async fetchNotifications() {
    try {
      const [notifRes, unreadRes] = await Promise.all([
        dashboardV2Api.getNotifications(false, 50, 0),
        dashboardV2Api.getUnreadCount(),
      ]);
      state = {
        ...state,
        notifications: notifRes.data,
        unreadCount: unreadRes.data.unread_count,
      };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async fetchActivity() {
    try {
      const res = await dashboardV2Api.getActivity();
      state = { ...state, activity: res.data };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async fetchWidgets(widgets, period) {
    try {
      const res = await dashboardV2Api.getWidgets(widgets, period);
      state = { ...state, widgets: res.data.widgets || {} };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async markRead(id) {
    try {
      await dashboardV2Api.markRead(id);
      state = {
        ...state,
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, read: true } : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  async markAllRead() {
    try {
      await dashboardV2Api.markAllRead();
      state = {
        ...state,
        notifications: state.notifications.map((n) => ({ ...n, read: true })),
        unreadCount: 0,
      };
    } catch {}
    subscribers.forEach((fn) => fn(state));
  },
  applyLiveUpdate(data) {
    if (data.type === "dashboard.updated" || data.type === "processing.batch.completed") {
      const period = state.period;
      if (period) {
        this.fetchOverview(period);
      }
    }
    if (data.type === "notification.created") {
      this.fetchNotifications();
    }
  },
};
