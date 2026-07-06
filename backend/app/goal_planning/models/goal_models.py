from datetime import datetime


GOAL_TYPES = ["emergency_fund", "vacation", "laptop", "vehicle", "house",
              "education", "wedding", "retirement", "investment", "custom"]

GOAL_STATUSES = ["active", "paused", "completed", "cancelled", "on_track", "at_risk"]

PRIORITIES = ["low", "medium", "high", "critical"]


class FinancialGoal:
    def __init__(self, user_id: str, goal_type: str, name: str, target_amount: float,
                 current_amount: float = 0.0, monthly_contribution: float = 0.0,
                 target_date: str = "", status: str = "active", priority: str = "medium",
                 category: str = "", description: str = "", feasibility_score: float = 0.0,
                 confidence_score: float = 0.0, risk_level: str = "moderate",
                 affordability_score: float = 0.0, completion_percentage: float = 0.0,
                 estimated_months: int = 0, start_date: str = "",
                 auto_adjust: bool = True, is_system_recommended: bool = False,
                 metadata: dict | None = None, created_at: datetime | None = None,
                 updated_at: datetime | None = None, id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.goal_type = goal_type
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.monthly_contribution = monthly_contribution
        self.target_date = target_date
        self.status = status
        self.priority = priority
        self.category = category
        self.description = description
        self.feasibility_score = feasibility_score
        self.confidence_score = confidence_score
        self.risk_level = risk_level
        self.affordability_score = affordability_score
        self.completion_percentage = completion_percentage
        self.estimated_months = estimated_months
        self.start_date = start_date
        self.auto_adjust = auto_adjust
        self.is_system_recommended = is_system_recommended
        self.metadata = metadata or {}
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "FinancialGoal":
        return cls(id=str(doc.get("_id", "")), user_id=str(doc.get("user_id", "")),
                   goal_type=doc.get("goal_type", "custom"), name=doc.get("name", ""),
                   target_amount=doc.get("target_amount", 0.0),
                   current_amount=doc.get("current_amount", 0.0),
                   monthly_contribution=doc.get("monthly_contribution", 0.0),
                   target_date=doc.get("target_date", ""),
                   status=doc.get("status", "active"), priority=doc.get("priority", "medium"),
                   category=doc.get("category", ""), description=doc.get("description", ""),
                   feasibility_score=doc.get("feasibility_score", 0.0),
                   confidence_score=doc.get("confidence_score", 0.0),
                   risk_level=doc.get("risk_level", "moderate"),
                   affordability_score=doc.get("affordability_score", 0.0),
                   completion_percentage=doc.get("completion_percentage", 0.0),
                   estimated_months=doc.get("estimated_months", 0),
                   start_date=doc.get("start_date", ""),
                   auto_adjust=doc.get("auto_adjust", True),
                   is_system_recommended=doc.get("is_system_recommended", False),
                   metadata=doc.get("metadata", {}),
                   created_at=doc.get("created_at"), updated_at=doc.get("updated_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "goal_type": self.goal_type, "name": self.name,
             "target_amount": self.target_amount, "current_amount": self.current_amount,
             "monthly_contribution": self.monthly_contribution,
             "target_date": self.target_date, "status": self.status,
             "priority": self.priority, "category": self.category,
             "description": self.description, "feasibility_score": self.feasibility_score,
             "confidence_score": self.confidence_score, "risk_level": self.risk_level,
             "affordability_score": self.affordability_score,
             "completion_percentage": self.completion_percentage,
             "estimated_months": self.estimated_months, "start_date": self.start_date,
             "auto_adjust": self.auto_adjust,
             "is_system_recommended": self.is_system_recommended,
             "metadata": self.metadata, "created_at": self.created_at,
             "updated_at": self.updated_at}
        if self.id:
            d["_id"] = self.id
        return d


class GoalProgress:
    def __init__(self, goal_id: str, user_id: str, period: str,
                 previous_amount: float = 0.0, current_amount: float = 0.0,
                 monthly_contribution: float = 0.0, contribution_count: int = 0,
                 skipped_months: int = 0, milestone_hit: bool = False,
                 milestone_label: str = "", progress_percentage: float = 0.0,
                 on_track: bool = True, notes: str = "",
                 created_at: datetime | None = None, id: str | None = None):
        self.id = id
        self.goal_id = goal_id
        self.user_id = user_id
        self.period = period
        self.previous_amount = previous_amount
        self.current_amount = current_amount
        self.monthly_contribution = monthly_contribution
        self.contribution_count = contribution_count
        self.skipped_months = skipped_months
        self.milestone_hit = milestone_hit
        self.milestone_label = milestone_label
        self.progress_percentage = progress_percentage
        self.on_track = on_track
        self.notes = notes
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "GoalProgress":
        return cls(id=str(doc.get("_id", "")), goal_id=str(doc.get("goal_id", "")),
                   user_id=str(doc.get("user_id", "")), period=doc.get("period", ""),
                   previous_amount=doc.get("previous_amount", 0.0),
                   current_amount=doc.get("current_amount", 0.0),
                   monthly_contribution=doc.get("monthly_contribution", 0.0),
                   contribution_count=doc.get("contribution_count", 0),
                   skipped_months=doc.get("skipped_months", 0),
                   milestone_hit=doc.get("milestone_hit", False),
                   milestone_label=doc.get("milestone_label", ""),
                   progress_percentage=doc.get("progress_percentage", 0.0),
                   on_track=doc.get("on_track", True), notes=doc.get("notes", ""),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"goal_id": self.goal_id, "user_id": self.user_id, "period": self.period,
             "previous_amount": self.previous_amount, "current_amount": self.current_amount,
             "monthly_contribution": self.monthly_contribution,
             "contribution_count": self.contribution_count,
             "skipped_months": self.skipped_months, "milestone_hit": self.milestone_hit,
             "milestone_label": self.milestone_label,
             "progress_percentage": self.progress_percentage, "on_track": self.on_track,
             "notes": self.notes, "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class GoalRecommendation:
    def __init__(self, user_id: str, goal_id: str = "", recommendation_type: str = "",
                 title: str = "", description: str = "", reasoning: str = "",
                 confidence_score: float = 0.0, estimated_impact: dict | None = None,
                 affected_categories: list[str] | None = None,
                 actionable_steps: list[str] | None = None,
                 assumptions: list[str] | None = None, priority: int = 0,
                 dismissed: bool = False, created_at: datetime | None = None,
                 id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.goal_id = goal_id
        self.recommendation_type = recommendation_type
        self.title = title
        self.description = description
        self.reasoning = reasoning
        self.confidence_score = confidence_score
        self.estimated_impact = estimated_impact or {}
        self.affected_categories = affected_categories or []
        self.actionable_steps = actionable_steps or []
        self.assumptions = assumptions or []
        self.priority = priority
        self.dismissed = dismissed
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "GoalRecommendation":
        return cls(id=str(doc.get("_id", "")), user_id=str(doc.get("user_id", "")),
                   goal_id=doc.get("goal_id", ""),
                   recommendation_type=doc.get("recommendation_type", ""),
                   title=doc.get("title", ""), description=doc.get("description", ""),
                   reasoning=doc.get("reasoning", ""),
                   confidence_score=doc.get("confidence_score", 0.0),
                   estimated_impact=doc.get("estimated_impact", {}),
                   affected_categories=doc.get("affected_categories", []),
                   actionable_steps=doc.get("actionable_steps", []),
                   assumptions=doc.get("assumptions", []),
                   priority=doc.get("priority", 0),
                   dismissed=doc.get("dismissed", False),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "goal_id": self.goal_id,
             "recommendation_type": self.recommendation_type, "title": self.title,
             "description": self.description, "reasoning": self.reasoning,
             "confidence_score": self.confidence_score,
             "estimated_impact": self.estimated_impact,
             "affected_categories": self.affected_categories,
             "actionable_steps": self.actionable_steps,
             "assumptions": self.assumptions, "priority": self.priority,
             "dismissed": self.dismissed, "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class GoalPrediction:
    def __init__(self, goal_id: str, user_id: str, period: str = "",
                 predicted_completion_date: str = "",
                 predicted_completion_amount: float = 0.0,
                 estimated_months_remaining: int = 0,
                 monthly_contribution_required: float = 0.0,
                 projected_amounts: list[dict] | None = None,
                 confidence_interval: list[float] | None = None,
                 best_case_date: str = "", worst_case_date: str = "",
                 probability_of_success: float = 0.0,
                 created_at: datetime | None = None, id: str | None = None):
        self.id = id
        self.goal_id = goal_id
        self.user_id = user_id
        self.period = period
        self.predicted_completion_date = predicted_completion_date
        self.predicted_completion_amount = predicted_completion_amount
        self.estimated_months_remaining = estimated_months_remaining
        self.monthly_contribution_required = monthly_contribution_required
        self.projected_amounts = projected_amounts or []
        self.confidence_interval = confidence_interval or []
        self.best_case_date = best_case_date
        self.worst_case_date = worst_case_date
        self.probability_of_success = probability_of_success
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "GoalPrediction":
        return cls(id=str(doc.get("_id", "")), goal_id=str(doc.get("goal_id", "")),
                   user_id=str(doc.get("user_id", "")), period=doc.get("period", ""),
                   predicted_completion_date=doc.get("predicted_completion_date", ""),
                   predicted_completion_amount=doc.get("predicted_completion_amount", 0.0),
                   estimated_months_remaining=doc.get("estimated_months_remaining", 0),
                   monthly_contribution_required=doc.get("monthly_contribution_required", 0.0),
                   projected_amounts=doc.get("projected_amounts", []),
                   confidence_interval=doc.get("confidence_interval", []),
                   best_case_date=doc.get("best_case_date", ""),
                   worst_case_date=doc.get("worst_case_date", ""),
                   probability_of_success=doc.get("probability_of_success", 0.0),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"goal_id": self.goal_id, "user_id": self.user_id, "period": self.period,
             "predicted_completion_date": self.predicted_completion_date,
             "predicted_completion_amount": self.predicted_completion_amount,
             "estimated_months_remaining": self.estimated_months_remaining,
             "monthly_contribution_required": self.monthly_contribution_required,
             "projected_amounts": self.projected_amounts,
             "confidence_interval": self.confidence_interval,
             "best_case_date": self.best_case_date,
             "worst_case_date": self.worst_case_date,
             "probability_of_success": self.probability_of_success,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d


class GoalNotification:
    def __init__(self, user_id: str, goal_id: str = "", notification_type: str = "",
                 title: str = "", message: str = "", severity: str = "info",
                 read: bool = False, actionable: bool = False,
                 action_data: dict | None = None,
                 created_at: datetime | None = None, id: str | None = None):
        self.id = id
        self.user_id = user_id
        self.goal_id = goal_id
        self.notification_type = notification_type
        self.title = title
        self.message = message
        self.severity = severity
        self.read = read
        self.actionable = actionable
        self.action_data = action_data or {}
        self.created_at = created_at

    @classmethod
    def from_mongo(cls, doc: dict) -> "GoalNotification":
        return cls(id=str(doc.get("_id", "")), user_id=str(doc.get("user_id", "")),
                   goal_id=doc.get("goal_id", ""),
                   notification_type=doc.get("notification_type", ""),
                   title=doc.get("title", ""), message=doc.get("message", ""),
                   severity=doc.get("severity", "info"), read=doc.get("read", False),
                   actionable=doc.get("actionable", False),
                   action_data=doc.get("action_data", {}),
                   created_at=doc.get("created_at"))

    def to_mongo(self) -> dict:
        d = {"user_id": self.user_id, "goal_id": self.goal_id,
             "notification_type": self.notification_type, "title": self.title,
             "message": self.message, "severity": self.severity, "read": self.read,
             "actionable": self.actionable, "action_data": self.action_data,
             "created_at": self.created_at}
        if self.id:
            d["_id"] = self.id
        return d
