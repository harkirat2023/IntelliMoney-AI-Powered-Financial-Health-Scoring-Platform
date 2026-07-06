import { AlertTriangle, Loader2 } from "lucide-react";

export function DisconnectDialog({ account, onConfirm, onCancel, loading }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl p-6 max-w-sm mx-4 w-full shadow-2xl">
        <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
          <AlertTriangle size={22} className="text-red-600" />
        </div>
        <h3 className="text-lg font-bold text-neutral-900 text-center mb-2">Disconnect Account?</h3>
        <p className="text-sm text-neutral-500 text-center mb-1">
          This will revoke access to <strong>{account?.bank_name}</strong> ({account?.masked_account_number}).
        </p>
        <p className="text-xs text-neutral-400 text-center mb-6">
          Transaction history already imported will be retained.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : null}
            Disconnect
          </button>
        </div>
      </div>
    </div>
  );
}
