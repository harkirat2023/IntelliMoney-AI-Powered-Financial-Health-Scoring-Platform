let subscribers = [];
let state = {
  alerts: [],
  loading: false,
  unreadCount: 0,
};

export const notificationStore = {
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
  setAlerts(alerts) {
    const unreadCount = alerts.filter((a) => !a.read).length;
    state = { alerts, loading: false, unreadCount };
    subscribers.forEach((fn) => fn(state));
  },
  setLoading(loading) {
    state = { ...state, loading };
    subscribers.forEach((fn) => fn(state));
  },
};
