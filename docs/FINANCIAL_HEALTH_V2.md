# Financial Health Engine V2

**Phase:** 9 | **Version:** 1.9

## Overview

The Financial Health Engine V2 computes a holistic financial wellness score using a 10-factor weighted formula across 5 risk levels (Excellent, Good, Fair, Moderate, Poor). It provides historical tracking, trend analysis, risk profiling, and actionable recommendations. The module comprises 4 models, 4 repositories, 7 services, and 8 REST endpoints consumed by 5 frontend pages within a dedicated HealthLayout.

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                   │
│                                                                   │
│  ┌──────────────────┐ ┌────────────────┐ ┌──────────────────┐    │
│  │HealthOverview    │ │HealthHistory   │ │HealthTrends      │    │
│  │Page              │ │Page            │ │Page              │    │
│  └────────┬─────────┘ └───────┬────────┘ └───────┬──────────┘    │
│           │                   │                   │                │
│  ┌────────┴───────────────────┴───────────────────┴───────────┐  │
│  │               HealthLayout (5-item sidebar nav)            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────┐ ┌────────────────────┐ ┌──────────────┐   │
│  │HealthRecommen-   │ │HealthRisk          │ │              │   │
│  │dationsPage       │ │Page                │ │              │   │
│  └──────────────────┘ └────────────────────┘ └──────────────┘   │
├──────────────────────┼────────────────────────────────────────────┤
│                  API │ 8 routes                                   │
├──────────────────────┼────────────────────────────────────────────┤
│                   BACKEND                                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                     Services                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐  │    │
│  │  │HealthScore   │ │RiskAssessment│ │HealthHistory    │  │    │
│  │  │Calculator    │ │Service       │ │Service          │  │    │
│  │  │(10-factor    │ │              │ │                 │  │    │
│  │  │ weighted)    │ │              │ │                 │  │    │
│  │  └──────────────┘ └──────────────┘ └─────────────────┘  │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐  │    │
│  │  │TrendAnalysis │ │Recommendation│ │HealthAggregation│  │    │
│  │  │Service       │ │Engine        │ │Service          │  │    │
│  │  │              │ │(5 types)     │ │                 │  │    │
│  │  └──────────────┘ └──────────────┘ └─────────────────┘  │    │
│  │  ┌──────────────────────────────────────────────────┐    │    │
│  │  │              FinancialHealthService              │    │    │
│  │  └──────────────────────────────────────────────────┘    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────────┐  │
│  │FinancialHealth│ │HealthHistory │ │RiskProfile│ │HealthRec-  │  │
│  │Repo          │ │Repo          │ │Repo       │ │ommendation │  │
│  │              │ │              │ │           │ │Repo        │  │
│  └──────────────┘ └──────────────┘ └───────────┘ └────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models

| Model | Description |
|---|---|
| **FinancialHealth** | Core health score and factor breakdown |
| **HealthHistory** | Historical snapshots of health scores |
| **RiskProfile** | User risk categorization and factors |
| **HealthRecommendation** | Generated recommendations with priority |

### Repositories (4)

One repository per model: `FinancialHealthRepository`, `HealthHistoryRepository`, `RiskProfileRepository`, `HealthRecommendationRepository`.

### Services (7)

| Service | Responsibility |
|---|---|
| **HealthScoreCalculator** | 10-factor weighted formula producing a composite score; classifies into 5 risk levels: Excellent (≥800), Good (700–799), Fair (600–699), Moderate (500–599), Poor (<500) |
| **RiskAssessmentService** | Evaluates risk based on score and external factors |
| **HealthHistoryService** | Manages historical score snapshots |
| **TrendAnalysisService** | Analyzes score direction and velocity |
| **RecommendationEngine** | Generates 5 types of actionable recommendations |
| **HealthAggregationService** | Aggregates data across all health services |
| **FinancialHealthService** | Top-level orchestrator |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/health/calculate` | Calculate current health score |
| POST | `/health/recalculate` | Force recalculation |
| GET | `/health/current` | Latest health score and breakdown |
| GET | `/health/history` | Historical score data |
| GET | `/health/trends` | Trend analysis |
| GET | `/health/breakdown` | Factor-by-factor breakdown |
| GET | `/health/recommendations` | Actionable recommendations |
| GET | `/health/risk` | Risk profile |

## Frontend Pages & Layout

### Pages (5)

| Page | Description |
|---|---|
| **HealthOverviewPage** | Current score, risk level, summary tiles |
| **HealthHistoryPage** | Historical score chart and table |
| **HealthTrendsPage** | Direction and velocity analysis |
| **HealthRecommendationsPage** | Actionable items with priority |
| **HealthRiskPage** | Detailed risk profile breakdown |

### Layout

**HealthLayout** provides a 5-item sidebar navigation across all health pages.

## Event Types

No events published by this module. Health data is consumed by other modules (Dashboard V2 widgets, notifications).

## Configuration

No module-specific configuration.

## Status & Version

| Property | Value |
|---|---|
| Phase | 9 |
| Version | 1.9 |
| Backend directory | `backend/app/health/` |
| Models | 4 |
| Repositories | 4 |
| Services | 7 |
| Endpoints | 8 |
| Risk levels | 5 (Excellent, Good, Fair, Moderate, Poor) |
| Scoring factors | 10 |
| Frontend pages | 5 |
