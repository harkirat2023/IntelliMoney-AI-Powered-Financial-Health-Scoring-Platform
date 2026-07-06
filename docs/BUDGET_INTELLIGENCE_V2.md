# Budget Intelligence V2

**Phase:** 10 | **Version:** 1.10

## Overview

Budget Intelligence V2 brings AI-driven budget management to IntelliMoney. It generates smart budgets based on historical spending patterns, forecasts future trends, identifies budget risks, recommends optimizations, and surfaces savings opportunities across 6 types. The module comprises 5 models, 5 repositories, 8 services, and 8 REST endpoints consumed by 5 frontend pages, backed by 9/9 integration tests.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND                                   │
│                                                                     │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────────────┐      │
│  │BIOOverview   │ │BIRecommendations │ │BIOptimization       │      │
│  │Page          │ │Page            │ │Page                 │      │
│  └──────┬───────┘ └───────┬────────┘ └─────────┬────────────┘      │
│         │                 │                    │                    │
│  ┌──────┴─────────────────┴────────────────────┴───────────────┐  │
│  │          BudgetIntelligenceLayout (5-item sidebar nav)       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐ ┌────────────────────┐                           │
│  │BITrends      │ │BIOpportunities     │                           │
│  │Page          │ │Page                │                           │
│  └──────────────┘ └────────────────────┘                           │
├────────────────────┼────────────────────────────────────────────────┤
│                API │ 8 routes                                      │
├────────────────────┼────────────────────────────────────────────────┤
│                    BACKEND                                         │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                       Services                              │   │
│  │  ┌─────────────────┐ ┌────────────────┐ ┌──────────────┐  │   │
│  │  │SmartBudget      │ │CategoryTrend   │ │BudgetForecast│  │   │
│  │  │Service          │ │Service         │ │Service       │  │   │
│  │  └─────────────────┘ └────────────────┘ └──────────────┘  │   │
│  │  ┌─────────────────┐ ┌────────────────┐ ┌──────────────┐  │   │
│  │  │BudgetRisk       │ │BudgetRecommend-│ │BudgetOptimi- │  │   │
│  │  │Service          │ │ationService    │ │zationService │  │   │
│  │  │                 │ │(3 rec types)   │ │              │  │   │
│  │  └─────────────────┘ └────────────────┘ └──────────────┘  │   │
│  │  ┌─────────────────┐ ┌──────────────────────────────────┐ │   │
│  │  │SavingsOpportunity│ │    BudgetIntelligenceService     │ │   │
│  │  │Service (6 types) │ │    (orchestrator)                │ │   │
│  │  └─────────────────┘ └──────────────────────────────────┘ │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │BudgetIntell│ │BudgetRecom-  │ │BudgetPred- │ │BudgetRisk    │  │
│  │igence Repo │ │mendation Repo│ │iction Repo │ │Repo          │  │
│  └────────────┘ └──────────────┘ └────────────┘ └──────────────┘  │
│  ┌────────────────┐                                                │
│  │SavingsOpportun-│                                                │
│  │ity Repo        │                                                │
│  └────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models (5)

| Model | Description |
|---|---|
| **BudgetIntelligence** | Core budget intelligence snapshot |
| **BudgetRecommendation** | AI-generated budget recommendations |
| **BudgetPrediction** | Predicted future budget states |
| **BudgetRisk** | Identified budget risks |
| **SavingsOpportunity** | Detected savings opportunities |

### Repositories (5)

One repository per model.

### Services (8)

| Service | Responsibility |
|---|---|
| **SmartBudgetService** | Generates intelligent budget limits from historical data |
| **CategoryTrendService** | Analyzes category-level spending trends |
| **BudgetForecastService** | Forecasts future budget trajectories |
| **BudgetRiskService** | Identifies overspend risk and anomalies |
| **BudgetRecommendationService** | Generates 3 recommendation types (reduce, reallocate, alert) |
| **BudgetOptimizationService** | Suggests optimal budget allocations |
| **SavingsOpportunityService** | Detects 6 savings opportunity types |
| **BudgetIntelligenceService** | Orchestrator coordinating all sub-services |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/budget-intelligence/generate` | Generate budget intelligence |
| POST | `/budget-intelligence/recalculate` | Force recalculation |
| GET | `/budget-intelligence/current` | Current intelligence snapshot |
| GET | `/budget-intelligence/recommendations` | Budget recommendations |
| GET | `/budget-intelligence/optimization` | Optimization suggestions |
| GET | `/budget-intelligence/trends` | Category and budget trends |
| GET | `/budget-intelligence/risk` | Budget risk analysis |
| GET | `/budget-intelligence/opportunities` | Savings opportunities |

## Frontend Pages & Layout

### Pages (5)

| Page | Description |
|---|---|
| **BIOOverviewPage** | Current budget intelligence summary |
| **BIRecommendationsPage** | AI-generated budget recommendations |
| **BIOptimizationPage** | Optimization suggestions |
| **BITrendsPage** | Category and budget trend visualizations |
| **BIOpportunitiesPage** | Savings opportunities list |

### Layout

**BudgetIntelligenceLayout** provides a 5-item sidebar navigation.

## Event Types

No events published by this module.

## Configuration

No module-specific configuration.

## Status & Version

| Property | Value |
|---|---|
| Phase | 10 |
| Version | 1.10 |
| Backend directory | `backend/app/budget_intelligence/` |
| Models | 5 |
| Repositories | 5 |
| Services | 8 |
| Endpoints | 8 |
| Recommendation types | 3 |
| Savings opportunity types | 6 |
| Frontend pages | 5 |
| Integration tests | 9/9 passing |
