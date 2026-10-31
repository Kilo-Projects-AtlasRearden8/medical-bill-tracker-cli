# STATUS — Medical Bill Tracker CLI

## What was built

A local-first Python command-line tool for tracking medical bills,
Explanations of Benefits (EOBs), insurance payments, and due dates. Built and
credited to **Asdale Dynamics, LLC** (Indiana, formed October 2026).

Package `medical_bill_tracker/` with modules:
- `models.py` — Bill, EOB, Payment, TrackerData dataclasses; date parse/format helpers
- `storage.py` — atomic JSON read/write (`tracker.json`), add/list/pay/delete helpers, date validation
- `summary.py` — balance totals, by-provider and by-status breakdowns, overdue and upcoming (next 30 days) bill lists, plain-text report
- `calendar_view.py` — printable monthly payment calendar (unpaid due dates marked with `*`) plus a date-range mode for printing multiple months
- `csv_export.py` — CSV export of bills, EOBs, and payments
- `cli.py` — argparse CLI: add-bill, add-eob, add-payment, pay-bill, list-bills, list-eobs, list-payments, summary, calendar, export, delete-bill; `--data-dir` flag (default `~/.medical_bill_tracker`, tilde-expanded)
- `__main__.py` — enables `python3 -m medical_bill_tracker`

Other files: `tests/test_tracker.py` (12 tests), `LICENSE` (MIT), `README.md`,
`.gitignore`, `pyproject.toml` (with `medical-bill-tracker` console script).

Local-first, no API keys, no secrets, no personal data, no network access,
no `.github/workflows`. Standard library only — no third-party dependencies.

## How to run

```bash
cd medical-bill-tracker-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

python3 -m medical_bill_tracker.cli --help
# or
python3 -m medical_bill_tracker --help

python3 -m medical_bill_tracker.cli add-bill --provider "City Clinic" \
  --amount 240.00 --due 2026-12-15
python3 -m medical_bill_tracker.cli summary
python3 -m medical_bill_tracker.cli calendar --year 2026 --month 12
python3 -m medical_bill_tracker.cli export --out ./export
python3 -m pytest
```

Data lives in `~/.medical_bill_tracker/tracker.json` unless `--data-dir` is set.

## Verification results

- `python3 -m pytest`: 12 passed (date round-trip, bill balance/paid status,
  overdue logic, summary totals + by-provider + by-status, upcoming/overdue
  aging, JSON storage round-trip incl. mark-paid/delete, EOBs/payments,
  calendar rendering, CSV export shapes, invalid-date rejection,
  pay-bill creates a payment record)
- `python3 -m py_compile medical_bill_tracker/*.py tests/*.py`: OK
- `ruff check`: 0 errors
- `ruff format --check`: all files formatted
- Manual CLI smoke test: add-bill/add-eob/add-payment/pay-bill/list-bills/
  list-eobs/list-payments/summary/calendar/calendar --range/export/delete-bill
  all ran correctly against a temp data dir; pay-bill creates a Payment
  record (audit trail); invalid dates are rejected with a friendly message;
  default `--data-dir` tilde expansion works (`~/.medical_bill_tracker`);
  `python3 -m medical_bill_tracker` works via `__main__.py`.
- Packaging: `pip install -e .` requires `--break-system-packages` on this
  host (PEP 668 externally managed environment); use a venv (documented in
  README). Console script entry point `medical-bill-tracker` is defined in
  pyproject.toml.

## Critical fix since initial release

The default `--data-dir` value `~/.medical_bill_tracker` was not tilde-
expanded, so running without `--data-dir` created a literal `~` folder in the
current directory. Fixed by expanding the user path in `main()` (cli.py).

## Known gaps

- No web GUI — CLI only; printable calendar is plain text (suitable for
  printing to a terminal or printer).
- Currency stored as float rounded to 2 decimals — fine for a personal
  tracker, not for double-entry bookkeeping.
- No data migration or schema versioning if the model changes later.
- Recurring bills, payment reminders/notifications, and PDF output not yet
  implemented.
- EOB patient-owes is tracked independently of bills; linking an EOB to a bill
  is by reference id string only, no enforced relationship.

## Credits and license

Built by and credited to Asdale Dynamics, LLC (Indiana, formed October 2026).
MIT License: Copyright (c) 2026 Asdale Dynamics, LLC. Healthcare use is
education only — not medical advice.
