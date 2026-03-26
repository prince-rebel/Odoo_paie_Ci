# -*- coding:utf-8 -*-

import datetime
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class SalaryVariationRule(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_salary_variation_rule_xls'
    _description = "Rapport de reconciliation des salaires "
    _inherit = 'report.report_xlsx.abstract'

    # Formattage pour les headers
    header_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': 'silver',
        'text_wrap': 1,
        'num_format': '### ### ##0'
    }

    important_elements_string_format = {
        'bold': 1,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'silver',
        'text_wrap': 1,
        'num_format': '### ### ##0'
    }
    important_elements_amount_format = {
        'bold': 1,
        'border': 1,
        'align': 'rigth',
        'valign': 'vcenter',
        'fg_color': 'silver',
        'text_wrap': 1,
        'num_format': '### ### ##0'
    }

    string_format = {
        'bold': 0,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': 'white',
    }

    cumul_label_format = {
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
    }

    amount_format = {
        'bold': 1,
        'border': 1,
        'align': 'right',
        'valign': 'vcenter',
        'num_format': '### ### ##0'
    }

    def formatSheet(self, sheet):
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:E', 15)
        sheet.set_column('F:F', 50)

    def generateHeaders(self, sheet, row, date_header, header_format):
        sheet.merge_range(0, 0, 0, 1, 'Période encours', header_format)
        sheet.merge_range(0, 2, 0, 3, date_header[0] + ' - ' + date_header[1], header_format)
        sheet.merge_range(1, 0, 1, 1, 'Période précédente', header_format)
        sheet.merge_range(1, 2, 1, 3, date_header[2] + ' - ' + date_header[3], header_format)
        sheet.set_row(row, 30)
        sheet.write(row, 0, 'RUBRIQUE', header_format)
        sheet.write(row, 1, 'LIBELLÉ RUBRIQUE', header_format)
        sheet.write(row, 2, 'MOIS PRÉCÉDENT', header_format)
        sheet.write(row, 3, 'MOIS EN COURS', header_format)
        sheet.write(row, 4, 'ECART', header_format)
        sheet.write(row, 5, 'OBSERVATION', header_format)
        row += 1
        return row

    def generateLines(self, sheet, row, elements, string_format, cumul_label_format, amount_format,
                      important_elements_string_format, important_elements_amount_format):
        old_amount = 0
        new_amount = 0
        old_gross = 0
        new_gross = 0
        old_net = 0
        new_net = 0
        ecart = 0
        for elt in elements:
            col = 0
            if elt['code'] not in ['BRUT', 'NET']:
                sheet.write(row, col, elt['code'], string_format)
                sheet.write(row, col + 1, elt['name'], string_format)
                sheet.write(row, col + 2, elt['old_amount'], amount_format)
                sheet.write(row, col + 3, elt['new_amount'], amount_format)
                sheet.write(row, col + 4, elt['ecart'], amount_format)
                sheet.write(row, col + 5, '', amount_format)
                if elt['code'] in ['TRSP', 'ALL_FAM']:
                    old_gross += elt['old_amount']
                    new_gross += elt['new_amount']

            else:
                sheet.write(row, col, elt['code'], important_elements_string_format)
                sheet.write(row, col + 1, elt['name'], important_elements_string_format)
                sheet.write(row, col + 2, elt['old_amount'], important_elements_amount_format)
                sheet.write(row, col + 3, elt['new_amount'], important_elements_amount_format)
                sheet.write(row, col + 4, elt['ecart'], important_elements_amount_format)
                sheet.write(row, col + 5, '', important_elements_string_format)
                if elt['code'] == 'BRUT':
                    old_gross = elt['old_amount']
                    new_gross = elt['new_amount']
                if elt['code'] == 'NET':
                    old_net = elt['old_amount']
                    new_net = elt['new_amount']

            old_amount += elt['old_amount']
            new_amount += elt['new_amount']
            ecart += elt['ecart']
            row += 1
        sheet.merge_range(row, 0, row, 1, 'TOTAL GENERAL', cumul_label_format)
        sheet.write(row, 2, old_amount, amount_format)
        sheet.write(row, 3, new_amount, amount_format)
        sheet.write(row, 4, ecart, amount_format)

        if old_gross != 0 or new_gross != 0:
            row += 2
            sheet.merge_range(row, 0, row, 1, 'TOTAL BRUTS MOIS PRECEDENTS', string_format)
            sheet.write(row, 2, old_gross, amount_format)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'TOTAL BRUTS MOIS EN COURS', string_format)
            sheet.write(row, 2, new_gross, amount_format)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'ECARTS BRUT TOTAL', important_elements_string_format)
            sheet.write(row, 2, new_gross - old_gross, important_elements_amount_format)
        if old_net != 0 or new_net != 0:
            row += 2
            sheet.merge_range(row, 0, row, 1, 'TOTAL NET MOIS PRECEDENTS', string_format)
            sheet.write(row, 2, old_net, amount_format)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'TOTAL NET MOIS EN COURS', string_format)
            sheet.write(row, 2, new_net, amount_format)
            row += 1
            sheet.merge_range(row, 0, row, 1, 'ECARTS NET',
                              important_elements_string_format)
            sheet.write(row, 2, new_net - old_net, important_elements_amount_format)

    def generate_xlsx_report(self, workbook, data, obj):
        results = data['elements']
        date_header = data['date_header']
        sheet = workbook.add_worksheet('RECONCILIATION DES SALAIRES')
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(self.header_format)
        important_elements_string_format = workbook.add_format(self.important_elements_string_format)
        important_elements_amount_format = workbook.add_format(self.important_elements_amount_format)
        string_format = workbook.add_format(self.string_format)
        cumul_label_format = workbook.add_format(self.cumul_label_format)
        amount_format = workbook.add_format(self.amount_format)
        self.formatSheet(sheet)
        row = 3
        row = self.generateHeaders(sheet, row, date_header, header_format)
        self.generateLines(sheet, row, results, string_format, cumul_label_format, amount_format,
                           important_elements_string_format, important_elements_amount_format)
        workbook.close()
