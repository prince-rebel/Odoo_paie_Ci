# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportWorkAccident(models.AbstractModel):
    _name = 'report.hr_custom.report_work_accident_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Rapport des accidents de travail"

    title = [
        "REFÉRENCE",
        "MATRICULE",
        "NOM & PRENOMS",
        "FONCTION",
        "SERVICE",
        "DEPARTEMENT",
        "DIRECTION",
        "SEXE",
        "NAISSANCE",
        "AGE",
        "DATE DE L'ACCIDENT",
    ]

    # cols = [
    #     'reference', 'matricule', 'name', 'job_id', 'agence_id', 'service_id', 'department_id', 'direction_id',
    #     'gender', 'birthday', 'age', 'accident_date'
    # ]

    i = 0

    # Formattage pour les headers
    h_format = {
        'bold': 1,
        'border': 1,
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': 'silver',
        'text_wrap': 0,
        'font_name': 'Helvetica'
    }

    c_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
        'text_wrap': 0,
        'num_format': 'dd/mm/yyyy',
        'font_name': 'Helvetica'
    }

    a_format = {
        'border': 1,
        'font_size': 10,
        'align': 'left',
        'valign': 'vcenter',
        'text_wrap': 1,
        'font_name': 'Helvetica'
    }

    def formatSheet(self, sheet):
        sheet.add_table('A1:K1', {'autofilter': True})
        sheet.set_default_row(30)
        sheet.set_row(0, 25)
        sheet.set_column('A:A', 13)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 37)
        sheet.set_column('D:D', 25)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 24)
        sheet.set_column('H:H', 13)
        sheet.set_column('I:I', 13)
        sheet.set_column('J:J', 11)
        sheet.set_column('K:K', 20)

    def generateLines(self, sheet, lines, content_format, string_format):
        cpt = 1
        for line in lines:
            sheet.write(cpt, 0, line['reference'] or '', string_format)
            sheet.write(cpt, 1, line['identification_id'] or '', string_format)
            sheet.write(cpt, 2, line['name'] or '', string_format)
            sheet.write(cpt, 3, line['job_id'] or '', string_format)
            sheet.write(cpt, 4, line['service_id'] or '', string_format)
            sheet.write(cpt, 5, line['department_id'] or '', string_format)
            sheet.write(cpt, 6, line['direction_id'] or '', string_format)
            sheet.write(cpt, 7, line['gender'] or '', string_format)
            sheet.write(cpt, 8, line['birthday'] or '', content_format)
            sheet.write(cpt, 9, line['age'] or '', string_format)
            sheet.write(cpt, 10, line['accident_date'] or '', string_format)
            cpt += 1

    def writeHeaders(self, sheet, obj, header_format):
        col = 0
        for i in range(len(self.title)):
            sheet.write(0, col, self.title[i], header_format)
            col += 1

    def generate_xlsx_report(self, workbook, data, obj):
        lines = data['lines']
        sheet = workbook.add_worksheet('LISTE DES ACCIDENTS DE TRAVAIL')
        header_format = workbook.add_format(self.h_format)
        content_format = workbook.add_format(self.c_format)
        string_format = workbook.add_format(self.a_format)
        self.formatSheet(sheet)
        self.writeHeaders(sheet, obj, header_format)
        self.generateLines(sheet, lines, content_format, string_format)
        workbook.close()