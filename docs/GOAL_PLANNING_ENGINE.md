# AI Financial Goal Planning Engine

**Phase:** 12 | **Version:** 1.12

## Overview

The AI Financial Goal Planning Engine enables users to define, track, and achieve financial goals across 10 types. It computes goal feasibility using a 4-factor scoring model, generates savings plans with discretionary overspend detection, predicts goal outcomes with 60-month projections, tracks progress through configurable milestones, and delivers intelligent recommendations with confidence scores, impact ratings, and step-by-step plans. The module comprises 5 models, 5 repositories, 7 services, 9 REST endpoints, and publishes 7 event types. It is consumed by 6 frontend pages within a dedicated GoalsLayout.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
│                                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │GoalsOverview │ │CreateGoal    │ │GoalDetail    │ │GoalRecommenda- │  │
│  │Page          │ │Page          │ │Page          │ │tionsPage       │  │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └───────┬────────┘  │
│         │                │                │                  │           │
│  ┌──────┴────────────────┴────────────────┴──────────────────┴───────┐  │
│  │                   GoalsLayout (5-item sidebar nav)                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────┐ ┌──────────────────┐                                  │
│  │GoalProgress  │ │GoalHistory       │                                  │
│  │Page          │ │Page              │                                  │
│  └──────────────┘ └──────────────────┘                                  │
├────────────────────┼────────────────────────────────────────────────────┤
│                API │ 9 routes                                           │
├────────────────────┼────────────────────────────────────────────────────┤
│                     BACKEND                                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     GoalPlanningService (orchestrator)           │   │
│  │                     Event publishing                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌────────────────┐ ┌──────────────────┐ ┌────────────────────┐        │
│  │GoalFeasibility │ │SavingsPlanService │ │GoalPrediction     │        │
│  │Service         │ │(discretionary     │ │Service            │        │
│  │(4-factor)      │ │ overspend detect) │ │(probability)      │        │
│  └────────────────┘ └──────────────────┘ └────────────────────┘        │
│  ┌────────────────┐ ┌──────────────────┐ ┌────────────────────┐        │
│  │GoalProgress    │ │GoalRecommendation│ │GoalNotification   │        │
│  │Service         │ │Service           │ │Service            │        │
│  │(milestones,    │ │(3 types,         │ │(completion,       │        │
│  │ missed detect) │ │ confidence/      │ │ milestone, at-risk│        │
│  │                │ │ impact/steps)    │ │ alerts)           │        │
│  └────────────────┘ └──────────────────┘ └────────────────────┘        │
│                                                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────┐  │
│  │Financial   │ │GoalProgress│ │GoalRecommen-│ │GoalPredict-│ │Goal  │  │
│  │Goal Repo   │ │Repo        │ │dation Repo  │ │ion Repo    │ │Notif.│  │
│  │            │ │            │ │             │ │            │ │Repo  │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └──────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Models (5)

| Model | Description |
|---|---|
| **FinancialGoal** | 10 types: `savings`, `emergency_fund`, `debt_repayment`, `investment`, `retirement`, `education`, `home_purchase`, `travel`, `wedding`, `custom` |
| **GoalProgress** | Tracks progress with up to 4 configurable milestones |
| **GoalRecommendation** | AI-driven recommendations with confidence, impact, and steps |
| **GoalPrediction** | 60-month projection with probability of success |
| **GoalNotification** | Alerts for completion, milestones, at-risk states |

### Repositories (5)

One repository per model.

### Services (7)

| Service | Responsibility |
|---|---|
| **GoalFeasibilityService** | 4-factor scoring (income, expenses, timeline, risk tolerance) |
| **SavingsPlanService** | Generates savings plans; detects discretionary overspend |
| **GoalPredictionService** | 60-month projection with probability of success |
| **GoalProgressService** | Milestone tracking and missed-milestone detection |
| **GoalRecommendationService** | 3 recommendation types with confidence score, impact rating, and step-by-step actions |
| **GoalNotificationService** | Sends notifications for completion, milestone reached, at-risk, and alerts |
| **GoalPlanningService** | Orchestrator coordinating all sub-services; publishes events |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/goals` | Create a new goal |
| PUT | `/goals/{id}` | Update an existing goal |
| DELETE | `/goals/{id}` | Delete a goal |
| GET | `/goals` | List all goals |
| GET | `/goals/{id}` | Get goal details |
| POST | `/goals/analyze` | Analyze goal feasibility |
| POST | `/goals/recalculate` | Recalculate all goal projections |
| GET | `/goals/recommendations` | Get goal recommendations |
| GET | `/goals/progress` | Get aggregated progress |

## Frontend Pages & Layout

### Pages (6)

| Page | Description |
|---|---|
| **GoalsOverviewPage** | Dashboard of all goals with progress tiles |
| **CreateGoalPage** | Goal creation form (type, target, timeline) |
| **GoalDetailPage** | Single goal detail with milestones and projection |
| **GoalRecommendationsPage** | AI-generated recommendations |
| **GoalProgressPage** | Aggregated progress across goals |
| **GoalHistoryPage** | Historical goal activity |

### Layout

**GoalsLayout** provides a 5-item sidebar navigation across all goal pages.

## Event Types (7)

| Event | Trigger |
|---|---|
| `goal.created` | New goal created |
| `goal.updated` | Goal details modified |
| `goal.deleted` | Goal removed |
| `goal.completed` | Goal target achieved |
| `goal.milestone_reached` | Milestone completed |
| `goal.at_risk` | Goal is off-track |
| `goal.progress_updated` | Progress recalculated |

## Configuration

No module-specific configuration.

## Status & Version

| Property | Value |
|---|---|
| Phase | 12 |
| Version | 1.12 |
| Backend directory | `backend/app/goal_planning/` |
| Models | 5 |
| Repositories | 5 |
| Services | 7 |
| Endpoints | 9 |
| Goal types | 10 |
| Milestones per goal | Up to 4 |
| Projection horizon | 60 months |
| Recommendation dimensions | Confidence, impact, steps |
| Event types | 7 |
| Frontend pages | 6 |
