# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SalaryCategory(models.Model):
    _name = "hr_custom.salary_category"
    _description = "Catégorie salariale"

    name = fields.Char('Catégorie salariale', size=64, required=False)
    category_salary_amount = fields.Integer("Salaire catégoriel")
    description = fields.Html('Description')
    activity_area_id = fields.Many2one('hr_custom.activity_area', "Secteur d'activité")


class ActivityArea(models.Model):
    _name = "hr_custom.activity_area"
    _description = "Secteur d'activite"

    name = fields.Char("Secteur d'activité")
    description = fields.Html("Description")
    convention_id = fields.Many2one("hr_custom.convention", "Convention")
    salary_category_ids = fields.One2many("hr_custom.salary_category", "activity_area_id", "Catégories salariales")

class Convention(models.Model):
    _name = "hr_custom.convention"
    _description = "Convention"

    name = fields.Char("Convention")
    description = fields.Html("Description")
    secteurs_ids = fields.One2many("hr_custom.activity_area", "convention_id", "Secteurs d'activtés")