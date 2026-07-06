import { goalsApi } from "../api/goals";

class GoalsStore {
  constructor() {
    this.goals = [];
    this.currentGoal = null;
    this.recommendations = [];
    this.progress = [];
    this.analysis = null;
    this.lastCreateResult = null;
    this.loading = { goals: false, current: false, recommendations: false, progress: false, create: false, analyze: false, recalculate: false };
    this.errors = {};
    this._listeners = [];
  }

  subscribe(fn) { this._listeners.push(fn); return () => { this._listeners = this._listeners.filter((l) => l !== fn); }; }
  _notify() { this._listeners.forEach((fn) => fn(this)); }
  _set(key, val) { this[key] = val; this._notify(); }

  async createGoal(data) {
    this.loading.create = true; this._notify();
    try {
      const res = await goalsApi.create(data);
      this._set("lastCreateResult", res.data);
      this._set("goals", [res.data.goal, ...this.goals]);
      this.errors.create = null;
      return res.data;
    } catch (e) {
      this.errors.create = e;
      throw e;
    } finally {
      this.loading.create = false;
      this._notify();
    }
  }

  async updateGoal(goalId, data) {
    try {
      const res = await goalsApi.update(goalId, data);
      this._set("goals", this.goals.map((g) => g.id === goalId ? res.data : g));
      if (this.currentGoal?.id === goalId) this._set("currentGoal", res.data);
    } catch (e) {
      this.errors.current = e;
    }
  }

  async deleteGoal(goalId) {
    try {
      await goalsApi.delete(goalId);
      this._set("goals", this.goals.filter((g) => g.id !== goalId));
      if (this.currentGoal?.id === goalId) this._set("currentGoal", null);
    } catch (e) {
      this.errors.current = e;
    }
  }

  async fetchGoals(status) {
    this.loading.goals = true; this._notify();
    try {
      const res = await goalsApi.getAll(status);
      this._set("goals", res.data);
      this.errors.goals = null;
    } catch (e) {
      this.errors.goals = e;
    } finally {
      this.loading.goals = false;
      this._notify();
    }
  }

  async fetchGoal(goalId) {
    this.loading.current = true; this._notify();
    try {
      const res = await goalsApi.getById(goalId);
      this._set("currentGoal", res.data);
      this.errors.current = null;
    } catch (e) {
      this.errors.current = e;
    } finally {
      this.loading.current = false;
      this._notify();
    }
  }

  async analyze(data) {
    this.loading.analyze = true; this._notify();
    try {
      const res = await goalsApi.analyze(data);
      this._set("analysis", res.data);
      this.errors.analyze = null;
      return res.data;
    } catch (e) {
      this.errors.analyze = e;
      throw e;
    } finally {
      this.loading.analyze = false;
      this._notify();
    }
  }

  async recalculate() {
    this.loading.recalculate = true; this._notify();
    try {
      const res = await goalsApi.recalculate();
      this.errors.recalculate = null;
      return res.data;
    } catch (e) {
      this.errors.recalculate = e;
    } finally {
      this.loading.recalculate = false;
      this._notify();
    }
  }

  async fetchRecommendations() {
    this.loading.recommendations = true; this._notify();
    try {
      const res = await goalsApi.getRecommendations();
      this._set("recommendations", res.data);
      this.errors.recommendations = null;
    } catch (e) {
      this.errors.recommendations = e;
    } finally {
      this.loading.recommendations = false;
      this._notify();
    }
  }

  async fetchProgress() {
    this.loading.progress = true; this._notify();
    try {
      const res = await goalsApi.getProgress();
      this._set("progress", res.data);
      this.errors.progress = null;
    } catch (e) {
      this.errors.progress = e;
    } finally {
      this.loading.progress = false;
      this._notify();
    }
  }

  async fetchAll() {
    await Promise.allSettled([
      this.fetchGoals(), this.fetchRecommendations(), this.fetchProgress(),
    ]);
  }
}

export const goalsStore = new GoalsStore();
