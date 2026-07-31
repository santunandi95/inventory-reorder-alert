
import csv
import os
import sys
import io
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


INPUT_FILE        = "stock_data.csv"
OUTPUT_REPORT_CSV = "restock_report.csv"
CRITICAL_THRESHOLD_PCT = 0.25   

def load_stock_data(filepath: str) -> tuple[list[dict], list[str]]:
    """
    Reads the CSV file and returns:
      - A list of cleaned stock-item dictionaries.
      - A list of warning strings for skipped / malformed rows.
    """
    items    : list[dict] = []
    warnings : list[str]  = []

    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)

        
        required_cols = {"item_name", "current_quantity", "reorder_threshold"}
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            print(f"[ERROR] Missing columns in CSV: {missing}")
            sys.exit(1)

        for row_num, row in enumerate(reader, start=2):   
            item = parse_row(row, row_num, warnings)
            if item:
                items.append(item)

    return items, warnings


def parse_row(row: dict, row_num: int, warnings: list[str]) -> dict | None:
    """
    Validates and normalises a single CSV row.
    Returns a clean dict or None if the row must be skipped.
    """
    name = row.get("item_name", "").strip()
    if not name:
        warnings.append(f"Row {row_num}: Skipped — missing item name.")
        return None

    # Parse current_quantity
    try:
        qty = float(row.get("current_quantity", "").strip())
        if qty < 0:
            warnings.append(f"Row {row_num} ({name}): Negative quantity treated as 0.")
            qty = 0.0
    except (ValueError, AttributeError):
        warnings.append(f"Row {row_num} ({name}): Missing/invalid quantity — treated as 0.")
        qty = 0.0

    # Parse reorder_threshold
    try:
        threshold = float(row.get("reorder_threshold", "").strip())
        if threshold <= 0:
            warnings.append(f"Row {row_num} ({name}): Non-positive threshold — row skipped.")
            return None
    except (ValueError, AttributeError):
        warnings.append(f"Row {row_num} ({name}): Missing/invalid threshold — row skipped.")
        return None

    # Parse healthy_stock_level (optional)
    try:
        healthy = float(row.get("healthy_stock_level", "").strip())
    except (ValueError, AttributeError):
        healthy = threshold * 3   

    return {
        "item_name"          : name,
        "current_quantity"   : qty,
        "reorder_threshold"  : threshold,
        "healthy_stock_level": healthy,
        "unit"               : row.get("unit", "units").strip() or "units",
        "category"           : row.get("category", "Uncategorised").strip() or "Uncategorised",
    }



def classify_item(item: dict) -> dict | None:
    
    qty       = item["current_quantity"]
    threshold = item["reorder_threshold"]
    healthy   = item["healthy_stock_level"]

    if qty >= threshold:
        return None   # stock is fine

    critical_mark = threshold * CRITICAL_THRESHOLD_PCT
    priority      = "🔴 CRITICAL" if qty < critical_mark else "🟡 LOW"

    # BONUS: Reorder quantity suggestion
    reorder_qty = max(0, healthy - qty)

    return {
        **item,
        "priority"   : priority,
        "reorder_qty": int(reorder_qty),
        "shortage"   : int(threshold - qty),
    }


def analyse_stock(items: list[dict]) -> list[dict]:
    """Runs classify_item over every item; returns only those needing restock."""
    return [result for item in items if (result := classify_item(item)) is not None]


DIVIDER  = "═" * 72
THIN_DIV = "─" * 72

def print_console_report(flagged: list[dict], warnings: list[str], run_time: str) -> None:
    """Prints a formatted restock report to the console."""

    critical_items = [i for i in flagged if "CRITICAL" in i["priority"]]
    low_items      = [i for i in flagged if "LOW"      in i["priority"]]

    print(f"\n{DIVIDER}")
    print(f"  [BOX] INVENTORY REORDER ALERT REPORT")
    print(f"  Generated : {run_time}")
    print(f"  Input     : {INPUT_FILE}")
    print(DIVIDER)
    print(f"  Items needing restock : {len(flagged)}")
    print(f"  [!!] Critical         : {len(critical_items)}")
    print(f"  [!]  Low              : {len(low_items)}")
    print(DIVIDER)

    if not flagged:
        print("\n  [OK] All stock levels are above their reorder thresholds. No action needed.\n")
        return

    # Group by category for readability
    categories = {}
    for item in flagged:
        categories.setdefault(item["category"], []).append(item)

    for category, cat_items in sorted(categories.items()):
        print(f"\n  [FOLDER] {category.upper()}")
        print(f"  {THIN_DIV}")
        print(f"  {'Item':<30} {'Priority':<12} {'Qty':>6} {'Threshold':>10} {'Reorder':>8} {'Unit':<10}")
        print(f"  {THIN_DIV}")
        for i in sorted(cat_items, key=lambda x: x["current_quantity"]):
            priority_label = "[!!] CRITICAL" if "CRITICAL" in i["priority"] else "[!]  LOW"
            print(
                f"  {i['item_name']:<30} {priority_label:<12} "
                f"{int(i['current_quantity']):>6} {int(i['reorder_threshold']):>10} "
                f"{i['reorder_qty']:>8} {i['unit']:<10}"
            )

    if warnings:
        print(f"\n  {THIN_DIV}")
        print(f"  [!] DATA WARNINGS ({len(warnings)})")
        print(f"  {THIN_DIV}")
        for w in warnings:
            print(f"  * {w}")

    print(f"\n{DIVIDER}\n")



def format_email_alert(flagged: list[dict], run_time: str) -> str:
    """
    Returns a string that mimics a restock-alert email
    (Subject + Body) — ready to hand to smtplib or any mailer.
    """
    critical_items = [i for i in flagged if "CRITICAL" in i["priority"]]
    low_items      = [i for i in flagged if "LOW"      in i["priority"]]

    subject = (
        f"[RESTOCK ALERT] {len(flagged)} items need attention "
        f"({len(critical_items)} CRITICAL) — {run_time[:10]}"
    )

    lines = [
        "=" * 60,
        f"  TO      : warehouse-manager@company.com",
        f"  FROM    : inventory-bot@company.com",
        f"  SUBJECT : {subject}",
        "=" * 60,
        "",
        "Hello,",
        "",
        f"This is your automated daily inventory check for {run_time[:10]}.",
        f"A total of {len(flagged)} item(s) are below their reorder threshold.",
        "",
    ]


    if critical_items:
        lines.append("[!!] CRITICAL -- Order Immediately:")
        lines.append("-" * 40)
        for i in critical_items:
            lines.append(
                f"  * {i['item_name']}: {int(i['current_quantity'])} {i['unit']} remaining "
                f"(threshold {int(i['reorder_threshold'])}). "
                f"Suggest ordering {i['reorder_qty']} {i['unit']}."
            )
        lines.append("")

    if low_items:
        lines.append("[!] LOW -- Plan to Reorder Soon:")
        lines.append("-" * 40)
        for i in low_items:
            lines.append(
                f"  * {i['item_name']}: {int(i['current_quantity'])} {i['unit']} remaining "
                f"(threshold {int(i['reorder_threshold'])}). "
                f"Suggest ordering {i['reorder_qty']} {i['unit']}."
            )
        lines.append("")

    lines += [
        "Please coordinate with the relevant suppliers as soon as possible.",
        "",
        "This is an automated message — do not reply directly.",
        "Inventory Alert System v1.0",
        "=" * 60,
    ]

    return "\n".join(lines)



def export_csv_report(flagged: list[dict], filepath: str, run_time: str) -> None:
    """Writes the flagged items to a restock_report.csv file."""
    fieldnames = [
        "item_name", "category", "priority",
        "current_quantity", "reorder_threshold",
        "shortage", "reorder_qty", "healthy_stock_level",
        "unit", "report_generated",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in flagged:
            row = {**item, "report_generated": run_time}
            # Strip emoji from priority for clean CSV
            row["priority"] = row["priority"].replace("🔴 ", "").replace("🟡 ", "")
            writer.writerow(row)

    print(f"  [OK] CSV report exported -> {filepath}")



def main() -> None:
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n  [*] Running inventory check at {run_time} ...")

    # Step 1 -- Load data
    items, warnings = load_stock_data(INPUT_FILE)
    print(f"  [*] Loaded {len(items)} valid item(s) from '{INPUT_FILE}'.")

    # Step 2 -- Analyse
    flagged = analyse_stock(items)

    # Step 3 -- Console report
    print_console_report(flagged, warnings, run_time)

    # Step 4 -- Email simulation (always print so the output is visible)
    if flagged:
        email_body = format_email_alert(flagged, run_time)
        print("\n  [EMAIL] SIMULATED EMAIL ALERT")
        print(email_body)
    else:
        print("  [EMAIL] No email alert needed -- all stock levels are healthy.\n")

    # Step 5 -- Export CSV
    export_csv_report(flagged, OUTPUT_REPORT_CSV, run_time)


if __name__ == "__main__":
    main()
