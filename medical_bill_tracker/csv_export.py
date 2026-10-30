"""CSV export for bills, EOBs, and payments."""

from __future__ import annotations

import csv
import io

from .models import EOB, Bill, Payment, TrackerData


def bills_csv(bills: list[Bill]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "id",
            "provider",
            "amount_due",
            "amount_paid",
            "balance",
            "due_date",
            "status",
            "category",
            "eob_reference",
            "notes",
        ]
    )
    for b in bills:
        writer.writerow(
            [
                b.id,
                b.provider,
                f"{b.amount_due:.2f}",
                f"{b.amount_paid:.2f}",
                f"{b.balance:.2f}",
                b.due_date,
                b.status,
                b.category,
                b.eob_reference,
                b.notes,
            ]
        )
    return buf.getvalue()


def eobs_csv(eobs: list[EOB]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "id",
            "claim_number",
            "provider",
            "date_of_service",
            "billed_amount",
            "allowed_amount",
            "insurance_paid",
            "patient_owes",
            "received_date",
            "notes",
        ]
    )
    for e in eobs:
        writer.writerow(
            [
                e.id,
                e.claim_number,
                e.provider,
                e.date_of_service,
                f"{e.billed_amount:.2f}",
                f"{e.allowed_amount:.2f}",
                f"{e.insurance_paid:.2f}",
                f"{e.patient_balance:.2f}",
                e.received_date,
                e.notes,
            ]
        )
    return buf.getvalue()


def payments_csv(payments: list[Payment]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["id", "date", "amount", "payee", "payment_type", "reference_id", "notes"]
    )
    for p in payments:
        writer.writerow(
            [
                p.id,
                p.date,
                f"{p.amount:.2f}",
                p.payee,
                p.payment_type,
                p.reference_id,
                p.notes,
            ]
        )
    return buf.getvalue()


def export_all(data: TrackerData) -> dict[str, str]:
    return {
        "bills.csv": bills_csv(data.bills),
        "eobs.csv": eobs_csv(data.eobs),
        "payments.csv": payments_csv(data.payments),
    }
