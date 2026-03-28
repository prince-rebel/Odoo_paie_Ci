# -*- coding:utf-8 -*-

from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class SalaryVariationEmployee(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_salary_variation_employee_xls'
    _description = "Rapport de variation des effectifs payés"
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

    string_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
    }

    content_format = {
        'bold': 0,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'fg_color': 'white',
        'num_format': '### ### ### ##0'
    }

    amount_format = {
        'bold': 1,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '### ### ### ##0'
    }

    cumul_label_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'color': 'black',
        'fg_color': 'white',
    }

    cumul_number_format = {
        'bold': 1,
        'border': 1,
        'align': 'rigth',
        'valign': 'vcenter',
        'color': 'black',
        'fg_color': 'white',
        'num_format': '### ### ### ##0'
    }

    def formatSheet(self, sheet):
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 12)
        sheet.set_column('C:C', 50)

    def generateHeaders(self, sheet, headers, date_header, header_format):
        sheet.merge_range(0,0,0,1, 'Période encours', header_format)
        sheet.write(0,2,date_header[0] + ' - '+ date_header[1], header_format)
        sheet.merge_range(1,0,1,1, 'Période précédente', header_format)
        sheet.write(1,2,date_header[2] + ' - '+ date_header[3], header_format)
        row = 3
        sheet.set_row(1, 30)
        sheet.merge_range(row, 0, row + 1, 0, 'N°', header_format)
        sheet.merge_range(row, 1, row + 1, 1, 'MATRICULE', header_format)
        sheet.merge_range(row, 2, row + 1, 2, 'NOM ET PRENOMS', header_format)
        idx1 = 3
        idx2 = 6
        for key in headers.keys():
            sheet.merge_range(row, idx1, row, idx2, headers[key]['en_US'], header_format)
            idx1 = idx2 + 1
            idx2 += 4
        row += 1
        col = 3
        for key in headers.keys():
            sheet.write(row, col, 'MOIS PRECEDENT', header_format)
            sheet.write(row, col + 1, 'MOIS EN COURS', header_format)
            sheet.write(row, col + 2, 'ECART', header_format)
            sheet.write(row, col + 3, 'OBSERVATIONS', header_format)
            sheet.set_column(row, col, 17)
            sheet.set_column(row, col + 1, 17)
            sheet.set_column(row, col + 2, 17)
            sheet.set_column(row, col + 3, 20)
            col += 4
        row += 1
        return row

    def generateLines(self, sheet, row, headers, elements, content_format, string_format, cumul_label_format, cumul_number_format):
        number = 1
        res = []
        for key in headers:
            vals = {
                'code': key,
                'last_month': 0,
                'current_month': 0
            }
            res.append(vals)
        for elt in elements:
            col = 0
            sheet.write(row, col, number, string_format)
            sheet.write(row, col + 1, elt['identification_id'], string_format)
            sheet.write(row, col + 2, (elt['name'] or '') + ' ' + (elt['first_name'] or ''), string_format)
            col += 3
            for line in elt['data']:
                sheet.write(row, col, line['last_month'], content_format)
                sheet.write(row, col + 1, line['current_month'], content_format)
                sheet.write(row, col + 2, line['current_month'] - line['last_month'], content_format)
                if line['code'] != 'NET':
                    sheet.write(row, col + 3, line['comment'], content_format)
                else:
                    sheet.write(row, col + 3, line['comment'][0] if line['comment'] else '', content_format)
                col += 4
                for data in res:
                    if line['code'] == data['code']:
                        data['last_month'] += line['last_month']
                        data['current_month'] += line['current_month']

            row += 1
            number += 1
        sheet.merge_range(row, 0, row, 2, 'TOTAL GENERAL', cumul_label_format)
        col = 3
        for key in res:
            sheet.write(row, col, key['last_month'], cumul_number_format)
            sheet.write(row, col + 1, key['current_month'], cumul_number_format)
            sheet.write(row, col + 2, key['current_month'] - key['last_month'], cumul_number_format)
            sheet.write(row, col + 3, '', cumul_label_format)
            col += 4

    def generate_xlsx_report(self, workbook, data, obj):
        codes = data['codes']
        elements = data['elements']
        date_header = data['date_header']
        sheet = workbook.add_worksheet('RECAPITULATIF DES SALAIRES PAR EMPLOYE')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(self.header_format)
        content_format = workbook.add_format(self.content_format)
        string_format = workbook.add_format(self.string_format)
        cumul_number_format = workbook.add_format(self.cumul_number_format)
        cumul_label_format = workbook.add_format(self.cumul_label_format)
        self.formatSheet(sheet)
        #row = 3
        row = self.generateHeaders(sheet, codes, date_header, header_format)
        self.generateLines(sheet, row, codes, elements, content_format, string_format, cumul_label_format, cumul_number_format)
        workbook.close()