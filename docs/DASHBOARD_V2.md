# Dashboard V2

**Phase:** 8 | **Version:** 1.8

## Overview

Dashboard V2 is the primary financial overview and analytics layer of IntelliMoney. It aggregates data across all financial modules into a unified interface, exposing summary metrics, spending breakdowns, cashflow trends, budget status, and real-time notifications. The module is backed by three backend services and delivers 11 REST endpoints consumed by 7 frontend pages, 4 chart components, and 4 widget components.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                     │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Overview  │ │Analytics │ │Spending  │ │Cashflow  │ │Budgets   │  │
│  │Page      │ │Page      │ │Page      │ │Page      │ │Page      │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│  ┌────┴────────────┴────────────┴────────────┴────────────┴─────┐   │
│  │              DashboardLayout (7-item sidebar nav)            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐       │
│  │Spending  │ │CategoryPie   │ │Cashflow  │ │Trends        │       │
│  │Chart     │ │Chart         │ │Chart     │ │Chart         │       │
│  └──────────┘ └──────────────┘ └──────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────────┐  │
│  │Spending      │ │Budget      │ │Health      │ │Recurring      │  │
│  │Widget        │ │Widget      │ │Widget      │ │Widget         │  │
│  └──────────────┘ └────────────┘ └────────────┘ └───────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │          dashboardStore (Observer / Event Mapping)            │   │
│  └────────────────────┬─────────────────────────────────────────┘   │
├───────────────────────┼─────────────────────────────────────────────┤
│                 API   │   (12 methods)                              │
├───────────────────────┼─────────────────────────────────────────────┤
│                  BACKEND                                            │
│                                                                      │
│  ┌──────────────┐ ┌──────────────────┐ ┌────────────────┐          │
│  │Dashboard     │ │Notification      │ │Widget           │          │
│  │Service       │ │Service           │ │Service          │          │
│  │(22 metrics)  │ │(read/unread)     │ │(4 types)        │          │
│  └──────┬───────┘ └────────┬─────────┘ └───────┬────────┘          │
│         │                  │                    │                    │
│  ┌──────┴──────────────────┴────────────────────┴───────────────┐  │
│  │                DashboardGateway (7 event types)              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌─────────────┐  ┌────────────────┐  ┌───────────────────────┐   │
│  │dashboard    │  │dashboard_v2    │  │dashboard_v2_extended  │   │
│  │services.py  │  │routes.py       │  │routes.py              │   │
│  │schemas.py   │  │                │  │                       │   │
│  └─────────────┘  └────────────────┘  └───────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models & Schemas

Defined in `backend/app/dashboard/schemas.py` — Pydantic models for all request/response payloads including summary, spending, cashflow, monthly, overview, analytics, budgets, insights, notifications, activity, and widgets.

### Services

| Service | File | Responsibility |
|---|---|---|
| **DashboardService** | `backend/app/dashboard/services.py` | Computes 22 aggregated metrics across spending, income, budgets, and trends |
| **NotificationService** | `backend/app/dashboard/services.py` | Manages notification lifecycle — create, list, mark read, unread count |
| **WidgetService** | `backend/app/dashboard/services.py` | Drives 4 widget types: Spending, Budget, Health, Recurring |

**DashboardGateway** subscribes to 7 event types and publishes state changes to the frontend via the observer-backed `dashboardStore`.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Aggregated financial summary |
| GET | `/dashboard/spending` | Spending breakdown by category |
| GET | `/dashboard/cashflow` | Income vs expense cashflow |
| GET | `/dashboard/monthly` | Monthly trends |
| GET | `/dashboard/overview` | High-level overview |
| GET | `/dashboard/analytics` | Deep analytics |
| GET | `/dashboard/budgets` | Budget status summary |
| GET | `/dashboard/insights` | Generated insights |
| GET | `/dashboard/notifications` | List notifications |
| GET | `/dashboard/notifications/unread-count` | Unread notification count |
| GET | `/dashboard/activity` | Recent activity feed |
| GET | `/dashboard/widgets` | Widget data |
| POST | `/dashboard/notifications/{id}/read` | Mark notification read |
| POST | `/dashboard/notifications/read-all` | Mark all notifications read |

### API Client

The frontend API client exposes 12 methods, one per dashboard endpoint.

## Frontend Pages & Layout

### Pages (7)

| Page | Route / Description |
|---|---|
| **OverviewPage** | High-level summary tiles |
| **AnalyticsPage** | Deep-dive data analytics |
| **SpendingPage** | Spending by category |
| **CashflowPage** | Income vs expenses |
| **BudgetsPage** | Budget tracking |
| **InsightsPage** | AI-generated insights |
| **NotificationsPage** | Notification center |

### Layout

**DashboardLayout** provides a 7-item sidebar navigation across all dashboard pages.

### Chart Components (4)

| Component | Purpose |
|---|---|
| **SpendingChart** | Spending trends over time |
| **CategoryPieChart** | Category distribution |
| **CashflowChart** | Income / expense comparison |
| **TrendsChart** | Aggregate financial trends |

### Widget Components (4)

| Component | Type |
|---|---|
| **SpendingWidget** | Spending snapshot |
| **BudgetWidget** | Budget progress |
| **HealthWidget** | Financial health score |
| **RecurringWidget** | Recurring transactions |

### Store

**dashboardStore** is an observer-based state store that maps incoming events to local state updates, driving reactive UI rendering.

## Event Types

The DashboardGateway subscribes to these 7 event types:

- `transaction.created`
- `transaction.updated`
- `transaction.deleted`
- `budget.updated`
- `goal.progress_updated`
- `notification.created`
- `health.calculated`

## Configuration

No module-specific configuration. Relies on global IntelliMoney settings.

## Status & Version

| Property | Value |
|---|---|
| Phase | 8 |
| Version | 1.8 |
| Backend files | `dashboard/services.py`, `schemas.py` |
| Route files | `api/routes/dashboard_v2.py`, `dashboard_v2_extended.py` |
| Service count | 3 |
| Endpoints | 14 |
| Frontend pages | 7 |
| Chart components | 4 |
| Widget components | 4 |
