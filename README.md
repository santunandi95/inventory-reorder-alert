# 📦 Inventory Reorder Alert System

A Python automation script that reads a warehouse stock CSV, compares each item against its reorder threshold, classifies low-stock items by severity, and generates a clean daily restock report — plus a simulated email alert and an exported CSV summary.

---

## Features

| Feature | Description |
|---|---|
| **CSV File Handling** | Reads `stock_data.csv` into a list of dicts; validates columns on startup |
| **Dictionary-driven logic** | Each stock item lives in a clean Python dict throughout the pipeline |
| **Conditional classification** | Two priority tiers per item based on percentage below threshold |
| **Edge-case handling** | Missing names, blank quantities, negative values, non-positive thresholds |
| **Console report** | Grouped by category, sorted by quantity ascending, formatted table |
| **[BONUS] Simulated email** | Prints a full `To / From / Subject / Body` email alert to console |
| **[BONUS] Priority levels** | `CRITICAL` (< 25 % of threshold) vs `LOW` (< threshold but ≥ 25 %) |
| **[BONUS] Reorder qty suggestion** | Calculates `healthy_stock_level − current_quantity` per item |
| **[BONUS] CSV export** | Writes flagged items to `restock_report.csv` with timestamp |

---

## Quick Start

```bash
# No external dependencies — uses only the Python standard library
python inventory_reorder_alert.py
```

Two output files will be created / updated on each run:
- **Console** — full formatted report + simulated email
- **`restock_report.csv`** — machine-readable export of flagged items

---

## Input File: `stock_data.csv`

| Column | Required | Notes |
|---|---|---|
| `item_name` | Yes | Rows with a blank name are skipped with a warning |
| `current_quantity` | Yes | Blank or non-numeric → treated as 0, warning logged |
| `reorder_threshold` | Yes | Must be a positive number; rows that fail are skipped |
| `healthy_stock_level` | No | Fallback: `threshold × 3` if missing |
| `unit` | No | Display label (e.g. "boxes", "rolls"); defaults to "units" |
| `category` | No | Used for grouping in the report; defaults to "Uncategorised" |

---

## Priority Classification Logic

```
qty < threshold × 0.25   →  [!!] CRITICAL — order immediately
qty < threshold          →  [!]  LOW      — plan to reorder soon
qty >= threshold         →  OK (not flagged)
```

The 25 % boundary (`CRITICAL_THRESHOLD_PCT`) is configurable at the top of the script.

---

## Reorder Quantity Suggestion

```python
reorder_qty = max(0, healthy_stock_level - current_quantity)
```

This brings stock up to a "healthy" level defined per item in the CSV, not just back to the threshold.

---

## Output: `restock_report.csv`

Columns exported:

```
item_name, category, priority, current_quantity, reorder_threshold,
shortage, reorder_qty, healthy_stock_level, unit, report_generated
```

---

## Approach Summary

1. **Load** — `csv.DictReader` turns every row into a dict; malformed rows raise a warning and are skipped rather than crashing the script.
2. **Classify** — a single `classify_item()` function computes priority tier and reorder quantity using pure conditional arithmetic.
3. **Report** — items are grouped by category and sorted by quantity so the most urgent gaps appear at the top of each group.
4. **Export** — `csv.DictWriter` writes a timestamped CSV ready for import into any warehouse management or spreadsheet tool.
5. **Simulate alert** — the email formatter produces a ready-to-send message body that can be handed directly to `smtplib` with no changes.

---

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| Missing item name | Row skipped; warning logged |
| Blank / non-numeric quantity | Treated as 0; warning logged |
| Negative quantity | Clamped to 0; warning logged |
| Missing threshold | Row skipped; warning logged |
| Non-positive threshold | Row skipped; warning logged |
| Missing `healthy_stock_level` | Defaults to `threshold × 3` |
| Empty file / wrong columns | Prints error and exits cleanly |

---

## Reflection Note (Bonus)

With more time I would add:

1. **Scheduling** — wrap the script in a `cron` job (Linux) or Windows Task Scheduler entry so it runs automatically every morning without any manual trigger.
2. **Real email delivery** — swap the simulated email body into Python's `smtplib` / an SMTP-relay service (e.g. SendGrid) so the warehouse manager receives an actual inbox alert.
3. **Supplier integration** — link each item to a supplier ID and auto-generate a purchase order draft (e.g. via a REST API or an EDI feed) rather than just suggesting a quantity.
4. **Historical trend tracking** — append each run's snapshot to a time-series table so the script can detect accelerating consumption and raise the reorder threshold dynamically before stock actually runs out.
5. **Web dashboard** — a lightweight Flask/FastAPI endpoint serving the latest `restock_report.csv` as a live HTML table, giving the warehouse team a browser-based view without needing to open any file.

---

## Project Structure

```
Inventory-Reorder-Alert/
├── inventory_reorder_alert.py   # Main script
├── stock_data.csv               # Sample input (25 rows, intentional edge cases)
├── restock_report.csv           # Auto-generated on each run
└── README.md                    # This file
```

---

## GitHub Repository

https://github.com/santunandi95/inventory-reorder-alert
