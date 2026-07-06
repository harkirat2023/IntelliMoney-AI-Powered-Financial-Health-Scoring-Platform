import { receiptsApi } from "../api/receipts";

class ReceiptsStore {
  constructor() {
    this.receipts = [];
    this.currentReceipt = null;
    this.uploadResult = null;
    this.processResult = null;
    this.loading = { list: false, current: false, upload: false, process: false, confirm: false };
    this.errors = {};
    this._listeners = [];
  }

  subscribe(fn) { this._listeners.push(fn); return () => { this._listeners = this._listeners.filter((l) => l !== fn); }; }
  _notify() { this._listeners.forEach((fn) => fn(this)); }
  _set(key, val) { this[key] = val; this._notify(); }

  async upload(file) {
    this.loading.upload = true; this._notify();
    try {
      const res = await receiptsApi.upload(file);
      this._set("uploadResult", res.data);
      this._set("receipts", [res.data.receipt, ...this.receipts]);
      this.errors.upload = null;
      return res.data;
    } catch (e) {
      this.errors.upload = e;
      throw e;
    } finally {
      this.loading.upload = false;
      this._notify();
    }
  }

  async process(receiptId) {
    this.loading.process = true; this._notify();
    try {
      const res = await receiptsApi.process(receiptId);
      this._set("processResult", res.data);
      this._set("currentReceipt", res.data.receipt);
      this.errors.process = null;
      return res.data;
    } catch (e) {
      this.errors.process = e;
      throw e;
    } finally {
      this.loading.process = false;
      this._notify();
    }
  }

  async confirm(receiptId) {
    this.loading.confirm = true; this._notify();
    try {
      const res = await receiptsApi.confirm(receiptId);
      this._set("processResult", res.data);
      this._set("currentReceipt", res.data.receipt);
      this.errors.process = null;
      return res.data;
    } catch (e) {
      this.errors.process = e;
      throw e;
    } finally {
      this.loading.confirm = false;
      this._notify();
    }
  }

  async fetchReceipts(status) {
    this.loading.list = true; this._notify();
    try {
      const res = await receiptsApi.getAll(status);
      this._set("receipts", res.data.receipts);
      this.errors.list = null;
    } catch (e) {
      this.errors.list = e;
    } finally {
      this.loading.list = false;
      this._notify();
    }
  }

  async fetchReceipt(receiptId) {
    this.loading.current = true; this._notify();
    try {
      const res = await receiptsApi.getById(receiptId);
      this._set("currentReceipt", res.data);
      this.errors.current = null;
    } catch (e) {
      this.errors.current = e;
    } finally {
      this.loading.current = false;
      this._notify();
    }
  }

  async updateReceipt(receiptId, data) {
    try {
      const res = await receiptsApi.update(receiptId, data);
      this._set("currentReceipt", res.data);
      this._set("receipts", this.receipts.map((r) => r.id === receiptId ? res.data : r));
    } catch (e) {
      this.errors.current = e;
    }
  }

  async deleteReceipt(receiptId) {
    try {
      await receiptsApi.delete(receiptId);
      this._set("receipts", this.receipts.filter((r) => r.id !== receiptId));
      if (this.currentReceipt?.id === receiptId) this._set("currentReceipt", null);
    } catch (e) {
      this.errors.list = e;
    }
  }
}

export const receiptsStore = new ReceiptsStore();
