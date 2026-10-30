"""Command-line interface for the medical bill tracker."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from .calendar_view import PaymentCalendar
from .csv_export import export_all
from .models import parse_date
from .storage import Storage
from .summary import Summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="medical-bill-tracker",
        description="Local-first medical bill, EOB, and payment tracker.",
    )
    parser.add_argument(
        "--data-dir",
        default="~/.medical_bill_tracker",
        help="Directory holding the local JSON store (default: ~/.medical_bill_tracker)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add-bill
    p = sub.add_parser("add-bill", help="Add a medical bill")
    p.add_argument("--provider", required=True)
    p.add_argument("--amount", required=True, type=float)
    p.add_argument("--due", required=True, help="Due date YYYY-MM-DD")
    p.add_argument(
        "--status", default="unpaid", choices=["unpaid", "partially_paid", "paid"]
    )
    p.add_argument("--category", default="")
    p.add_argument("--notes", default="")
    p.add_argument("--eob-reference", default="")

    # add-eob
    p = sub.add_parser("add-eob", help="Add an Explanation of Benefits")
    p.add_argument("--claim", required=True, dest="claim_number")
    p.add_argument("--provider", required=True)
    p.add_argument("--date-of-service", default="", dest="date_of_service")
    p.add_argument("--billed", type=float, default=0.0)
    p.add_argument("--allowed", type=float, default=0.0)
    p.add_argument("--insurance-paid", type=float, default=0.0, dest="insurance_paid")
    p.add_argument("--patient-owes", type=float, default=0.0, dest="patient_owes")
    p.add_argument("--received", default=None)

    # add-payment
    p = sub.add_parser("add-payment", help="Record a payment")
    p.add_argument("--amount", required=True, type=float)
    p.add_argument("--payee", required=True)
    p.add_argument("--date", default=None)
    p.add_argument(
        "--type",
        default="patient",
        choices=["patient", "insurance"],
        dest="payment_type",
    )
    p.add_argument("--reference", default="", dest="reference_id")
    p.add_argument("--notes", default="")

    # pay-bill
    p = sub.add_parser("pay-bill", help="Record a payment against a specific bill")
    p.add_argument("--id", required=True, dest="bill_id")
    p.add_argument("--amount", required=True, type=float)
    p.add_argument("--date", default=None)

    # list-bills
    p = sub.add_parser("list-bills", help="List bills")
    p.add_argument(
        "--status", default=None, choices=["unpaid", "partially_paid", "paid"]
    )

    # list-eobs / list-payments
    sub.add_parser("list-eobs", help="List EOBs")
    sub.add_parser("list-payments", help="List payments")

    # summary
    sub.add_parser("summary", help="Print balance summary")

    # calendar
    p = sub.add_parser("calendar", help="Print a printable payment calendar")
    p.add_argument("--year", type=int, default=date.today().year)
    p.add_argument("--month", type=int, default=date.today().month)
    p.add_argument(
        "--range",
        nargs=2,
        metavar=("START", "END"),
        help="YYYY-MM-DD YYYY-MM-DD, print all months in range",
    )

    # export
    p = sub.add_parser("export", help="Export data to CSV files")
    p.add_argument(
        "--out", default=".", help="Output directory (default: current directory)"
    )

    # delete-bill
    p = sub.add_parser("delete-bill", help="Delete a bill by id")
    p.add_argument("--id", required=True, dest="bill_id")

    return parser


def cmd_add_bill(args, storage: Storage) -> int:
    b = storage.add_bill(
        provider=args.provider,
        amount_due=args.amount,
        due_date=args.due,
        status=args.status,
        category=args.category,
        notes=args.notes,
        eob_reference=args.eob_reference,
    )
    print(f"Added bill {b.id}: {b.provider} — ${b.amount_due:.2f} due {b.due_date}")
    return 0


def cmd_add_eob(args, storage: Storage) -> int:
    e = storage.add_eob(
        claim_number=args.claim_number,
        provider=args.provider,
        date_of_service=args.date_of_service,
        billed_amount=args.billed,
        allowed_amount=args.allowed,
        insurance_paid=args.insurance_paid,
        patient_owes=args.patient_owes,
        received_date=args.received,
    )
    print(
        f"Added EOB {e.id}: claim {e.claim_number} — patient owes ${e.patient_balance:.2f}"
    )
    return 0


def cmd_add_payment(args, storage: Storage) -> int:
    p = storage.add_payment(
        amount=args.amount,
        payee=args.payee,
        payment_date=args.date,
        payment_type=args.payment_type,
        reference_id=args.reference_id,
        notes=args.notes,
    )
    print(f"Recorded payment {p.id}: ${p.amount:.2f} to {p.payee} on {p.date}")
    return 0


def cmd_pay_bill(args, storage: Storage) -> int:
    b = storage.mark_bill_paid(args.bill_id, args.amount)
    if b is None:
        print(f"Bill {args.bill_id} not found", file=sys.stderr)
        return 1
    print(
        f"Applied ${args.amount:.2f} to bill {b.id} ({b.provider}); "
        f"balance ${b.balance:.2f}, status {b.status}"
    )
    return 0


def cmd_list_bills(args, storage: Storage) -> int:
    bills = storage.load().bills
    if args.status:
        bills = [b for b in bills if b.status == args.status]
    if not bills:
        print("No bills.")
        return 0
    print(f"{'ID':<12} {'Provider':<26} {'Due':<12} {'Balance':<10} {'Status'}")
    print("-" * 70)
    for b in bills:
        print(
            f"{b.id:<12} {b.provider:<26} {b.due_date:<12} ${b.balance:<9.2f} {b.status}"
        )
    return 0


def cmd_list_eobs(args, storage: Storage) -> int:
    eobs = storage.load().eobs
    if not eobs:
        print("No EOBs.")
        return 0
    print(
        f"{'ID':<12} {'Claim':<18} {'Provider':<26} {'Patient Owes':<12} {'Received'}"
    )
    print("-" * 80)
    for e in eobs:
        print(
            f"{e.id:<12} {e.claim_number:<18} {e.provider:<26} "
            f"${e.patient_balance:<11.2f} {e.received_date}"
        )
    return 0


def cmd_list_payments(args, storage: Storage) -> int:
    payments = storage.load().payments
    if not payments:
        print("No payments.")
        return 0
    print(
        f"{'ID':<12} {'Date':<12} {'Amount':<10} {'Type':<10} {'Payee':<26} {'Reference'}"
    )
    print("-" * 80)
    for p in payments:
        print(
            f"{p.id:<12} {p.date:<12} ${p.amount:<9.2f} {p.payment_type:<10} "
            f"{p.payee:<26} {p.reference_id}"
        )
    return 0


def cmd_summary(args, storage: Storage) -> int:
    print(Summary(storage.load()).as_text())
    return 0


def cmd_calendar(args, storage: Storage) -> int:
    cal = PaymentCalendar(storage.load().bills)
    if args.range:
        start = parse_date(args.range[0])
        end = parse_date(args.range[1])
        if end < start:
            print("End date must be on or after start date", file=sys.stderr)
            return 1
        print(cal.render_range(start, end))
    else:
        print(cal.render(args.year, args.month))
    return 0


def cmd_export(args, storage: Storage) -> int:
    import os

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    files = export_all(storage.load())
    written = []
    for name, content in files.items():
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        written.append(path)
    for path in written:
        print(f"Wrote {path}")
    return 0


def cmd_delete_bill(args, storage: Storage) -> int:
    ok = storage.delete_bill(args.bill_id)
    if not ok:
        print(f"Bill {args.bill_id} not found", file=sys.stderr)
        return 1
    print(f"Deleted bill {args.bill_id}")
    return 0


COMMANDS = {
    "add-bill": cmd_add_bill,
    "add-eob": cmd_add_eob,
    "add-payment": cmd_add_payment,
    "pay-bill": cmd_pay_bill,
    "list-bills": cmd_list_bills,
    "list-eobs": cmd_list_eobs,
    "list-payments": cmd_list_payments,
    "summary": cmd_summary,
    "calendar": cmd_calendar,
    "export": cmd_export,
    "delete-bill": cmd_delete_bill,
}


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = Storage(args.data_dir)
    return COMMANDS[args.command](args, storage)


if __name__ == "__main__":
    raise SystemExit(main())
