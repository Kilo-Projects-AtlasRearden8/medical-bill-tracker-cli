"""Balance summaries for the medical bill tracker."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from .models import Bill, TrackerData, parse_date


class Summary:
    """Computed balance and aging summaries."""

    def __init__(self, data: TrackerData):
        self.data = data

    def total_billed(self) -> float:
        return round(sum(b.amount_due for b in self.data.bills), 2)

    def total_paid(self) -> float:
        return round(sum(b.amount_paid for b in self.data.bills), 2)

    def total_outstanding(self) -> float:
        return round(sum(b.balance for b in self.data.bills), 2)

    def total_eob_patient_owes(self) -> float:
        return round(sum(e.patient_balance for e in self.data.eobs), 2)

    def total_insurance_paid(self) -> float:
        return round(sum(e.insurance_paid for e in self.data.eobs), 2)

    def by_provider(self) -> dict[str, dict[str, float]]:
        result: dict[str, dict[str, float]] = defaultdict(
            lambda: {"billed": 0.0, "paid": 0.0, "outstanding": 0.0}
        )
        for b in self.data.bills:
            entry = result[b.provider]
            entry["billed"] += b.amount_due
            entry["paid"] += b.amount_paid
            entry["outstanding"] += b.balance
        return {
            k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in result.items()
        }

    def by_status(self) -> dict[str, dict[str, object]]:
        result: dict[str, dict[str, object]] = defaultdict(
            lambda: {"count": 0, "outstanding": 0.0}
        )
        for b in self.data.bills:
            entry = result[b.status]
            entry["count"] += 1
            entry["outstanding"] += b.balance
        return {
            k: {"count": v["count"], "outstanding": round(v["outstanding"], 2)}
            for k, v in result.items()
        }

    def upcoming(self, days: int = 30) -> list[Bill]:
        today = date.today()
        cutoff = today + timedelta(days=days)
        result = []
        for b in self.data.bills:
            if b.is_paid or not b.due_date:
                continue
            due = parse_date(b.due_date)
            if today <= due <= cutoff:
                result.append(b)
        result.sort(key=lambda b: parse_date(b.due_date))
        return result

    def overdue(self) -> list[Bill]:
        return [b for b in self.data.bills if b.is_overdue]

    def as_text(self, upcoming_days: int = 30) -> str:
        lines = []
        lines.append("Medical Bill Balance Summary")
        lines.append("=" * 32)
        lines.append(f"Total billed:   ${self.total_billed():.2f}")
        lines.append(f"Total paid:     ${self.total_paid():.2f}")
        lines.append(f"Outstanding:    ${self.total_outstanding():.2f}")
        lines.append("")
        lines.append("By provider:")
        for provider, amounts in sorted(self.by_provider().items()):
            lines.append(
                f"  {provider}: billed ${amounts['billed']:.2f} "
                f"paid ${amounts['paid']:.2f} "
                f"outstanding ${amounts['outstanding']:.2f}"
            )
        lines.append("")
        lines.append("By status:")
        for status, info in sorted(self.by_status().items()):
            lines.append(
                f"  {status}: {info['count']} bill(s), "
                f"${info['outstanding']:.2f} outstanding"
            )
        lines.append("")
        overdue = self.overdue()
        lines.append(f"Overdue bills: {len(overdue)}")
        for b in overdue:
            lines.append(f"  {b.due_date}  {b.provider}  ${b.balance:.2f}  {b.id}")
        lines.append("")
        upcoming = self.upcoming(upcoming_days)
        lines.append(f"Due in next {upcoming_days} days: {len(upcoming)}")
        for b in upcoming:
            lines.append(f"  {b.due_date}  {b.provider}  ${b.balance:.2f}  {b.id}")
        lines.append("")
        lines.append(
            f"EOB patient responsibility total: ${self.total_eob_patient_owes():.2f}"
        )
        lines.append(
            f"Insurance paid (EOBs):             ${self.total_insurance_paid():.2f}"
        )
        return "\n".join(lines)
