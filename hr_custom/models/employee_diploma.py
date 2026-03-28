# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

Type_diploma = [('diplome', 'Diplôme'), ('certif', 'Certification')]
nature_identity_card = [('attestion', "Attestation d'indentité"), ("carte_sejour", "Carte de séjour"),
                                     ("cni", "CNI"), ("passeport", "Passeport")]

class EmployeeDegree(models.Model):
    _name = "hr_custom.employee_degree"
    _description = "Niveau d'étude"
    _order = "sequence"

    name = fields.Char('Niveau')
    sequence = fields.Integer('Sequence', help="Est utilisé pour l'affichage des niveaux d'étude.", default=1)

    @api.constrains('name')
    def _check_unique_name(self):
        for rec in self:
            count_name = self.search_count([('name','=', rec.name),('id','!=',rec.id)])
            if count_name > 0:
                raise ValidationError(_("Le niveau d'étude doit être unique"))


class Diploma(models.Model):
    _name = 'hr_custom.diploma'
    _description = "Diplome"

    name = fields.Char("Diplome", help="Diplome")


class StudyArea(models.Model):
    _name = "hr_custom.study_area"
    _description = "Domaine d'étude"

    name = fields.Char('Domaine', help="Domanie d'étude" , size=64)


class IdentityCard(models.Model):
    _name = "hr_custom.identity_card"
    _description = "Pièce d'identité"

    name = fields.Char("Numéro de la pièce", size=128, help="Numéro de la pièce d'identité")
    nature_piece = fields.Selection(nature_identity_card, string="Nature")
    date_etablissement = fields.Date("Date d'établissement")
    autorite = fields.Char("Autorité", size=128, help="L'autorité qui a délivrée la pièce d'identité")