# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
from . import emergency_contacts
import logging

_logger = logging.getLogger(__name__)


Type_employee = [('h', 'Horaire'), ('j', 'Journalier'), ('m', 'Mensuel')]
Type_payment_method = [('espece', 'Espèces'), ('virement', 'Virement bancaire'), ('cheque', 'Chèques')]
Type_employee_status = [('cadre', 'Cadre'), ('non_cadre', 'Non cadre'), ('csup', 'Csup')]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    address_home_id = fields.Many2one('res.partner', string='Home Address', help="Employee's home address")
    
    @api.onchange('address_id')
    def _onchange_address_home_id(self):
        if self.address_id:
            self.address_home_id = self.address_id


    def button_mission_pro(self):
        active_id = self.id
        return {
            'name': "Mission professionnelle",
            'id': self.id,
            'res_model': 'hr_custom.professional_mission',
            'type': 'ir.actions.act_window',
            'context': {"default_employee_id": active_id},
            'domain':[('employee_id','=',active_id)],
            'view_mode': 'tree,form',
            'view_type': 'tree,form',
        }

    def button_work_accident(self):
        active_id = self.id
        return {
            'name': "Accidents de travail",
            'id': self.id,
            'res_model': 'hr_custom.work_accident',
            'type': 'ir.actions.act_window',
            'context': {"default_employee_id": active_id},
            'domain':[('employee_id','=',active_id)],
            'view_mode': 'tree,form',
            'view_type': 'tree,form',
        }
    @api.depends('marital', 'children')
    def _get_part_igr(self):
        """
        Function to determine the number of IGR shares
        :return: none
        """
        for rec in self:
            result = 0
            if rec.marital:
                marital_status_temp = rec.marital
                marital_status = marital_status_temp[0]
                number_of_children = rec.children

                if (marital_status == "s") or (marital_status == "d"):
                    if number_of_children == 0:
                        result = 1
                    elif (1.5 + number_of_children * 0.5) > 5:
                        result = 5
                    else:
                        result = 1.5 + number_of_children * 0.5
                else:
                    if marital_status == "m":
                        if number_of_children == 0:
                            result = 2
                        else:
                            if (2 + number_of_children * 0.5) > 5:
                                result = 5
                            else:
                                result = 2 + number_of_children * 0.5
                    else:
                        if marital_status == "w":
                            if number_of_children == 0:
                                result = 1.5
                            else:
                                if (2 + number_of_children * 0.5) > 5:
                                    result = 5
                                else:
                                    result = 2 + number_of_children * 0.5
            rec.part_igr = result
            rec._get_nb_part_cmu()

    def _get_nb_part_cmu(self):
        """
        Function that determines the number of shares for Universal Health Coverage (CMU)
        :return: none
        """
        for emp in self:
            nb = emp.total_children + 1
            if emp.marital == "married":
                nb += 1
            emp.part_cmu = nb

    @api.constrains('identification_cnps')
    def check_identification_cnsp(self):
        """
        This function checks that the registered CNPS number respects the number of mandatory characters
        :return:
        """
        for rec in self:
            if rec.identification_cnps and len(rec.identification_cnps) < 12:
                raise ValidationError(
                    _("Le numéro CNPS est de 12 caractères, merci de faire les vérifications nécessaires."))

    @api.depends('hiring_date', 'departure_date')
    def _get_seniority(self):
        """
        This function makes it possible to calculate the seniority of the employee in the company since his hiring date
        :return: none
        """
        today = fields.Datetime.now()

        for emp in self:
            hiring_date = fields.Datetime.from_string(emp.hiring_date)
            if emp.departure_date:
                departure_date = fields.Datetime.from_string(emp.departure_date)
                this_date = min(today, departure_date)
            else:
                this_date = today
            tmp = relativedelta(this_date, hiring_date)
            emp.seniority_employee = tmp.years

    first_name = fields.Char("Prénoms")
    identification_cnps = fields.Char('N° CNPS', size=12)
    employee_category_id = fields.Many2one('hr_custom.employee_category', 'Catégorie employé',
                                           help="Catégorie de l'employé. Ex: Cadre, Employé, Agent de maitrise...")
    type = fields.Selection(Type_employee, 'Type', default=False,
                            help="Ce type est utilisé pour la génération des déclations sociales/fiscales telle que "
                                 "la CNPS")
    identification_cmu = fields.Char('N° CMU')
    part_igr = fields.Float(compute=_get_part_igr, string='Part IGR', tracking=True)
    part_cmu = fields.Integer("Nombre de part CMU", compute="_get_nb_part_cmu", tracking=True)
    hiring_date = fields.Date("Date d'embauche", tracking=True)
    seniority_employee = fields.Integer("Anciennété", compute="_get_seniority")
    age = fields.Integer('Âge employé', compute='_get_age_employee')
    total_children = fields.Integer('Nombre enfant total', compute='_compute_children')
    childrens_ids = fields.One2many('hr_custom.employee_children', 'employee_id', 'Enfants')
    diplome_id = fields.Many2one('hr_custom.diploma', 'Diplôme', help="Renseigner le diplôme le plus élévé")
    study_area_id = fields.Many2one('hr_custom.study_area', 'Domaine', help="Renseigner le domaine d'étude")
    children = fields.Integer(compute="_compute_children", tracking=True)
    salary_category_id = fields.Many2one('hr_custom.salary_category', 'Catégorie salariale',
                                         help="Catégorie salariale de l'employé")
    piece_identite_id = fields.Many2one("hr_custom.identity_card", "Pièce d'identité")
    num_piece = fields.Char("Numéro de la pièce",
                            help="Renseignez le numéro de la pièce que vous avez sélectionné plus haut")
    emergency_contacts_ids = fields.One2many('hr_custom.emergency_contacts', 'employee_id', 'Personnes à contacter')
    level_of_study_id = fields.Many2one('hr_custom.employee_degree', "Niveau d'étude")
    direction_id = fields.Many2one('hr.department', 'Direction', domain="[('type', '=', 'direction')]")
    department_id = fields.Many2one(domain="[('type', '=', 'department')]")
    service_id = fields.Many2one('hr.department', 'Service', domain="[('type', '=', 'service')]")

    nature_employe = fields.Selection([('local', 'Local'), ('expat', 'Expatrié')], "Nature de l'employé",
                                      default='local')
    payment_method = fields.Selection(Type_payment_method, string='Moyens de paiement', default='espece', tracking=True)
    employee_status = fields.Selection(Type_employee_status, string="Statut", tracking=True,
                                       help="Le statut de l'employé. Il permet de distinguer les cadres supérieurs, "
                                            "des cadres et des non-cadre et les ")
    first_retirement_notification_date = fields.Date("Date première alerte retraite")#date_first_alerte_retraite
    second_retirement_notification_date = fields.Date("Date seconde alerte retraite")#date_second_alerte_retraite
    estimated_date_retirement = fields.Date("Date prévisionnelle départ retraite")
    medical_visit_ids = fields.One2many('hr_custom.medical_visit', 'employee_id', 'Visites médicales',
                                        help="Les visites médicales de l'employé")
    professional_sanctions_ids = fields.One2many('hr_custom.professional_sanctions', 'employee_id', string='Sanctions',
                                                 help="Les sanctions de l'employé")
    mission_ids = fields.One2many('hr_custom.professional_mission', 'employee_id', string='Missions')
    work_accident_ids = fields.One2many('hr_custom.work_accident', 'employee_id', string='Accidents de travail')

    # SPOUSE'S INFORMATIONS
    conjoint_name = fields.Char(string="Nom conjoint(e)", groups="hr.group_hr_user", tracking=True)
    conjoint_first_name = fields.Char(string="Prénoms conjoint(e)", groups="hr.group_hr_user", tracking=True)
    gender_conjoint = fields.Selection(emergency_contacts.Type_gender, "Sexe", groups="hr.group_hr_user", tracking=True)
    birthplace = fields.Char("Lieu de naissance", groups="hr.group_hr_user", tracking=True)
    num_cmu_conjoint = fields.Char('N° CMU conjoint', tracking=True)

    @api.depends("childrens_ids")
    def _compute_children(self):
        """
            Function to determine the number of children taken into account in the calculation of certain premiums
        :return:
        """
        for emp in self:
            emp.total_children = len(emp.childrens_ids)
            children_in_charge = 0
            for child in emp.childrens_ids:
                if child.age <= emp.company_id.max_age_child and child.active:
                    children_in_charge += 1
                else:
                    if child.study_certificate and child.age <= emp.company_id.max_age_child_certificat \
                            and child.active:
                        children_in_charge += 1
            emp.children = children_in_charge

    @api.constrains('identification_id')
    def _check_unique_name(self):
        """
        This function checks the uniqueness of the employee identification number
        :return:
        """
        for rec in self:
            count_identification_id = self.search_count(
                [('identification_id', '=', rec.identification_id), ('id', '!=', rec.id)])
            if count_identification_id > 0:
                raise ValidationError(
                    _("Ce matricule est déjà utilisé par un autre employé. S'il s'agit du même employé, veuillez le "
                      "rechercher et actualiser les données nécessaires. Dans le cas contraire, attribuez un matricule "
                      "différent de ceux existant."))

    @api.depends('birthday')
    def _get_age_employee(self):
        this_date = fields.Datetime.now()
        for emp in self:
            date_naissance = fields.Datetime.from_string(emp.birthday)
            tmp = relativedelta(this_date, date_naissance)
            emp.age = tmp.years
            emp.determine_date_retirement()

    def determine_date_retirement(self, employees=False):
        """
        Cette fonction permet de déterminer les dates de notifications pour le départ à la retraite d'un employé ou du
        liste d'employés
        :param employees: Liste des employés
        :return: True
        """
        employees = employees if employees else self
        for rec in employees:
            if rec.company_id and rec.birthday:
                date_retirement = rec.birthday + relativedelta(
                    years=rec.company_id.retirement_age)
                first_date = str(fields.Date.from_string(date_retirement) + relativedelta(
                    months=- rec.company_id.first_retirement_alert))
                second_date = str(fields.Date.from_string(date_retirement) + relativedelta(
                    months=- rec.company_id.second_retirement_alert))
                rec.first_retirement_notification_date = first_date
                rec.second_retirement_notification_date = second_date
                rec.estimated_date_retirement = date_retirement
        return True

    def cron_determine_date_retirement_all_employee(self): #determine_date_retirement_all_employee
        """
        Cette actions planifiées permet de détermniner les dates de départ à la retraite de l'ensemble des employés
        :return: Null
        """
        all_employee = self.env['hr.employee'].search([])
        self.determine_date_retirement(all_employee)


    def cron_send_mail_retirement(self):
        """
        Fonction permettant d'envoyer des emails de notification concernant les départs à la retraite
        :return:
        """
        today = datetime.today()
        employees = self.search(['|', ('first_retirement_notification_date', '=', today),
                                 ('second_retirement_notification_date', '=', today)])
        if employees:
            email_template_id = self.env.ref('hr_custom.template_email_retirement').id
            email_template = self.env['mail.template'].browse(email_template_id)
            for employee in employees:
                email_template.send_mail(employee.id, force_send=True)


class EmployeeCategory(models.Model):
    _name = 'hr_custom.employee_category'
    _description = "Categorie des employés"
    _order = 'sequence'

    name = fields.Char('Désignation')
    code = fields.Char('Code', size=2)
    sequence = fields.Integer('Séquence')
    description = fields.Text('Description')