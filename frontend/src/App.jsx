import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import PageLoader from "./components/PageLoader";

const AppLayout = lazy(() => import("./layouts/AppLayout"));
const DashboardLayout = lazy(() => import("./layouts/DashboardLayout"));
const Budgets = lazy(() => import("./pages/Budgets"));
const BudgetOptimizer = lazy(() => import("./pages/BudgetOptimizer"));
const Expenses = lazy(() => import("./pages/Expenses"));
const Login = lazy(() => import("./pages/Login"));
const Register = lazy(() => import("./pages/Register"));
const Recurring = lazy(() => import("./pages/Recurring"));
const Anomaly = lazy(() => import("./pages/Anomaly"));
const Reports = lazy(() => import("./pages/Reports"));
const Subscriptions = lazy(() => import("./pages/Subscriptions"));
const Sync = lazy(() => import("./pages/Sync"));
const SyncHistory = lazy(() => import("./pages/SyncHistory"));
const SyncStatus = lazy(() => import("./pages/SyncStatus"));
const OverviewPage = lazy(() => import("./dashboard/pages/OverviewPage"));
const AnalyticsPage = lazy(() => import("./dashboard/pages/AnalyticsPage"));
const SpendingPage = lazy(() => import("./dashboard/pages/SpendingPage"));
const CashflowPage = lazy(() => import("./dashboard/pages/CashflowPage"));
const BudgetsPage = lazy(() => import("./dashboard/pages/BudgetsPage"));
const InsightsPage = lazy(() => import("./dashboard/pages/InsightsPage"));
const NotificationsPage = lazy(() => import("./dashboard/pages/NotificationsPage"));
const HealthLayout = lazy(() => import("./layouts/HealthLayout"));
const HealthOverviewPage = lazy(() => import("./pages/health/HealthOverviewPage"));
const HealthHistoryPage = lazy(() => import("./pages/health/HealthHistoryPage"));
const HealthTrendsPage = lazy(() => import("./pages/health/HealthTrendsPage"));
const HealthRecommendationsPage = lazy(() => import("./pages/health/HealthRecommendationsPage"));
const HealthRiskPage = lazy(() => import("./pages/health/HealthRiskPage"));
const BudgetIntelligenceLayout = lazy(() => import("./layouts/BudgetIntelligenceLayout"));
const CopilotLayout = lazy(() => import("./layouts/CopilotLayout"));
const CopilotChatPage = lazy(() => import("./pages/copilot/CopilotChatPage"));
const CopilotHistoryPage = lazy(() => import("./pages/copilot/CopilotHistoryPage"));
const CopilotHistoryDetailPage = lazy(() => import("./pages/copilot/CopilotHistoryDetailPage"));
const CopilotSettingsPage = lazy(() => import("./pages/copilot/CopilotSettingsPage"));
const GoalsLayout = lazy(() => import("./layouts/GoalsLayout"));
const GoalsOverviewPage = lazy(() => import("./pages/goals/GoalsOverviewPage"));
const CreateGoalPage = lazy(() => import("./pages/goals/CreateGoalPage"));
const GoalDetailPage = lazy(() => import("./pages/goals/GoalDetailPage"));
const GoalRecommendationsPage = lazy(() => import("./pages/goals/GoalRecommendationsPage"));
const GoalProgressPage = lazy(() => import("./pages/goals/GoalProgressPage"));
const GoalHistoryPage = lazy(() => import("./pages/goals/GoalHistoryPage"));
const ReceiptsLayout = lazy(() => import("./layouts/ReceiptsLayout"));
const ReceiptsOverviewPage = lazy(() => import("./pages/receipts/ReceiptsOverviewPage"));
const ReceiptUploadPage = lazy(() => import("./pages/receipts/ReceiptUploadPage"));
const ReceiptReviewPage = lazy(() => import("./pages/receipts/ReceiptReviewPage"));
const ReceiptHistoryPage = lazy(() => import("./pages/receipts/ReceiptHistoryPage"));
const BIOOverviewPage = lazy(() => import("./pages/budgetIntelligence/BIOOverviewPage"));
const BIRecommendationsPage = lazy(() => import("./pages/budgetIntelligence/BIRecommendationsPage"));
const BIOptimizationPage = lazy(() => import("./pages/budgetIntelligence/BIOptimizationPage"));
const BITrendsPage = lazy(() => import("./pages/budgetIntelligence/BITrendsPage"));
const BIOpportunitiesPage = lazy(() => import("./pages/budgetIntelligence/BIOpportunitiesPage"));

import { LandingLayout } from "./landing/layouts/LandingLayout";
const HomePageLazy = lazy(() => import("./landing/pages/HomePage").then(m => ({ default: m.HomePage })));
const FeaturesPageLazy = lazy(() => import("./landing/pages/FeaturesPage").then(m => ({ default: m.FeaturesPage })));
const AboutPageLazy = lazy(() => import("./landing/pages/AboutPage").then(m => ({ default: m.AboutPage })));
const ContactPageLazy = lazy(() => import("./landing/pages/ContactPage").then(m => ({ default: m.ContactPage })));
const PrivacyPageLazy = lazy(() => import("./landing/pages/PrivacyPage").then(m => ({ default: m.PrivacyPage })));
const TermsPageLazy = lazy(() => import("./landing/pages/TermsPage").then(m => ({ default: m.TermsPage })));
const ConnectBank = lazy(() => import("./pages/ConnectBank"));
const ConsentPage = lazy(() => import("./pages/ConsentPage"));
const ConnectSuccess = lazy(() => import("./pages/ConnectSuccess"));
const ManageAccounts = lazy(() => import("./pages/ManageAccounts"));
const ImportPreference = lazy(() => import("./pages/ImportPreference"));
const ReviewPage = lazy(() => import("./pages/ReviewPage"));
const CompletePage = lazy(() => import("./pages/CompletePage"));

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<LandingLayout />}>
          <Route index element={<Suspense fallback={<PageLoader />}><HomePageLazy /></Suspense>} />
          <Route path="features" element={<Suspense fallback={<PageLoader />}><FeaturesPageLazy /></Suspense>} />
          <Route path="about" element={<Suspense fallback={<PageLoader />}><AboutPageLazy /></Suspense>} />
          <Route path="contact" element={<Suspense fallback={<PageLoader />}><ContactPageLazy /></Suspense>} />
          <Route path="privacy" element={<Suspense fallback={<PageLoader />}><PrivacyPageLazy /></Suspense>} />
          <Route path="terms" element={<Suspense fallback={<PageLoader />}><TermsPageLazy /></Suspense>} />
          <Route path="connect-bank" element={<Suspense fallback={<PageLoader />}><ConnectBank /></Suspense>} />
          <Route path="connect-bank/consent" element={<Suspense fallback={<PageLoader />}><ConsentPage /></Suspense>} />
          <Route path="connect-bank/success" element={<Suspense fallback={<PageLoader />}><ConnectSuccess /></Suspense>} />
          <Route path="connect-bank/manage" element={<Suspense fallback={<PageLoader />}><ManageAccounts /></Suspense>} />
          <Route path="connect-bank/import-preference" element={<Suspense fallback={<PageLoader />}><ImportPreference /></Suspense>} />
          <Route path="connect-bank/review" element={<Suspense fallback={<PageLoader />}><ReviewPage /></Suspense>} />
          <Route path="connect-bank/complete" element={<Suspense fallback={<PageLoader />}><CompletePage /></Suspense>} />
        </Route>
        <Route path="/login" element={<Suspense fallback={<PageLoader />}><Login /></Suspense>} />
        <Route path="/register" element={<Suspense fallback={<PageLoader />}><Register /></Suspense>} />
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <Suspense fallback={<PageLoader />}>
                <AppLayout />
              </Suspense>
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="expenses" element={<Suspense fallback={<PageLoader />}><Expenses /></Suspense>} />
          <Route path="budgets" element={<Suspense fallback={<PageLoader />}><Budgets /></Suspense>} />
          <Route path="budget-optimizer" element={<Suspense fallback={<PageLoader />}><BudgetOptimizer /></Suspense>} />
          <Route path="reports" element={<Suspense fallback={<PageLoader />}><Reports /></Suspense>} />
          <Route path="subscriptions" element={<Suspense fallback={<PageLoader />}><Subscriptions /></Suspense>} />
          <Route path="recurring" element={<Suspense fallback={<PageLoader />}><Recurring /></Suspense>} />
          <Route path="anomaly" element={<Suspense fallback={<PageLoader />}><Anomaly /></Suspense>} />
          <Route path="bank-accounts" element={<Suspense fallback={<PageLoader />}><ManageAccounts /></Suspense>} />
          <Route path="sync" element={<Suspense fallback={<PageLoader />}><Sync /></Suspense>} />
          <Route path="sync/history" element={<Suspense fallback={<PageLoader />}><SyncHistory /></Suspense>} />
          <Route path="sync/status" element={<Suspense fallback={<PageLoader />}><SyncStatus /></Suspense>} />
          <Route path="dashboard" element={<Suspense fallback={<PageLoader />}><DashboardLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><OverviewPage /></Suspense>} />
            <Route path="overview" element={<Suspense fallback={<PageLoader />}><OverviewPage /></Suspense>} />
            <Route path="analytics" element={<Suspense fallback={<PageLoader />}><AnalyticsPage /></Suspense>} />
            <Route path="spending" element={<Suspense fallback={<PageLoader />}><SpendingPage /></Suspense>} />
            <Route path="cashflow" element={<Suspense fallback={<PageLoader />}><CashflowPage /></Suspense>} />
            <Route path="budgets" element={<Suspense fallback={<PageLoader />}><BudgetsPage /></Suspense>} />
            <Route path="insights" element={<Suspense fallback={<PageLoader />}><InsightsPage /></Suspense>} />
            <Route path="notifications" element={<Suspense fallback={<PageLoader />}><NotificationsPage /></Suspense>} />
          </Route>
          <Route path="health" element={<Suspense fallback={<PageLoader />}><HealthLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><HealthOverviewPage /></Suspense>} />
            <Route path="history" element={<Suspense fallback={<PageLoader />}><HealthHistoryPage /></Suspense>} />
            <Route path="trends" element={<Suspense fallback={<PageLoader />}><HealthTrendsPage /></Suspense>} />
            <Route path="recommendations" element={<Suspense fallback={<PageLoader />}><HealthRecommendationsPage /></Suspense>} />
            <Route path="risk" element={<Suspense fallback={<PageLoader />}><HealthRiskPage /></Suspense>} />
          </Route>
          <Route path="budget-intelligence" element={<Suspense fallback={<PageLoader />}><BudgetIntelligenceLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><BIOOverviewPage /></Suspense>} />
            <Route path="recommendations" element={<Suspense fallback={<PageLoader />}><BIRecommendationsPage /></Suspense>} />
            <Route path="optimization" element={<Suspense fallback={<PageLoader />}><BIOptimizationPage /></Suspense>} />
            <Route path="trends" element={<Suspense fallback={<PageLoader />}><BITrendsPage /></Suspense>} />
            <Route path="opportunities" element={<Suspense fallback={<PageLoader />}><BIOpportunitiesPage /></Suspense>} />
          </Route>
          <Route path="copilot" element={<Suspense fallback={<PageLoader />}><CopilotLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><CopilotChatPage /></Suspense>} />
            <Route path="history" element={<Suspense fallback={<PageLoader />}><CopilotHistoryPage /></Suspense>} />
            <Route path="history/:sessionId" element={<Suspense fallback={<PageLoader />}><CopilotHistoryDetailPage /></Suspense>} />
            <Route path="settings" element={<Suspense fallback={<PageLoader />}><CopilotSettingsPage /></Suspense>} />
          </Route>
          <Route path="goals" element={<Suspense fallback={<PageLoader />}><GoalsLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><GoalsOverviewPage /></Suspense>} />
            <Route path="create" element={<Suspense fallback={<PageLoader />}><CreateGoalPage /></Suspense>} />
            <Route path="recommendations" element={<Suspense fallback={<PageLoader />}><GoalRecommendationsPage /></Suspense>} />
            <Route path="progress" element={<Suspense fallback={<PageLoader />}><GoalProgressPage /></Suspense>} />
            <Route path="history" element={<Suspense fallback={<PageLoader />}><GoalHistoryPage /></Suspense>} />
            <Route path=":goalId" element={<Suspense fallback={<PageLoader />}><GoalDetailPage /></Suspense>} />
          </Route>
          <Route path="receipts" element={<Suspense fallback={<PageLoader />}><ReceiptsLayout /></Suspense>}>
            <Route index element={<Suspense fallback={<PageLoader />}><ReceiptsOverviewPage /></Suspense>} />
            <Route path="upload" element={<Suspense fallback={<PageLoader />}><ReceiptUploadPage /></Suspense>} />
            <Route path="review" element={<Suspense fallback={<PageLoader />}><ReceiptReviewPage /></Suspense>} />
            <Route path="history" element={<Suspense fallback={<PageLoader />}><ReceiptHistoryPage /></Suspense>} />
          </Route>
        </Route>
        <Route path="*" element={<CatchAllRedirect />} />
      </Routes>
    </Suspense>
  );
}

function CatchAllRedirect() {
  const token = localStorage.getItem("intellimoney_token");
  return <Navigate to={token ? "/app" : "/"} replace />;
}