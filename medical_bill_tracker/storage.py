"""Local JSON storage for the medical bill tracker."""

from __future__ import annotations

import json
import os
import uuid
from datetime import date
from pathlib import Path

from .models import EOB, Bill, Payment, TrackerData, format_date

DEFAULT_FILENAME = "tracker.json"


class Storage:
    """Reads/writes tracker data to a local JSON file."""

    def __init__(self, data_dir: str | os.PathLike, filename: str = DEFAULT_FILENAME):
        self.data_dir = Path(data_dir)
        self.path = self.data_dir / filename

    def ensure_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> TrackerData:
        if not self.path.exists():
            return TrackerData()
        with self.path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
        return TrackerData.from_dict(raw)

    def save(self, data: TrackerData) -> None:
        self.ensure_dir()
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data.to_dict(), fh, indent=2, sort_keys=True)
        tmp.replace(self.path)

    # ---- helpers ----

    @staticmethod
    def _new_id() -> str:
        return uuid.uuid4().hex[:12]

    def add_bill(
        self,
        provider: str,
        amount_due: float,
        due_date: str | None,
        status: str = "unpaid",
        category: str = "",
        notes: str = "",
        eob_reference: str = "",
    ) -> Bill:
        data = self.load()
        bill = Bill(
            id=self._new_id(),
            provider=provider,
            amount_due=round(amount_due, 2),
            due_date=due_date or "",
            status=status,
            category=category,
            notes=notes,
            eob_reference=eob_reference,
        )
        data.bills.append(bill)
        self.save(data)
        return bill

    def add_eob(
        self,
        claim_number: str,
        provider: str,
        date_of_service: str = "",
        billed_amount: float = 0.0,
        allowed_amount: float = 0.0,
        insurance_paid: float = 0.0,
        patient_owes: float = 0.0,
        received_date: str | None = None,
        notes: str = "",
    ) -> EOB:
        data = self.load()
        eob = EOB(
            id=self._new_id(),
            claim_number=claim_number,
            provider=provider,
            date_of_service=date_of_service,
            billed_amount=round(billed_amount, 2),
            allowed_amount=round(allowed_amount, 2),
            insurance_paid=round(insurance_paid, 2),
            patient_owes=round(patient_owes, 2),
            received_date=received_date or format_date(date.today()),
            notes=notes,
        )
        data.eobs.append(eob)
        self.save(data)
        return eob

    def add_payment(
        self,
        amount: float,
        payee: str,
        payment_date: str | None = None,
        payment_type: str = "patient",
        reference_id: str = "",
        notes: str = "",
    ) -> Payment:
        data = self.load()
        payment = Payment(
            id=self._new_id(),
            date=payment_date or format_date(date.today()),
            amount=round(amount, 2),
            payee=payee,
            payment_type=payment_type,
            reference_id=reference_id,
            notes=notes,
        )
        data.payments.append(payment)
        self.save(data)
        return payment

    def get_bill(self, bill_id: str) -> Bill | None:
        for b in self.load().bills:
            if b.id == bill_id:
                return b
        return None

    def mark_bill_paid(self, bill_id: str, amount: float) -> Bill | None:
        data = self.load()
        for b in data.bills:
            if b.id == bill_id:
                b.amount_paid = round(b.amount_paid + amount, 2)
                b.status = "paid" if b.balance <= 0 else "partially_paid"
                self.save(data)
                return b
        return None

    def delete_bill(self, bill_id: str) -> bool:
        data = self.load()
        before = len(data.bills)
        data.bills = [b for b in data.bills if b.id != bill_id]
        if len(data.bills) < before:
            self.save(data)
            return True
        return False
