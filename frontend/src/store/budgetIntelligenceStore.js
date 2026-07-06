import { budgetIntelligenceApi } from "../api/budgetIntelligence";

class BudgetIntelligenceStore {
  constructor() {
    this.current = null;
    this.recommendations = [];
    this.optimization = null;
    this.trends = null;
    this.risk = null;
    this.opportunities = [];
    this.loading = { current: false, recommendations: false, optimization: false, trends: false, risk: false, opportunities: false, generate: false };
    this.errors = {};
    this._listeners = [];
  }

  subscribe(fn) { this._listeners.push(fn); return () => { this._listeners = this._listeners.filter((l) => l !== fn); }; }
  _notify() { this._listeners.forEach((fn) => fn(this)); }
  _set(key, val) { this[key] = val; this._notify(); }

  async generate() {
    this.loading.generate = true; this._notify();
    try { const res = await budgetIntelligenceApi.generate(); this._set("current", { period: res.data.period, budget_score: res.data.budget_score }); this.errors.generate = null; }
    catch (e) { this.errors.generate = e; }
    finally { this.loading.generate = false; this._notify(); }
  }

  async recalculate() {
    this.loading.generate = true; this._notify();
    try { const res = await budgetIntelligenceApi.recalculate(); this._set("current", { period: res.data.period, budget_score: res.data.budget_score }); }
    catch (e) { this.errors.generate = e; }
    finally { this.loading.generate = false; this._notify(); }
  }

  async fetchCurrent() {
    this.loading.current = true; this._notify();
    try { const res = await budgetIntelligenceApi.getCurrent(); this._set("current", res.data); this.errors.current = null; }
    catch (e) { this.errors.current = e; }
    finally { this.loading.current = false; this._notify(); }
  }

  async fetchRecommendations() {
    this.loading.recommendations = true; this._notify();
    try { const res = await budgetIntelligenceApi.getRecommendations(); this._set("recommendations", res.data); this.errors.recommendations = null; }
    catch (e) { this.errors.recommendations = e; }
    finally { this.loading.recommendations = false; this._notify(); }
  }

  async fetchOptimization() {
    this.loading.optimization = true; this._notify();
    try { const res = await budgetIntelligenceApi.getOptimization(); this._set("optimization", res.data); this.errors.optimization = null; }
    catch (e) { this.errors.optimization = e; }
    finally { this.loading.optimization = false; this._notify(); }
  }

  async fetchTrends() {
    this.loading.trends = true; this._notify();
    try { const res = await budgetIntelligenceApi.getTrends(); this._set("trends", res.data); this.errors.trends = null; }
    catch (e) { this.errors.trends = e; }
    finally { this.loading.trends = false; this._notify(); }
  }

  async fetchRisk() {
    this.loading.risk = true; this._notify();
    try { const res = await budgetIntelligenceApi.getRisk(); this._set("risk", res.data); this.errors.risk = null; }
    catch (e) { this.errors.risk = e; }
    finally { this.loading.risk = false; this._notify(); }
  }

  async fetchOpportunities() {
    this.loading.opportunities = true; this._notify();
    try { const res = await budgetIntelligenceApi.getOpportunities(); this._set("opportunities", res.data); this.errors.opportunities = null; }
    catch (e) { this.errors.opportunities = e; }
    finally { this.loading.opportunities = false; this._notify(); }
  }

  async fetchAll() {
    await Promise.allSettled([
      this.fetchCurrent(), this.fetchRecommendations(), this.fetchOptimization(),
      this.fetchTrends(), this.fetchRisk(), this.fetchOpportunities(),
    ]);
  }
}

export const budgetIntelligenceStore = new BudgetIntelligenceStore();
