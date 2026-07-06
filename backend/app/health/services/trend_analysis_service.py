from statistics import pstdev

from app.health.repositories.health_history_repository import (
    MongoHealthHistoryRepository,
)


class TrendAnalysisService:
    def __init__(self, history_repo: MongoHealthHistoryRepository):
        self._history_repo = history_repo

    async def analyze(self, user_id: str, months: int = 12) -> dict:
        history = await self._history_repo.get_by_user(user_id, months)
        if len(history) < 2:
            return {
                "overall_trend": "stable",
                "volatility": 0,
                "periods_analyzed": len(history),
                "points": [
                    {"period": h.period, "score": h.score, "delta": 0}
                    for h in history
                ],
            }

        points = []
        deltas = []
        for i in range(len(history)):
            prev_score = history[i + 1].score if i + 1 < len(history) else history[i].score
            delta = history[i].score - prev_score if i + 1 < len(history) else 0
            deltas.append(delta)
            points.append({
                "period": history[i].period,
                "score": history[i].score,
                "delta": delta,
            })

        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        if avg_delta > 3:
            trend = "improving"
        elif avg_delta < -3:
            trend = "declining"
        else:
            trend = "stable"

        scores = [h.score for h in history]
        volatility = round(pstdev(scores), 2) if len(scores) > 1 else 0

        return {
            "overall_trend": trend,
            "volatility": volatility,
            "periods_analyzed": len(history),
            "points": points,
        }
