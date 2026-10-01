# -*- coding:utf-8 -*-
from odoo import fields, models


class ReportContributionSummaryXlsx(models.AbstractModel):
    _name = 'report.hr_payroll_custom.report_contribution_summary_xls'
    _description = "État résumé des cotisations (Excel)"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, summaries):
        title_fmt = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        info_fmt = workbook.add_format({'font_size': 9})
        head_fmt = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter',
                                        'text_wrap': True, 'fg_color': '#D9D9D9'})
        text_fmt = workbook.add_format({'border': 1})
        rate_fmt = workbook.add_format({'border': 1, 'num_format': '0.00'})
        amount_fmt = workbook.add_format({'border': 1, 'num_format': '# ### ### ##0'})
        int_fmt = workbook.add_format({'border': 1, 'num_format': '0'})
        total_text_fmt = workbook.add_format({'bold': True, 'border': 1, 'fg_color': '#A9C8EE'})
        total_amount_fmt = workbook.add_format({'bold': True, 'border': 1, 'fg_color': '#A9C8EE',
                                                'num_format': '# ### ### ##0'})

        headers = ["N°", "Rubriques de cotisations", "Taux salarial", "Taux patronal", "Taux global",
                   "Assiette de cotisation", "Base", "Montant salarial", "Montant patronal", "Montant global",
                   "Effectif H.", "Effectif F."]
        widths = [8, 32, 10, 10, 10, 16, 16, 16, 16, 16, 10, 10]

        for summary in summaries:
            sheet = workbook.add_worksheet((summary.name or 'Etat')[:31])
            for col, width in enumerate(widths):
                sheet.set_column(col, col, width)
            closure = dict(summary._fields['closure_mode'].selection).get(summary.closure_mode)
            sheet.merge_range(0, 0, 0, len(headers) - 1, "État résumé des cotisations MENSUEL", title_fmt)
            sheet.write(1, 0, f"Société : {summary.company_id.name}", info_fmt)
            sheet.write(2, 0, f"Période du {summary.date_from.strftime('%d/%m/%Y')} au "
                              f"{summary.date_to.strftime('%d/%m/%Y')} - Édition en "
                              f"{summary.currency_id.name} ({closure})", info_fmt)
            sheet.write(3, 0, f"Édité le {fields.Datetime.context_timestamp(self, fields.Datetime.now()).strftime('%d/%m/%Y %H:%M')}"
                              f" - Bulletins : {summary.payslip_count}", info_fmt)

            row = 5
            sheet.set_row(row, 30)
            for col, label in enumerate(headers):
                sheet.write(row, col, label, head_fmt)
            sheet.freeze_panes(row + 1, 2)
            row += 1

            def write_total(r, label, emp, pat, tot):
                sheet.write(r, 0, '', total_text_fmt)
                sheet.write(r, 1, label, total_text_fmt)
                for c in range(2, 7):
                    sheet.write(r, c, '', total_text_fmt)
                sheet.write_number(r, 7, emp, total_amount_fmt)
                sheet.write_number(r, 8, pat, total_amount_fmt)
                sheet.write_number(r, 9, tot, total_amount_fmt)
                sheet.write(r, 10, '', total_text_fmt)
                sheet.write(r, 11, '', total_text_fmt)

            for group in summary._get_report_groups():
                for line in group['lines']:
                    sheet.write(row, 0, line.code or '', text_fmt)
                    sheet.write(row, 1, line.name or '', text_fmt)
                    if line.rate_total:
                        sheet.write_number(row, 2, line.rate_employee, rate_fmt)
                        sheet.write_number(row, 3, line.rate_employer, rate_fmt)
                        sheet.write_number(row, 4, line.rate_total, rate_fmt)
                    else:
                        for c in (2, 3, 4):
                            sheet.write(row, c, '', text_fmt)
                    for col, value in ((5, line.assiette), (6, line.base), (7, line.amount_employee),
                                       (8, line.amount_employer), (9, line.amount_total)):
                        sheet.write_number(row, col, round(value or 0), amount_fmt)
                    sheet.write_number(row, 10, line.headcount_male, int_fmt)
                    sheet.write_number(row, 11, line.headcount_female, int_fmt)
                    row += 1
                write_total(row, f"Total {group['name']}", round(group['total_employee']),
                            round(group['total_employer']), round(group['total_global']))
                row += 1
            write_total(row, "Total", round(summary.total_employee), round(summary.total_employer),
                        round(summary.total_global))
