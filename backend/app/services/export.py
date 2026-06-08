import csv
import json
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ExportService:
    @staticmethod
    def export_json(data: dict) -> bytes:
        return json.dumps(data, indent=2).encode('utf-8')

    @staticmethod
    def export_csv(data: dict) -> bytes:
        # Simplistic CSV export assuming data is a list of dicts under a main key
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Flatten simple structures
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                headers = value[0].keys()
                writer.writerow([f"--- {key} ---"])
                writer.writerow(headers)
                for row in value:
                    writer.writerow([row.get(h, "") for h in headers])
                writer.writerow([])
            else:
                writer.writerow([key, value])
                
        return output.getvalue().encode('utf-8')

    @staticmethod
    def export_excel(data: dict) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = "Overview"
        
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                sheet = wb.create_sheet(title=key[:31])
                headers = list(value[0].keys())
                sheet.append(headers)
                for row in value:
                    sheet.append([str(row.get(h, "")) for h in headers])
            else:
                ws.append([key, str(value)])
                
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @staticmethod
    def export_pdf(data: dict, title: str = "Report") -> bytes:
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"Palladium Automation - {title}")
        c.setFont("Helvetica", 10)
        c.drawString(50, 730, f"Generated: {data.get('generated_at', 'N/A')}")
        
        y = 700
        for key, value in data.items():
            if key == 'generated_at': continue
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{key}:")
            y -= 20
            c.setFont("Helvetica", 10)
            if isinstance(value, list):
                for item in value[:10]: # Limit to avoid pagination logic in simple mock
                    c.drawString(70, y, str(item))
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = 750
            else:
                c.drawString(70, y, str(value))
                y -= 20
            
            y -= 10
            if y < 50:
                c.showPage()
                y = 750
                
        c.save()
        return output.getvalue()