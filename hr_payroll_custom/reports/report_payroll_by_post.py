# -*- coding:utf-8 -*-

from odoo import models, api, _

class PayrollByPost(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_payroll_by_post_xls'
    _description = "Rapport des rubriques par période"
    _inherit = 'report.report_xlsx.abstract'

    # Formattage pour les headers
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'white',
        'text_wrap': 1,
        'font_name': 'Calibri',
        'font_size': 16
    }

    sub_header_format = {
        'bold': 0,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'white',
        'text_wrap': 1,
        'font_name': 'Calibri',
        'font_size': 13
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

    sub_amount_format = {
        'bold': 0,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '### ### ##0'
    }

    def formatSheet(self, sheet):
        sheet.set_default_row(16)
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:G', 13)

    def generateHeaders(self, sheet, data, header_format, sub_header_format):
        sheet.merge_range('A1:G1', 'ETAT DES RUBRIQUES', header_format)
        sheet.write(2, 0, 'Période', sub_header_format)
        sheet.write(2, 1, data[0]['date_from'], sub_header_format)
        sheet.write(2, 2, ' - ', sub_header_format)
        sheet.write(2, 3, data[0]['date_to'], sub_header_format)
        sheet.write(3, 0, 'Rubrique Code ', sub_header_format)
        sheet.write(3, 1, data[0]['rubrique'], sub_header_format)
        sheet.write(3, 3, 'Rubrique', sub_header_format)
        sheet.merge_range('E4:F4', data[0]['rule_id'], sub_header_format)

    def generateLines(self, sheet, data_lines, content_format, sub_amount_format):
        cumulative_earnings = 0
        cumulative_deductions = 0
        line = 5
        sheet.write(line, 0, 'MATRICULE', content_format)
        sheet.write(line, 1, 'Nom et Prénoms', content_format)
        sheet.write(line, 2, 'Base', content_format)
        sheet.write(line, 3, 'Quantité', content_format)
        sheet.write(line, 4, 'Taux (%)', content_format)
        sheet.write(line, 5, 'Retenues', content_format)
        sheet.write(line, 6, 'Gains', content_format)
        line += 1
        for rec in data_lines:
            sheet.write(line, 0, rec['matricule'] or '', content_format)
            sheet.write(line, 1, rec['full_name'], content_format)
            sheet.write(line, 2, rec['base'], content_format)
            sheet.write(line, 3, rec['quantity'], content_format)
            sheet.write(line, 4, rec['taux'], content_format)
            sheet.write(line, 5, '', content_format)
            sheet.write(line, 6, '', content_format)
            if rec['imputation_type'] == 'deductions':
                sheet.write(line, 5, rec['amount'], sub_amount_format)
                cumulative_deductions += rec['amount']
            if rec['imputation_type'] == 'earnings':
                sheet.write(line, 6, rec['amount'], sub_amount_format)
                cumulative_earnings += rec['amount']
            line += 1
        return line, cumulative_deductions, cumulative_earnings

    def generateLinesTotaux(self, sheet, row, cumulative_deductions, cumulative_earnings, content_format):
        col = 4
        sheet.write(row, col, 'Total Général', content_format)
        sheet.write(row, col + 1, cumulative_deductions, content_format)
        sheet.write(row, col + 2, cumulative_earnings, content_format)

    def generate_xlsx_report(self, workbook, data, obj):
        data_header = data['details_report']
        data_lines = data['res']
        sheet = workbook.add_worksheet('Rubrique de paie par position')
        self.formatSheet(sheet)
        header_format = workbook.add_format(self.header_format)
        sub_header_format = workbook.add_format(self.sub_header_format)
        content_format = workbook.add_format(self.content_format)
        amount_format = workbook.add_format(self.amount_format)
        sub_amount_format = workbook.add_format(self.sub_amount_format)
        self.generateHeaders(sheet, data_header, header_format, sub_header_format)
        row, cumulative_deductions, cumulative_earnings= self.generateLines(sheet, data_lines, content_format, sub_amount_format)
        self.generateLinesTotaux(sheet,row, cumulative_deductions, cumulative_earnings, amount_format)
        workbook.close()
