import { api } from "../api/client";

let subscribers = [];
let state = {
  summary: null,
  monthly: [],
  categories: [],
  recent: [],
  score: null,
  recommendations: [],
  loading: false,
  error: null,
};

export const dashboardStore = {
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
  async fetch() {
    state = { ...state, loading: true, error: null };
    subscribers.forEach((fn) => fn(state));
    try {
      const [summary, monthly, categories, recent, score, recommendations] =
        await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/monthly-spending"),
          api.get("/analytics/category-breakdown"),
          api.get("/analytics/recent-expenses"),
          api.get("/financial-health/score"),
          api.get("/recommendations"),
        ]);
      state = {
        summary: summary.data,
        monthly: monthly.data,
        categories: categories.data,
        recent: recent.data,
        score: score.data,
        recommendations: recommendations.data,
        loading: false,
        error: null,
      };
    } catch {
      state = {
        ...state,
        loading: false,
        error: "Could not load dashboard data.",
      };
    }
    subscribers.forEach((fn) => fn(state));
  },
};
