"""Printable monthly payment calendar."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date

from .models import Bill, parse_date


class PaymentCalendar:
    """Renders a printable text calendar annotated with bill due dates."""

    def __init__(self, bills: list[Bill]):
        self.bills = bills

    def _due_by_day(self, year: int, month: int) -> dict[int, list[Bill]]:
        grouped: dict[int, list[Bill]] = defaultdict(list)
        for b in self.bills:
            if b.is_paid or not b.due_date:
                continue
            try:
                due = parse_date(b.due_date)
            except ValueError:
                continue
            if due.year == year and due.month == month:
                grouped[due.day].append(b)
        return grouped

    def render(self, year: int, month: int) -> str:
        cal = calendar.TextCalendar(calendar.SUNDAY)
        grouped = self._due_by_day(year, month)
        header = f"{calendar.month_name[month]} {year}  Payment Calendar"
        lines = []
        lines.append(header.center(40))
        lines.append("=" * 40)
        lines.append("Su Mo Tu We Th Fr Sa")
        for week in cal.monthdayscalendar(year, month):
            parts = []
            for day in week:
                if day == 0:
                    parts.append("   ")
                else:
                    dues = grouped.get(day, [])
                    tag = "*" if dues else " "
                    parts.append(f"{day:>2}{tag}")
            lines.append(" ".join(parts))
        lines.append("")
        lines.append("* = bill due (unpaid)")
        lines.append("")
        if any(grouped.values()):
            lines.append("Due dates this month:")
            for day in sorted(grouped):
                for b in grouped[day]:
                    lines.append(
                        f"  {day:02d}  ${b.balance:.2f}  {b.provider}  ({b.id})"
                    )
        else:
            lines.append("No unpaid bills due this month.")
        lines.append("")
        return "\n".join(lines)

    def render_range(self, start: date, end: date) -> str:
        """Render every month in an inclusive date range."""
        out = []
        y, m = start.year, start.month
        while (y, m) <= (end.year, end.month):
            out.append(self.render(y, m))
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
        return "\n".join(out)
