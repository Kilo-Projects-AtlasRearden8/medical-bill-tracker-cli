# Medical Bill Tracker CLI

A local-first, no-keys Python command-line tool for tracking medical bills,
Explanations of Benefits (EOBs), insurance payments, and due dates. Built and
credited to **Asdale Dynamics, LLC** (Indiana, formed October 2026) — part of
Dylan Asdale's open-source small-business and life-admin tooling. Plain
English, tested, local-first, no secrets or personal data stored anywhere but
your own machine.

## What it does

- Track medical bills: provider, amount due, amount paid, due date, status,
  category, notes, and linked EOB reference.
- Track EOBs: claim number, provider, date of service, billed/allowed amounts,
  insurance paid, patient responsibility, received date.
- Record payments (patient or insurance) against bills or claims.
- Print balance summaries: totals billed/paid/outstanding, by provider, by
  status, overdue bills, and bills due in the next 30 days.
- Print a printable monthly payment calendar (unpaid due dates marked with `*`),
  including a date-range mode for printing multiple months.
- Export all data to CSV (`bills.csv`, `eobs.csv`, `payments.csv`) in any
  directory you choose.
- Everything is stored in a single local JSON file. No accounts, no API keys,
  no network calls, no personal data leaves your computer.

## Install

```bash
git clone <this-repo>
cd medical-bill-tracker-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Or just run the module directly without installing:

```bash
python3 -m medical_bill_tracker.cli --help
```

## Usage

Data is stored in `~/.medical_bill_tracker/tracker.json` by default. Use
`--data-dir` to keep it anywhere (for example, inside a project folder).

Add a bill:

```bash
python3 -m medical_bill_tracker.cli add-bill \
  --provider "City Clinic" --amount 240.00 --due 2026-12-15 \
  --category visit --notes "Follow-up appointment"
```

Add an EOB:

```bash
python3 -m medical_bill_tracker.cli add-eob \
  --claim CLM-998877 --provider "City Clinic" --date-of-service 2026-11-01 \
  --billed 300.00 --allowed 240.00 --insurance-paid 192.00 --patient-owes 48.00
```

Record a payment:

```bash
python3 -m medical_bill_tracker.cli add-payment \
  --amount 48.00 --payee "City Clinic" --type patient --reference CLM-998877
```

Apply a payment to a specific bill:

```bash
python3 -m medical_bill_tracker.cli pay-bill --id <bill-id> --amount 120.00
```

List unpaid bills:

```bash
python3 -m medical_bill_tracker.cli list-bills --status unpaid
```

Print the balance summary:

```bash
python3 -m medical_bill_tracker.cli summary
```

Print this month's payment calendar:

```bash
python3 -m medical_bill_tracker.cli calendar
```

Print a printable range of months:

```bash
python3 -m medical_bill_tracker.cli calendar --range 2026-11-01 2026-12-31
```

Export to CSV:

```bash
python3 -m medical_bill_tracker.cli export --out ./export
```

## Tests

```bash
python3 -m pytest
```

Tests cover date parsing, bill balance/paid status, overdue logic, summary
totals and aging, JSON storage round-trips, EOBs/payments, calendar rendering,
and CSV export shapes.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Dylan Asdale is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC. His book *The Massive AI Manual* and hub site
dylanasdale.github.io explain AI "like a friend would": plain English, step by
step, never condescending. The LLC publishes beginner-friendly AI education,
books and guides, practical tools, small-business and author tooling, and
accessible life-admin helpers. This healthcare paperwork helper is education
only — it is not medical advice.
