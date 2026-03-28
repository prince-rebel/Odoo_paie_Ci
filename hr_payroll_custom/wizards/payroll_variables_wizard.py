# -*- coding:utf-8 -*-

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError
import xlrd
import base64


class PayrollVariables(models.TransientModel):
    _name = 'hr_payroll_custom.payroll_variables'
    _description = "Assistant d'importation des variables de paye"

    type = fields.Selection([('input', "Données d'entrée"), ('days', 'Jours')], 'Type ')
    rule_id = fields.Many2one('hr.salary.rule', 'Règle')
    data_file = fields.Binary("Fichier à importer",
                              help="Le fichier (XLS) des données d'entrée doit contenir les colonnes suivantes: 'matricule', "
                                   "'code', 'libelle', 'montant'. Pour les heures supplémentaires, veuillez choisir le "
                                   "type 'jours'. Le fichier afférent doit contenir les colonnes suivantes:"
                                   " 'matricule', 'code', 'libelle', 'jours', 'heures'.")

    def _get_compute_data(self, sheet):
        try:
            keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]

            dict_list = []
            for row_index in range(1, sheet.nrows):
                d = {keys[col_index]: sheet.cell(row_index, col_index).value
                     for col_index in range(sheet.ncols)}
                dict_list.append(d)
            return dict_list
        except:
            return False

    def compute_data(self):
        for rec in self:
            if not rec.type or not rec.rule_id or not rec.data_file:
                raise ValidationError(
                    _(f"Les informations réquises n'ont pas été définies. Merci de faire le nécessaire"))

            data_file = base64.b64decode(rec.data_file)
            book = xlrd.open_workbook(file_contents=data_file)
            sheet_names = book.sheet_names()
            run_id = self.env['hr.payslip.run'].search([('id', '=', rec.env.context.get('active_id'))])
            if run_id:
                if sheet_names:
                    for name in sheet_names:
                        sheet = book.sheet_by_name(name)
                        data = rec._get_compute_data(sheet)
                        for dt in data:
                            identification = int(dt['matricule'])
                            if dt['code'] != rec.rule_id.code:
                                raise ValidationError(
                                    _("le code contenu dans le fichier est différent de celui de la règle que "
                                      "vous voulez importer. Merci de faire les corrections nécessaires"))
                            employee = self.env['hr.employee'].search([('identification_id', '=', identification)],
                                                                      limit=1)
                            if employee:
                                payslip = run_id.slip_ids.filtered(lambda s: s.employee_id == employee)
                                if len(payslip) > 1:
                                    raise exceptions.ValidationError(
                                        _(f"L'employé {employee.identification_id} / {employee.name} {employee.first_name or ''} "
                                          f"possède plus d'un bulletin dans ce lot. Merci de les supprimer et de ne garder qu'un seul."))
                                if payslip:
                                    if rec.type == 'input':
                                        input = self.env['hr.payslip.input'].search(
                                            [('payslip_id', '=', payslip.id), ('code', '=', dt['code'])])
                                        if len(input) > 1:
                                            raise ValidationError(_(f"Le bulletin {payslip.number} de l'employé {employee.name} possède plus "
                                                f"d'une fois l'entrée {self.rule_id.name} dans son bulletin."
                                                f" Merci de les supprimer et de ne garder qu'un seul"))
                                        if input:
                                            input.write({'amount': dt['montant']})
                                        else:
                                            self.env['hr.payslip.input'].create({
                                                'payslip_id': payslip.id,
                                                'code': dt['code'],
                                                'amount': dt['montant'],
                                                'name': rec.rule_id.name
                                            })

                                    else:
                                        worked_days = self.env['hr.payslip.worked_days'].search(
                                            [('payslip_id', '=', payslip.id), ('code', '=', dt['code'])])
                                        if len(worked_days) > 1:
                                            raise ValidationError(f"Le bulletin {payslip.number} de l'employé {employee.name} possède plus "
                                                f"d'une fois l'entrée {rec.rule_id.name} dans son bulletin."
                                                f" Merci de les supprimer et de ne garder qu'un seul.")
                                        if worked_days:
                                            worked_days.write({
                                                'number_of_days': dt['jours'],
                                                'number_of_hours': dt['heures']
                                            })
                                        else:
                                            work_entry_type_id = self.env['hr.work.entry.type'].search([('code','=',dt['code'])], limit=1)
                                            if len(work_entry_type_id) != 1:
                                                raise ValidationError(_(f"La variable {rec.rule_id.name} que vous "
                                                                        f"voulez importer n'est soit pas présente, soit "
                                                                        f"existe en doublon. Merci de contacter un administrateur."))
                                            self.env['hr.payslip.worked_days'].create({
                                                'payslip_id': payslip.id,
                                                'work_entry_type_id': work_entry_type_id.id,
                                                'code': dt['code'],
                                                'name': rec.rule_id.name,
                                                'number_of_days': dt['jours'],
                                                'number_of_hours': dt['heures'],
                                            })
                                    payslip.compute_sheet()
            else:
                raise ValidationError(_(f"Impossible de récupérer le lot de paye. Merci de contacter un administrateur"))
        return True
