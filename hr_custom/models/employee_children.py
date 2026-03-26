# -*- coding: utf-8 -*-

from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from . import emergency_contacts


class EmployeeChildren(models.Model):
    _name = 'hr_custom.employee_children'
    _description = 'Enfants des employées'

    @api.depends('date_of_birth')
    def _get_age_child(self):
        this_date = fields.Datetime.now()
        for child in self:
            date_of_birth = fields.Datetime.from_string(child.date_of_birth)
            delta = relativedelta(this_date, date_of_birth)
            child.age = delta.years



    def name_get(self):
        result = []
        for enf in self:
            if enf.first_name:
                name = enf.name + ' ' + enf.first_name
            else:
                name = enf.name
            result.append((enf.id, name))
        return result

    name = fields.Char('Nom', size=128, )
    first_name = fields.Char("Prénoms", size=225)
    date_of_birth = fields.Date("Date de naissance")
    mobile = fields.Char('Portable', size=128)
    email = fields.Char('email', size=128)
    num_cmu = fields.Char("N° CMU")
    employee_id = fields.Many2one('hr.employee', 'Employé')
    age = fields.Integer('Âge', compute="_get_age_child")
    gender = fields.Selection(emergency_contacts.Type_gender, "Sexe")
    study_certificate = fields.Boolean('Certificat de fréquentation', default=False,
                                       help="Cocher le bouton si vous avez reçu un certificat de fréquentation pour "
                                            "cet enfant, ensuite ajouter le document numérique dans les documents")
    active = fields.Boolean('Actif', default=True)
