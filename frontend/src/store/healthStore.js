import { healthApi } from "../api/health";

class HealthStore {
  constructor() {
    this.current = null;
    this.history = null;
    this.trends = null;
    this.breakdown = null;
    this.recommendations = [];
    this.risk = null;
    this.loading = { current: false, history: false, trends: false, breakdown: false, recommendations: false, risk: false, calculate: false };
    this.errors = {};
    this._listeners = [];
  }

  subscribe(fn) { this._listeners.push(fn); return () => { this._listeners = this._listeners.filter((l) => l !== fn); }; }
  _notify() { this._listeners.forEach((fn) => fn(this)); }
  _set(key, val) { this[key] = val; this._notify(); }

  async calculate() {
    this.loading.calculate = true; this._notify();
    try { const res = await healthApi.calculate(); this._set("current", res.data); } catch (e) { this.errors.calculate = e; this._notify(); }
    finally { this.loading.calculate = false; this._notify(); }
  }

  async recalculate() {
    this.loading.calculate = true; this._notify();
    try { const res = await healthApi.recalculate(); this._set("current", res.data); } catch (e) { this.errors.calculate = e; this._notify(); }
    finally { this.loading.calculate = false; this._notify(); }
  }

  async fetchCurrent() {
    this.loading.current = true; this._notify();
    try { const res = await healthApi.getCurrent(); this._set("current", res.data); this.errors.current = null; } catch (e) { this.errors.current = e; }
    finally { this.loading.current = false; this._notify(); }
  }

  async fetchHistory(limit = 36) {
    this.loading.history = true; this._notify();
    try { const res = await healthApi.getHistory(limit); this._set("history", res.data); } catch (e) { this.errors.history = e; }
    finally { this.loading.history = false; this._notify(); }
  }

  async fetchTrends(months = 12) {
    this.loading.trends = true; this._notify();
    try { const res = await healthApi.getTrends(months); this._set("trends", res.data); } catch (e) { this.errors.trends = e; }
    finally { this.loading.trends = false; this._notify(); }
  }

  async fetchBreakdown() {
    this.loading.breakdown = true; this._notify();
    try { const res = await healthApi.getBreakdown(); this._set("breakdown", res.data); } catch (e) { this.errors.breakdown = e; }
    finally { this.loading.breakdown = false; this._notify(); }
  }

  async fetchRecommendations() {
    this.loading.recommendations = true; this._notify();
    try { const res = await healthApi.getRecommendations(); this._set("recommendations", res.data); } catch (e) { this.errors.recommendations = e; }
    finally { this.loading.recommendations = false; this._notify(); }
  }

  async fetchRisk() {
    this.loading.risk = true; this._notify();
    try { const res = await healthApi.getRisk(); this._set("risk", res.data); this.errors.risk = null; } catch (e) { this.errors.risk = e; }
    finally { this.loading.risk = false; this._notify(); }
  }

  async fetchAll() {
    await Promise.allSettled([
      this.fetchCurrent(), this.fetchHistory(), this.fetchTrends(),
      this.fetchBreakdown(), this.fetchRecommendations(), this.fetchRisk(),
    ]);
  }
}

export const healthStore = new HealthStore();
