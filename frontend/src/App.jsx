import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";
import DashboardLayout from "./layouts/DashboardLayout";
import Budgets from "./pages/Budgets";
import BudgetOptimizer from "./pages/BudgetOptimizer";
import Expenses from "./pages/Expenses";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Recurring from "./pages/Recurring";
import Anomaly from "./pages/Anomaly";
import Reports from "./pages/Reports";
import Subscriptions from "./pages/Subscriptions";
import Sync from "./pages/Sync";
import SyncHistory from "./pages/SyncHistory";
import SyncStatus from "./pages/SyncStatus";
import OverviewPage from "./dashboard/pages/OverviewPage";
import AnalyticsPage from "./dashboard/pages/AnalyticsPage";
import SpendingPage from "./dashboard/pages/SpendingPage";
import CashflowPage from "./dashboard/pages/CashflowPage";
import BudgetsPage from "./dashboard/pages/BudgetsPage";
import InsightsPage from "./dashboard/pages/InsightsPage";
import NotificationsPage from "./dashboard/pages/NotificationsPage";
import HealthLayout from "./layouts/HealthLayout";
import HealthOverviewPage from "./pages/health/HealthOverviewPage";
import HealthHistoryPage from "./pages/health/HealthHistoryPage";
import HealthTrendsPage from "./pages/health/HealthTrendsPage";
import HealthRecommendationsPage from "./pages/health/HealthRecommendationsPage";
import HealthRiskPage from "./pages/health/HealthRiskPage";
import BudgetIntelligenceLayout from "./layouts/BudgetIntelligenceLayout";
import CopilotLayout from "./layouts/CopilotLayout";
import CopilotChatPage from "./pages/copilot/CopilotChatPage";
import CopilotHistoryPage from "./pages/copilot/CopilotHistoryPage";
import CopilotHistoryDetailPage from "./pages/copilot/CopilotHistoryDetailPage";
import CopilotSettingsPage from "./pages/copilot/CopilotSettingsPage";
import GoalsLayout from "./layouts/GoalsLayout";
import GoalsOverviewPage from "./pages/goals/GoalsOverviewPage";
import CreateGoalPage from "./pages/goals/CreateGoalPage";
import GoalDetailPage from "./pages/goals/GoalDetailPage";
import GoalRecommendationsPage from "./pages/goals/GoalRecommendationsPage";
import GoalProgressPage from "./pages/goals/GoalProgressPage";
import GoalHistoryPage from "./pages/goals/GoalHistoryPage";
import ReceiptsLayout from "./layouts/ReceiptsLayout";
import ReceiptsOverviewPage from "./pages/receipts/ReceiptsOverviewPage";
import ReceiptUploadPage from "./pages/receipts/ReceiptUploadPage";
import ReceiptReviewPage from "./pages/receipts/ReceiptReviewPage";
import ReceiptHistoryPage from "./pages/receipts/ReceiptHistoryPage";
import BIOOverviewPage from "./pages/budgetIntelligence/BIOOverviewPage";
import BIRecommendationsPage from "./pages/budgetIntelligence/BIRecommendationsPage";
import BIOptimizationPage from "./pages/budgetIntelligence/BIOptimizationPage";
import BITrendsPage from "./pages/budgetIntelligence/BITrendsPage";
import BIOpportunitiesPage from "./pages/budgetIntelligence/BIOpportunitiesPage";

import { LandingLayout } from "./landing/layouts/LandingLayout";
import { HomePage } from "./landing/pages/HomePage";
import { FeaturesPage } from "./landing/pages/FeaturesPage";
import { AboutPage } from "./landing/pages/AboutPage";
import { ContactPage } from "./landing/pages/ContactPage";
import { PrivacyPage } from "./landing/pages/PrivacyPage";
import { TermsPage } from "./landing/pages/TermsPage";
import ConnectBank from "./pages/ConnectBank";
import ConsentPage from "./pages/ConsentPage";
import ConnectSuccess from "./pages/ConnectSuccess";
import ManageAccounts from "./pages/ManageAccounts";
import ImportPreference from "./pages/ImportPreference";
import ReviewPage from "./pages/ReviewPage";
import CompletePage from "./pages/CompletePage";

export default function App() {
  return (
    <Routes>
      <Route element={<LandingLayout />}>
        <Route index element={<HomePage />} />
        <Route path="features" element={<FeaturesPage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="contact" element={<ContactPage />} />
        <Route path="privacy" element={<PrivacyPage />} />
        <Route path="terms" element={<TermsPage />} />
        <Route path="connect-bank" element={<ConnectBank />} />
        <Route path="connect-bank/consent" element={<ConsentPage />} />
        <Route path="connect-bank/success" element={<ConnectSuccess />} />
        <Route path="connect-bank/manage" element={<ManageAccounts />} />
        <Route path="connect-bank/import-preference" element={<ImportPreference />} />
        <Route path="connect-bank/review" element={<ReviewPage />} />
        <Route path="connect-bank/complete" element={<CompletePage />} />
      </Route>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="expenses" element={<Expenses />} />
        <Route path="budgets" element={<Budgets />} />
        <Route path="budget-optimizer" element={<BudgetOptimizer />} />
        <Route path="reports" element={<Reports />} />
        <Route path="subscriptions" element={<Subscriptions />} />
        <Route path="recurring" element={<Recurring />} />
        <Route path="anomaly" element={<Anomaly />} />
        <Route path="bank-accounts" element={<ManageAccounts />} />
        <Route path="sync" element={<Sync />} />
        <Route path="sync/history" element={<SyncHistory />} />
        <Route path="sync/status" element={<SyncStatus />} />
        <Route path="dashboard" element={<DashboardLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="spending" element={<SpendingPage />} />
          <Route path="cashflow" element={<CashflowPage />} />
          <Route path="budgets" element={<BudgetsPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
        </Route>
        <Route path="health" element={<HealthLayout />}>
          <Route index element={<HealthOverviewPage />} />
          <Route path="history" element={<HealthHistoryPage />} />
          <Route path="trends" element={<HealthTrendsPage />} />
          <Route path="recommendations" element={<HealthRecommendationsPage />} />
          <Route path="risk" element={<HealthRiskPage />} />
        </Route>
        <Route path="budget-intelligence" element={<BudgetIntelligenceLayout />}>
          <Route index element={<BIOOverviewPage />} />
          <Route path="recommendations" element={<BIRecommendationsPage />} />
          <Route path="optimization" element={<BIOptimizationPage />} />
          <Route path="trends" element={<BITrendsPage />} />
          <Route path="opportunities" element={<BIOpportunitiesPage />} />
        </Route>
        <Route path="copilot" element={<CopilotLayout />}>
          <Route index element={<CopilotChatPage />} />
          <Route path="history" element={<CopilotHistoryPage />} />
          <Route path="history/:sessionId" element={<CopilotHistoryDetailPage />} />
          <Route path="settings" element={<CopilotSettingsPage />} />
        </Route>
        <Route path="goals" element={<GoalsLayout />}>
          <Route index element={<GoalsOverviewPage />} />
          <Route path="create" element={<CreateGoalPage />} />
          <Route path="recommendations" element={<GoalRecommendationsPage />} />
          <Route path="progress" element={<GoalProgressPage />} />
          <Route path="history" element={<GoalHistoryPage />} />
          <Route path=":goalId" element={<GoalDetailPage />} />
        </Route>
        <Route path="receipts" element={<ReceiptsLayout />}>
          <Route index element={<ReceiptsOverviewPage />} />
          <Route path="upload" element={<ReceiptUploadPage />} />
          <Route path="review" element={<ReceiptReviewPage />} />
          <Route path="history" element={<ReceiptHistoryPage />} />
        </Route>
      </Route>
      <Route path="*" element={<CatchAllRedirect />} />
    </Routes>
  );
}


function CatchAllRedirect() {
  const token = localStorage.getItem("intellimoney_token");
  return <Navigate to={token ? "/app" : "/"} replace />;
}
