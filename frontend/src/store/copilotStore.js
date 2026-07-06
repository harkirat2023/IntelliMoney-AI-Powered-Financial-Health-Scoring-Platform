import { copilotApi } from "../api/copilot";

class CopilotStore {
  constructor() {
    this.sessions = [];
    this.currentSessionId = null;
    this.messages = [];
    this.suggestions = [];
    this.settings = null;
    this.loading = { chat: false, sessions: false, history: false, suggestions: false };
    this.errors = {};
    this._listeners = [];
  }

  subscribe(fn) { this._listeners.push(fn); return () => { this._listeners = this._listeners.filter(l => l !== fn); }; }
  _notify() { this._listeners.forEach(fn => fn(this)); }
  _set(key, val) { this[key] = val; this._notify(); }

  async sendMessage(message, sessionId) {
    this.loading.chat = true; this._notify();
    try {
      const res = await copilotApi.chat({ session_id: sessionId, message });
      this._set("currentSessionId", res.data.session_id);
      return res.data;
    } catch (e) {
      this.errors.chat = e;
      throw e;
    } finally {
      this.loading.chat = false;
      this._notify();
    }
  }

  async fetchSessions() {
    this.loading.sessions = true; this._notify();
    try {
      const res = await copilotApi.getSessions();
      this._set("sessions", res.data);
      this.errors.sessions = null;
    } catch (e) {
      this.errors.sessions = e;
    } finally {
      this.loading.sessions = false;
      this._notify();
    }
  }

  async fetchHistory(sessionId) {
    this.loading.history = true; this._notify();
    try {
      const res = await copilotApi.getSessionHistory(sessionId);
      const { messages } = res.data;
      this._set("messages", messages);
      this._set("currentSessionId", sessionId);
      this.errors.history = null;
    } catch (e) {
      this.errors.history = e;
    } finally {
      this.loading.history = false;
      this._notify();
    }
  }

  async deleteAll() {
    try {
      await copilotApi.deleteAllSessions();
      this._set("sessions", []);
      this._set("messages", []);
      this._set("currentSessionId", null);
    } catch (e) {
      this.errors.sessions = e;
    }
  }

  async fetchSuggestions() {
    this.loading.suggestions = true; this._notify();
    try {
      const res = await copilotApi.getSuggestions();
      this._set("suggestions", res.data.suggestions);
      this.errors.suggestions = null;
    } catch (e) {
      this.errors.suggestions = e;
    } finally {
      this.loading.suggestions = false;
      this._notify();
    }
  }

  async fetchSettings() {
    try {
      const res = await copilotApi.getSettings();
      this._set("settings", res.data);
    } catch (e) {
      this.errors.settings = e;
    }
  }

  clearMessages() {
    this._set("messages", []);
  }
}

export const copilotStore = new CopilotStore();
