import tempfile
from datetime import date, timedelta

import pytest

from medical_bill_tracker.calendar_view import PaymentCalendar
from medical_bill_tracker.csv_export import export_all
from medical_bill_tracker.models import (
    EOB,
    Bill,
    Payment,
    TrackerData,
    format_date,
    parse_date,
)
from medical_bill_tracker.storage import Storage
from medical_bill_tracker.summary import Summary


@pytest.fixture
def storage():
    dirpath = tempfile.mkdtemp()
    return Storage(dirpath)


def test_parse_and_format_date_roundtrip():
    d = parse_date("2026-11-15")
    assert d.year == 2026 and d.month == 11 and d.day == 15
    assert format_date(d) == "2026-11-15"


def test_bill_balance_and_paid_status():
    b = Bill(id="b1", provider="Clinic", amount_due=100.0, amount_paid=30.0)
    assert b.balance == 70.0
    assert not b.is_paid
    b.amount_paid = 100.0
    assert b.balance == 0.0
    assert b.is_paid


def test_bill_overdue_logic():
    today = date.today()
    b_past = Bill(
        id="b1",
        provider="Clinic",
        amount_due=50.0,
        due_date=format_date(today - timedelta(days=5)),
    )
    assert b_past.is_overdue
    b_future = Bill(
        id="b2",
        provider="Clinic",
        amount_due=50.0,
        due_date=format_date(today + timedelta(days=5)),
    )
    assert not b_future.is_overdue
    b_paid = Bill(
        id="b3",
        provider="Clinic",
        amount_due=50.0,
        amount_paid=50.0,
        due_date=format_date(today - timedelta(days=5)),
    )
    assert not b_paid.is_overdue
    b_no_due = Bill(id="b4", provider="Clinic", amount_due=50.0)
    assert not b_no_due.is_overdue


def test_summary_totals_and_by_provider():
    data = TrackerData(
        bills=[
            Bill(
                id="b1",
                provider="Hospital A",
                amount_due=200.0,
                amount_paid=50.0,
                status="partially_paid",
            ),
            Bill(
                id="b2",
                provider="Hospital A",
                amount_due=100.0,
                amount_paid=100.0,
                status="paid",
            ),
            Bill(
                id="b3",
                provider="Clinic B",
                amount_due=75.0,
                amount_paid=0.0,
                status="unpaid",
            ),
        ]
    )
    s = Summary(data)
    assert s.total_billed() == 375.0
    assert s.total_paid() == 150.0
    assert s.total_outstanding() == 225.0
    providers = s.by_provider()
    assert providers["Hospital A"]["outstanding"] == 150.0
    assert providers["Clinic B"]["outstanding"] == 75.0
    assert s.by_status()["unpaid"]["count"] == 1
    assert s.by_status()["paid"]["count"] == 1


def test_summary_upcoming_and_overdue():
    today = date.today()
    data = TrackerData(
        bills=[
            Bill(
                id="b1",
                provider="X",
                amount_due=10.0,
                due_date=format_date(today - timedelta(days=2)),
            ),
            Bill(
                id="b2",
                provider="Y",
                amount_due=20.0,
                due_date=format_date(today + timedelta(days=10)),
            ),
            Bill(
                id="b3",
                provider="Z",
                amount_due=30.0,
                due_date=format_date(today + timedelta(days=45)),
            ),
            Bill(
                id="b4",
                provider="W",
                amount_due=40.0,
                amount_paid=40.0,
                due_date=format_date(today - timedelta(days=2)),
            ),
        ]
    )
    s = Summary(data)
    overdue = s.overdue()
    assert len(overdue) == 1
    assert overdue[0].id == "b1"
    upcoming = s.upcoming(days=30)
    assert len(upcoming) == 1
    assert upcoming[0].id == "b2"


def test_storage_roundtrip(storage):
    b = storage.add_bill("Clinic", 123.45, "2026-12-01")
    assert b.id is not None
    loaded = storage.load()
    assert len(loaded.bills) == 1
    assert loaded.bills[0].balance == 123.45

    fetched = storage.get_bill(b.id)
    assert fetched is not None
    assert fetched.provider == "Clinic"

    updated = storage.mark_bill_paid(b.id, 50.0)
    assert updated.balance == 73.45
    assert updated.status == "partially_paid"

    storage.mark_bill_paid(b.id, 73.45)
    updated = storage.get_bill(b.id)
    assert updated.status == "paid"

    assert storage.delete_bill(b.id) is True
    assert storage.delete_bill("nope") is False
    assert len(storage.load().bills) == 0


def test_eob_and_payment(storage):
    e = storage.add_eob("C123", "Clinic", patient_owes=40.0, insurance_paid=160.0)
    assert e.patient_balance == 40.0
    p = storage.add_payment(40.0, "Patient", reference_id=e.id)
    assert p.amount == 40.0
    loaded = storage.load()
    assert len(loaded.eobs) == 1
    assert len(loaded.payments) == 1


def test_calendar_render_contains_due_marks():
    today = date.today()
    bills = [
        Bill(id="b1", provider="Clinic", amount_due=50.0, due_date=format_date(today)),
    ]
    cal = PaymentCalendar(bills)
    out = cal.render(today.year, today.month)
    assert f"*{today.day:02d}" in out or f" {today.day:02d}* " in out or "*" in out
    assert "Payment Calendar" in out


def test_csv_export_shapes():
    data = TrackerData(
        bills=[
            Bill(
                id="b1",
                provider="Clinic",
                amount_due=10.0,
                amount_paid=2.0,
                due_date="2026-01-01",
            )
        ],
        eobs=[EOB(id="e1", claim_number="C1", provider="Clinic", patient_owes=5.0)],
        payments=[Payment(id="p1", date="2026-01-02", amount=5.0, payee="Clinic")],
    )
    files = export_all(data)
    assert "bills.csv" in files and "eobs.csv" in files and "payments.csv" in files
    assert files["bills.csv"].startswith("id,provider,amount_due")
    assert "$" not in files["bills.csv"]
