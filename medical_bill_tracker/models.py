"""Data models for the medical bill tracker."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime

DATE_FORMAT = "%Y-%m-%d"


def parse_date(value: str) -> date:
    """Parse a YYYY-MM-DD string into a date."""
    return datetime.strptime(value, DATE_FORMAT).date()


def format_date(value: date) -> str:
    """Format a date as YYYY-MM-DD."""
    return value.strftime(DATE_FORMAT)


@dataclass
class Bill:
    """A medical bill from a provider."""

    id: str
    provider: str
    amount_due: float
    amount_paid: float = 0.0
    due_date: str = ""
    status: str = "unpaid"  # unpaid, partially_paid, paid
    category: str = ""
    notes: str = ""
    eob_reference: str = ""

    @property
    def balance(self) -> float:
        return round(self.amount_due - self.amount_paid, 2)

    @property
    def is_paid(self) -> bool:
        return self.balance <= 0.0

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.is_paid:
            return False
        return parse_date(self.due_date) < date.today()

    @property
    def due_date_obj(self) -> date | None:
        if not self.due_date:
            return None
        return parse_date(self.due_date)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> Bill:
        return Bill(**d)


@dataclass
class EOB:
    """An Explanation of Benefits from an insurer."""

    id: str
    claim_number: str
    provider: str
    date_of_service: str = ""
    billed_amount: float = 0.0
    allowed_amount: float = 0.0
    insurance_paid: float = 0.0
    patient_owes: float = 0.0
    received_date: str = ""
    notes: str = ""

    @property
    def patient_balance(self) -> float:
        return round(self.patient_owes, 2)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> EOB:
        return EOB(**d)


@dataclass
class Payment:
    """A payment toward a bill or EOB (insurance or patient)."""

    id: str
    date: str
    amount: float
    payee: str
    payment_type: str = "patient"  # patient or insurance
    reference_id: str = ""  # bill id or claim number
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> Payment:
        return Payment(**d)


@dataclass
class TrackerData:
    """Top-level container persisted to JSON."""

    bills: list = field(default_factory=list)
    eobs: list = field(default_factory=list)
    payments: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "bills": [b.to_dict() for b in self.bills],
            "eobs": [e.to_dict() for e in self.eobs],
            "payments": [p.to_dict() for p in self.payments],
        }

    @staticmethod
    def from_dict(d: dict) -> TrackerData:
        return TrackerData(
            bills=[Bill.from_dict(b) for b in d.get("bills", [])],
            eobs=[EOB.from_dict(e) for e in d.get("eobs", [])],
            payments=[Payment.from_dict(p) for p in d.get("payments", [])],
        )
