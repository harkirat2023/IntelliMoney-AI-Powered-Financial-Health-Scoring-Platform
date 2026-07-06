import { useEffect, useState } from "react";
import { copilotStore } from "../../store/copilotStore";
import { Settings as SettingsIcon, Loader } from "lucide-react";

export default function CopilotSettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    copilotStore.fetchSettings().then(() => {
      setSettings(copilotStore.settings);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="copilot-settings-page">
      <div className="page-header">
        <h2><SettingsIcon size={20} /> Copilot Settings</h2>
      </div>
      <div className="settings-card">
        <div className="setting-row">
          <span className="setting-label">Model</span>
          <span className="setting-value">{settings?.model || "gpt-4o"}</span>
        </div>
        <div className="setting-row">
          <span className="setting-label">Temperature</span>
          <span className="setting-value">{settings?.temperature || 0.3}</span>
        </div>
        <div className="setting-row">
          <span className="setting-label">Max Tokens</span>
          <span className="setting-value">{settings?.max_tokens || 1024}</span>
        </div>
      </div>
      <p className="settings-note">Settings are configured server-side via environment variables.</p>
    </div>
  );
}
