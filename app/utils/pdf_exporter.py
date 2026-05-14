from fpdf import FPDF
import mailparser

class PDFExporter:
    @staticmethod
    def export_eml_to_pdf(eml_path, output_pdf_path):
        mail = mailparser.parse_from_file(eml_path)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ArchyPEC - Messaggio Esportato", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Oggetto: {mail.subject}", ln=True)
        pdf.cell(0, 10, f"Mittente: {mail.from_}", ln=True)
        pdf.cell(0, 10, f"Data: {mail.date}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", size=10)
        body = mail.text_plain[0] if mail.text_plain else "Nessun testo disponibile."
        pdf.multi_cell(0, 10, body)

        pdf.output(output_pdf_path)
        return output_pdf_path
