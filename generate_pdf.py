import os
from fpdf import FPDF

class ProjectPDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font("helvetica", "B", 15)
        # Title
        self.cell(0, 10, "INVENTORY REORDER ALERT SYSTEM - ASSESSMENT REPORT", border=0, align="C")
        # Line break
        self.ln(15)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font("helvetica", "I", 8)
        # Page number
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", border=0, align="C")

def create_pdf():
    pdf = ProjectPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title Section
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(0, 102, 204) # blue color
    pdf.cell(0, 15, "Assessment Submission Form", ln=True, align="L")
    pdf.ln(5)
    
    # Metadata Table/Block
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(50, 8, "Project Name:", border=1)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "Inventory Reorder Alert System", border=1, ln=True)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(50, 8, "Repository URL:", border=1)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "https://github.com/santunandi95/inventory-reorder-alert", border=1, ln=True)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(50, 8, "Author:", border=1)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "santunandi95", border=1, ln=True)

    pdf.set_font("helvetica", "B", 12)
    pdf.cell(50, 8, "Date:", border=1)
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "2026-07-31", border=1, ln=True)
    pdf.ln(10)

    # 1. Approach Summary Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "1. Approach Summary", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 10)
    
    summary_text = (
        "Reads 'stock_data.csv' into validated dictionaries, safely handling missing, negative, or malformed "
        "data by logging warnings and applying fallback values. Compares current stock against thresholds to "
        "classify priorities into 'Critical' (<25% of threshold) vs 'Low' tiers, and calculates the required "
        "reorder quantity to reach a healthy level. Generates a clean category-grouped console report, prints a "
        "simulated email alert, and exports the results to a structured 'restock_report.csv' file."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(8)

    # 2. File Structure
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "2. Project Files Created", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 10)
    
    files_text = (
        "- inventory_reorder_alert.py: Main script containing core file handling, validation, logic, and email simulation.\n"
        "- stock_data.csv: Warehouse stock CSV loaded with 25 test items (including standard values and edge-case samples).\n"
        "- restock_report.csv: Machine-readable output generated containing the low-stock alert list.\n"
        "- README.md: Detailed documentation of parameters, logic, approach, and future extension ideas."
    )
    pdf.multi_cell(0, 6, files_text)
    pdf.ln(8)

    # 3. Source Code Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "3. Python Source Code (inventory_reorder_alert.py)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("courier", "", 8.5)
    
    with open("inventory_reorder_alert.py", "r", encoding="utf-8") as f:
        code_content = f.read()
    
    # We clean up non-ascii characters for Courier default PDF encoding compatibility
    code_content_cleaned = code_content.encode("ascii", "replace").decode("ascii")
    pdf.multi_cell(0, 4.5, code_content_cleaned)
    pdf.ln(8)

    # 4. Input Stock Data (stock_data.csv)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "4. Sample Input Data (stock_data.csv)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("courier", "", 9)
    
    with open("stock_data.csv", "r", encoding="utf-8") as f:
        csv_content = f.read()
        
    pdf.multi_cell(0, 5, csv_content.encode("ascii", "replace").decode("ascii"))
    pdf.ln(8)

    # 5. Output Verification Report (restock_report.csv)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "5. Output Generated Report (restock_report.csv)", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("courier", "", 9)
    
    with open("restock_report.csv", "r", encoding="utf-8") as f:
        out_csv_content = f.read()
        
    pdf.multi_cell(0, 5, out_csv_content.encode("ascii", "replace").decode("ascii"))
    pdf.ln(8)

    # 6. Reflection Note
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "6. Assessment Reflection & Future Scope", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "", 10)
    
    reflection_text = (
        "Given more time, the following improvements would be integrated:\n"
        "1. Scheduling: Establish automated execution triggers via system Cron or Windows Task Scheduler.\n"
        "2. Real Notification Service: Integrate SMTP relay or APIs like SendGrid/SES to dispatch warning digests.\n"
        "3. Supplier API/Integrations: Directly send draft Purchase Orders to pre-mapped vendors for low items.\n"
        "4. Historical Tracking & Smart Reorder Thresholds: Aggregate daily snapshots into a database to detect "
        "trends, calculate moving velocity, and adjust thresholds automatically to prevent stockouts."
    )
    pdf.multi_cell(0, 6, reflection_text)

    # Output to File
    pdf.output("Inventory_Reorder_Alert_Assessment.pdf")
    print("PDF Report Generated Successfully: Inventory_Reorder_Alert_Assessment.pdf")

if __name__ == "__main__":
    create_pdf()
