# -*- coding:utf-8 -*-

import datetime
from odoo import models, api, _


class CMURapportXlsx(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_list_insured_cmu_xls'
    _description = "Liste des assurés CMU"
    _inherit = 'report.report_xlsx.abstract'

    #i = 0

    # Formattage pour les headers
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#afafaf',
        'text_wrap': 1
    }

    content_format_left = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
        'font_name': 'Helvetica'
    }
    content_format_right = {
        'bold': 0,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'fg_color': 'white',
        'font_name': 'Helvetica'
    }

    date_format = {
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': 'dd/mm/yyyy',
        'font_name': 'Helvetica'
    }

    headers = (
        "NUMERO CNPS ASSURE",
        "NUMERO SECURITE SOCIALE ASSURE",
        "NOM ASSURE",
        "PRENOMS ASSURE",
        "DATE DE NAISSANCE ASSURE",
        "NUMERO CNPS BENEFICIAIRE",
        "NUMERO SECURITE SOCIALE BENEFICIAIRE",
        "TYPE BENEFICIAIRE\nC: CONJOINT\nT: TRAVAILLEUR\nE: ENFANT",
        "NOM BENEFICIAIRE",
        "PRENOMS BENEFICIAIRE",
        "DATE DE NAISSANCE BENEFICIAIRE",
        "GENRE BENEFICIAIRE\nH: HOMME\nF: FEMME"
    )

    def formatSheet(self, sheet):
        sheet.set_column('A:B', 15)
        sheet.set_column('C:C', 35)
        sheet.set_column('D:D', 55)
        sheet.set_column('E:G', 15)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 35)
        sheet.set_column('J:J', 55)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)

    def generateHeaders(self, sheet, header_format):
        row = 0
        col = 0
        sheet.set_row(0, 70)
        for x in range(len(self.headers)):
            sheet.write(row, col, self.headers[x], header_format)
            col += 1
        row += 1
        return row

    def generateLines(self, sheet, row, lines, content_format_left, content_format_right, date_format):
        for line in lines:
            sexe = "H"
            sheet.write(row, 0, line.identification_cnps or '', content_format_right)
            sheet.write(row, 1, line.identification_cmu or '', content_format_left)
            sheet.write(row, 2, line.name.upper() if line.name else '', content_format_left)
            sheet.write(row, 3, line.first_name.upper() if line.first_name else '', content_format_left)
            sheet.write(row, 4, line.birthday or '', date_format)
            sheet.write(row, 5, line.identification_cnps or '', content_format_right)
            sheet.write(row, 6, line.num_cmu_beneficiary or '', content_format_left)
            sheet.write(row, 7, str(line.type).upper(), content_format_left)
            sheet.write(row, 8, line.name_beneficiary.upper() if line.name_beneficiary else '', content_format_left)
            sheet.write(row, 9, line.first_name_beneficiary.upper() if line.first_name_beneficiary else '', content_format_left)
            sheet.write(row, 10, line.birthday_beneficiary or '', date_format)
            if line.gender != 'male':
                sexe = "F"
            sheet.write(row, 11, sexe, content_format_left)
            row += 1

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('CMU')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(self.header_format)
        content_format_left = workbook.add_format(self.content_format_left)
        content_format_right = workbook.add_format(self.content_format_right)
        date_format = workbook.add_format(self.date_format)
        self.formatSheet(sheet)
        #self.i = 0
        row = self.generateHeaders(sheet, header_format)
        if obj.line_ids:
            self.generateLines(sheet, row, obj.line_ids, content_format_left, content_format_right, date_format)
        workbook.close()
