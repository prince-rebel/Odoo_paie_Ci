#-*- coding:utf-8 -*-
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)

class ReportPayBook(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_pay_book_xls'
    _description = "Livre de paie"
    _inherit = 'report.report_xlsx.abstract'

    # Formattage pour les headers
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'silver',
        'text_wrap': 1
    }

    content_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
        'num_format': '### ### ##0'
    }

    amount_format = {
        'bold': 1,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '### ### ##0'
    }

    def formatSheet(self, sheet):
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 40)
        sheet.set_column('C:BZ', 20)

    def generateHeaders(self, sheet, headers, header_format):
        i = 3
        col = 0
        sheet.set_row(i, 40)
        sheet.write_row(i, col, headers, header_format)
        i += 1

    def generateLines(self, sheet, lines, amount_format, content_format):
        row = 4
        for line in lines:
            col = 1

            sheet.write(row, 0, line['matricule'], content_format)
            sheet.write(row, 1, line['name'], content_format)
            for amount in line['data']:
                col += 1
                sheet.write(row, col, amount, amount_format)
            row += 1
        return row

    def generateLinesTotaux(self, sheet, row, totals, amount_format, content_format):
        col = 0
        sheet.merge_range(row, col, row, col + 1, 'TOTAUX', content_format)
        col += 2
        sheet.write_row(row, col, totals, amount_format)

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('LIVRE DE PAIE')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(self.header_format)
        content_format = workbook.add_format(self.content_format)
        amount_format = workbook.add_format(self.amount_format)
        title = data['title']
        sheet.merge_range(0, 0, 0, 2, title, bold)
        self.formatSheet(sheet)
        self.generateHeaders(sheet, data['header'], header_format)

        row = self.generateLines(sheet,data['lines'], amount_format, content_format)
        self.generateLinesTotaux(sheet, row, data['totals'], amount_format, content_format)
        workbook.close()
