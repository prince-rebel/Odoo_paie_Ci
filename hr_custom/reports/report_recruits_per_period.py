# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportRecruitsPerPeriod(models.AbstractModel):
    _name = 'report.hr_custom.report_recruits_per_period_wizard'
    _description = "Etat des recurtements par période"
    _inherit = 'report.report_xlsx.abstract'

    title = [
        "MTLE",
        "CATEGORIE",
        "STATUT",
        "NOM & PRENOMS",
        "FONCTION",
        "SERVICES",
        "DEPARTEMENTS",
        "DIRECTION",
        "SEXE",
        "EMBAUCHE",
        "NAISSANCE",
        "AGE",
        "NATURE DU CONTRAT",
    ]

    i = 0

    # Formattage pour les headers
    h_format = {
        'bold': 1,
        'border': 1,
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': 'silver',
        'text_wrap': 1,
        'font_name': 'Helvetica'
    }

    c_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
        'num_format': '# ##0',
        'font_name': 'Helvetica'
    }

    a_format = {
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'num_format': 'dd/mm/yy',
        'font_name': 'Helvetica'
    }

    def formatSheet(self, sheet):
        sheet.add_table('A1:M1', {'autofilter': True})
        sheet.set_default_row(30)
        sheet.set_row(0, 25)
        sheet.set_column('A:A', 13)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 11)
        sheet.set_column('D:D', 45)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 25)
        sheet.set_column('H:H', 25)
        sheet.set_column('I:I', 13)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 20)

    def generateLines(self, sheet, lines, content_format, amount_format):
        row = 1
        for line in lines:
            sheet.write(row, 0, line['identification_id'] or '', content_format)
            sheet.write(row, 1, line['cat'] or '', content_format)
            sheet.write(row, 2, line['status'] or '', content_format)
            sheet.write(row, 3, line['name'] or '', content_format)
            sheet.write(row, 4, line['job_id'] or '', content_format)
            sheet.write(row, 5, line['service_id'] or '', content_format)
            sheet.write(row, 6, line['department_id'] or '', content_format)
            sheet.write(row, 7, line['direction_id'] or '', content_format)
            sheet.write(row, 8, line['gender'] or '', content_format)
            sheet.write(row, 9, line['hiring_date'] or '', amount_format)
            sheet.write(row, 10, line['birthday'] or '', amount_format)
            sheet.write(row, 11, line['age'] or '', content_format)
            sheet.write(row, 12, line['type_contrat'] or '', content_format)
            row += 1

    def writeHeaders(self, sheet, obj, header_format):
        col = 0
        for i in range(len(self.title)):
            sheet.write(0, col, self.title[i], header_format)
            col += 1

    def generate_xlsx_report(self, workbook, data, obj):
        lines = data['lines']
        sheet = workbook.add_worksheet('LISTE DES NOUVELLES RECRUES')
        header_format = workbook.add_format(self.h_format)
        content_format = workbook.add_format(self.c_format)
        amount_format = workbook.add_format(self.a_format)
        self.formatSheet(sheet)
        self.writeHeaders(sheet, obj, header_format)
        self.generateLines(sheet, lines, content_format, amount_format)
        workbook.close()