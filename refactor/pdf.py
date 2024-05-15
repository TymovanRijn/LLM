from fpdf import FPDF
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, 'Offerte', 0, 1, 'C')
        self.set_font("Arial", "", 10)
        self.cell(0, 10, 'WebShrines', 0, 1, 'C')
        self.cell(0, 10, 'Adres, Postcode, Plaats', 0, 1, 'C')
        self.cell(0, 10, 'Telefoonnummer, Emailadres', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def table_row(self, header, value):
        self.set_font("Arial", "B", 12)
        self.cell(60, 10, header, border=1)
        self.set_font("Arial", "", 12)
        self.cell(0, 10, str(value), border=1)
        self.ln()