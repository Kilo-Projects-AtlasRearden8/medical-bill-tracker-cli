# Medical Bill Tracker CLI

A friendly, local-first command-line tool for tracking medical bills,
Explanations of Benefits (EOBs), insurance payments, and due dates — built
and credited to **Asdale Dynamics, LLC** (Indiana, formed October 2026).

This is part of Dylan Asdale's open-source small-business and life-admin
tooling. Dylan is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC. His book *The Massive AI Manual* and hub site
dylanasdale.github.io explain AI "like a friend would": plain English, step
by step, never condescending.

Plain English, tested, local-first. No accounts, no API keys, no network
calls, and no personal data ever leaves your computer. Everything lives in a
single JSON file on your own machine.

**Education only.** This tool helps you organize paperwork. It is not medical
advice, billing advice, or a substitute for talking with your provider or
insurer.

## Who this is for

Anyone who wants a simple, no-frills way to stay on top of medical paperwork:
- Nurses and healthcare workers tracking their own bills and EOBs
- People managing a family's medical expenses
- Small-business owners and freelancers keeping health costs organized
- Anyone who likes low-energy, ADHD-friendly tools that do one thing well

## What it does

- **Track medical bills** — provider, amount due, amount paid, due date,
  status, category, notes, and a linked EOB reference.
- **Track EOBs** — claim number, provider, date of service, billed/allowed
  amounts, insurance paid, patient responsibility, received date.
- **Record payments** — patient or insurance payments, with an optional link
  back to a bill or claim.
- **Pay a bill** — apply a payment to a specific bill and watch the balance
  and status update automatically (a payment record is created too).
- **List bills, EOBs, and payments** — filter bills by status.
- **Print a balance summary** — totals billed/paid/outstanding, by provider,
  by status, overdue bills, and bills due in the next 30 days, plus EOB
  patient-responsibility and insurance-paid totals.
- **Print a payment calendar** — a printable monthly calendar with unpaid due
  dates marked by `*`. Print one month or a range of months.
- **Export to CSV** — `bills.csv`, `eobs.csv`, and `payments.csv` to any
  folder you choose.

Everything is stored in one local JSON file (`tracker.json` by default). No
accounts, no API keys, no network calls, no personal data leaves your
computer.

## Install

You need Python 3.9 or newer. No extra packages are required — the tool uses
only Python's standard library.

```bash
git clone <this-repo>
cd medical-bill-tracker-cli
```

### Option A: run without installing (quickest)

```bash
python3 -m medical_bill_tracker.cli --help
```

### Option B: install into a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then the `medical-bill-tracker` command is available everywhere:

```bash
medical-bill-tracker --help
```

## Your data

By default, data is stored in `~/.medical_bill_tracker/tracker.json`. To keep
your data somewhere else (for example, inside a project folder), use
`--data-dir`:

```bash
medical-bill-tracker --data-dir ./my-health-data summary
```

## Step-by-step: a full workflow

Here's a friendly walkthrough from start to finish.

**1. Add a bill** from a provider:

```bash
medical-bill-tracker add-bill \
  --provider "City Clinic" \
  --amount 240.00 \
  --due 2026-12-15 \
  --category visit \
  --notes "Follow-up appointment"
```

You'll get back a short bill ID (like `9a08f3624f1f`). Keep it handy — you'll
use it when you pay the bill.

**2. Add an EOB** from your insurer:

```bash
medical-bill-tracker add-eob \
  --claim CLM-998877 \
  --provider "City Clinic" \
  --date-of-service 2026-11-01 \
  --billed 300.00 \
  --allowed 240.00 \
  --insurance-paid 192.00 \
  --patient-owes 48.00
```

**3. Record a payment** you made:

```bash
medical-bill-tracker add-payment \
  --amount 48.00 \
  --payee "City Clinic" \
  --type patient \
  --reference CLM-998877
```

**4. Apply a payment to a specific bill** (using the bill ID from step 1):

```bash
medical-bill-tracker pay-bill --id 9a08f3624f1f --amount 120.00
```

This updates the bill's balance and status, and creates a payment record so
you have an audit trail.

**5. See where you stand:**

```bash
medical-bill-tracker list-bills --status unpaid
medical-bill-tracker summary
medical-bill-tracker calendar
```

**6. Export your data** to CSV whenever you like:

```bash
medical-bill-tracker export --out ./my-export
```

## Command reference

| Command | What it does |
|---------|--------------|
| `add-bill` | Add a medical bill (`--provider`, `--amount`, `--due`) |
| `add-eob` | Add an Explanation of Benefits (`--claim`, `--provider`) |
| `add-payment` | Record a patient or insurance payment |
| `pay-bill` | Apply a payment to a specific bill (`--id`, `--amount`) |
| `list-bills` | List bills (optional `--status`) |
| `list-eobs` | List all EOBs |
| `list-payments` | List all payments |
| `summary` | Print balance totals and aging |
| `calendar` | Print a monthly payment calendar (`--year`, `--month`, or `--range`) |
| `export` | Export bills, EOBs, and payments to CSV (`--out`) |
| `delete-bill` | Delete a bill by ID (`--id`) |

Run `medical-bill-tracker <command> --help` for details on any command.

## Tests

```bash
python3 -m pytest
```

Tests cover date parsing, bill balance and paid status, overdue logic,
summary totals and aging, JSON storage round-trips, EOBs and payments,
calendar rendering, and CSV export shapes.

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About Asdale Dynamics, LLC

Dylan Asdale is a registered nurse turned AI author and founder of Asdale
Dynamics, LLC (Indiana, formed October 2026). His book *The Massive AI Manual*
and hub site dylanasdale.github.io explain AI "like a friend would": plain
English, step by step, never condescending.

The LLC publishes beginner-friendly AI education, books and guides, and
practical tools — including small-business and author tools (KDP, marketing,
reselling, bookkeeping) and accessible life-admin helpers like this one.

This healthcare paperwork helper is published by Asdale Dynamics, LLC for
education only. It is not medical advice.
