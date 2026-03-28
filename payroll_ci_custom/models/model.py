# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    cmu_contributor = fields.Selection([
        ('full_contribution', 'Cotisation complète (100%)'),
        ('supported_fifty', 'Prise en charge 50%'),
        ('fully_supported', 'Prise en charge totale par l\'employeur'),
        ('do_not_contribute', 'Ne cotise pas'),
    ], string='Contribution CMU',
       default='full_contribution',
       help="Détermine qui prend en charge la CMU")

    part_cmu = fields.Integer(
        "Nombre de part CMU",
        compute="_get_nb_part_cmu",
        store=True,
        tracking=True
    )

    # Champs related vers hr.version pour affichage dans le formulaire employé
    net_souhaite = fields.Float(
        related='version_id.net_souhaite', readonly=False, store=False,
        string='Net Souhaité')
    brut_imposable_calcule = fields.Float(
        related='version_id.brut_imposable_calcule', readonly=True, store=False,
        string='Brut Imposable Calculé')
    its_calcule = fields.Float(
        related='version_id.its_calcule', readonly=True, store=False,
        string='ITS Calculé')
    cnps_calcule = fields.Float(
        related='version_id.cnps_calcule', readonly=True, store=False,
        string='CNPS Calculée')
    net_a_payer_calcule = fields.Float(
        related='version_id.net_a_payer_calcule', readonly=True, store=False,
        string='Net à Payer Calculé')
    cmu_calcule = fields.Float(
        related='version_id.cmu_calcule', readonly=True, store=False,
        string='CMU Calculée')

    @api.depends('marital', 'total_children')
    def _get_nb_part_cmu(self):
        for emp in self:
            nb = emp.total_children + 1
            if emp.marital == "married":
                nb += 1
            emp.part_cmu = nb

    def action_calculer_sursalaire(self):
        self.ensure_one()
        if self.version_id:
            return self.version_id.action_calculer_sursalaire()

    def action_simuler_paie(self):
        self.ensure_one()
        if self.version_id:
            return self.version_id.action_simuler_paie()

    def action_reinitialiser_calcul(self):
        self.ensure_one()
        if self.version_id:
            return self.version_id.action_reinitialiser_calcul()


class HrVersion(models.Model):
    _inherit = 'hr.version'

    net_souhaite = fields.Float(
        string='Net Souhaité',
        help='Salaire net que l\'employé souhaite recevoir'
    )

    # Champs calculés (wage et extra_pay sont déjà sur hr.version via hr_payroll_custom)
    brut_imposable_calcule = fields.Float(
        string='Brut Imposable Calculé',
        compute='_compute_elements_paie',
        store=True
    )

    its_calcule = fields.Float(
        string='ITS Calculé',
        compute='_compute_elements_paie',
        store=True
    )

    cnps_calcule = fields.Float(
        string='CNPS Calculée',
        compute='_compute_elements_paie',
        store=True
    )

    net_a_payer_calcule = fields.Float(
        string='Net à Payer Calculé',
        compute='_compute_elements_paie',
        store=True
    )

    cmu_calcule = fields.Float(
        string='CMU Calculée',
        compute='_compute_elements_paie',
        store=True
    )

    def _get_prime_anciennete(self, salaire_base, anciennete_annees):
        """Calcule la prime d'ancienneté"""
        if anciennete_annees < 2:
            taux = 0
        else:
            taux = 2 + int(anciennete_annees - 2)
            if taux > 25:
                taux = 25
        return round(salaire_base * (taux / 100), 0)
    
    def _calculer_its(self, brut_imposable, part_igr):
        """Calcule l'ITS selon le barème ivoirien"""
        # Calcul ITS brut
        if brut_imposable < 75000:
            its_brut = 0
        elif brut_imposable <= 240000:
            its_brut = (brut_imposable - 75000) * 0.16
        elif brut_imposable <= 800000:
            its_brut = (brut_imposable - 240000) * 0.21 + 26400
        elif brut_imposable <= 2400000:
            its_brut = (brut_imposable - 800000) * 0.24 + 144000
        elif brut_imposable <= 8000000:
            its_brut = (brut_imposable - 2400000) * 0.28 + 527999
        else:
            its_brut = (brut_imposable - 8000000) * 0.32 + 2095999
        
        # Réduction selon parts
        reductions = {
            1: 0, 1.5: 5500, 2: 11000, 2.5: 16500,
            3: 22000, 3.5: 27500, 4: 33000, 4.5: 38500
        }
        reduction = reductions.get(part_igr, 44000 if part_igr >= 5 else 0)
        
        return round(max(0, its_brut - reduction), 0)
    
    def _get_montant_cmu(self, employee):
        """Calcule le montant CMU déduit du salaire employé.
        Correspond exactement à la règle CMU du CDI/CDD :
        - supported_fifty  → part_cmu × 500 (l'employé paie la moitié)
        - tous les autres  → 0 (l'employeur prend en charge ou pas de déduction salariale)
        """
        if not employee:
            return 0
        cmu_contributor = getattr(employee, 'cmu_contributor', 'full_contribution')
        if cmu_contributor == 'supported_fifty':
            return employee.part_cmu * 500
        return 0
    
    def _get_primes_fixes(self, worked_days=30):
        """Récupère les primes fixes du contrat.

        Règles appliquées pour correspondre exactement à la structure CDI/CDD :
        - TRSP : entièrement non-imposable (va dans INDMNI comme dans la règle TRSP).
                 Si aucun TRSP n'est configuré, on applique le forfait légal de 25 000 FCFA
                 (valeur par défaut de la règle TRSP dans CDI/CDD).
        - ASM  : assurance maladie déduite du net.
        - CMU  : montant CMU si saisi en input (override de la règle CMU).
        """
        tx = worked_days / 30.0
        primes = {
            'transport_non_imposable': 0,
            'transport_imposable': 0,   # toujours 0 : TRSP est entièrement non-imposable
            'assurance': 0,
            'cmu': 0,
            'trsp_found': False,
        }

        for premium in self.fixed_premiums_ids:
            if premium.input_type_id.code == 'TRSP':
                # Tout le transport va en non-imposable (règle TRSP CDI/CDD → INDMNI)
                primes['transport_non_imposable'] = premium.amount * tx
                primes['trsp_found'] = True

            elif premium.input_type_id.code == 'ASM':
                primes['assurance'] = premium.amount * tx

            elif premium.input_type_id.code == 'CMU':
                primes['cmu'] = premium.amount * tx

        # Si aucun TRSP configuré, applique le forfait par défaut de la règle TRSP (25 000 FCFA)
        if not primes['trsp_found']:
            primes['transport_non_imposable'] = 25000 * tx

        return primes
    
    def _calculer_net_depuis_brut(self, brut_imposable, employee, worked_days=30):
        """
        Calcule le net à payer selon la formule exacte de votre système
        
        FORMULE CORRECTE selon vos règles :
        1. BRUT_IMPOSABLE = BASE + SURSA + PANC + transport_imposable
        2. ITS = calculé sur BRUT_IMPOSABLE
        3. CNPS = 6.3% sur min(BRUT_IMPOSABLE, 3375000)
        4. RET = ITS + CNPS
        5. BRUT_TOTAL = BRUT_IMPOSABLE + transport_non_imposable
        6. NET_PAIE = BRUT_TOTAL - RET - assurance_maladie
        7. NET = NET_PAIE - CMU
        """
        # 1. Calcul ITS sur brut imposable
        its = self._calculer_its(brut_imposable, employee.part_igr)
        
        # 2. CNPS salariale 6.3%
        base_cnps = min(brut_imposable, 3375000)
        cnps = round(base_cnps * 0.063, 0)
        
        # 3. Total retenues fiscales et sociales
        ret = its + cnps
        
        # 4. Primes fixes
        primes = self._get_primes_fixes(worked_days)
        
        # 5. CMU
        cmu = primes['cmu'] if primes['cmu'] > 0 else self._get_montant_cmu(employee)
        
        # 6. Assurance maladie
        assurance = primes['assurance']
        
        # 7. BRUT_TOTAL = BRUT_IMPOSABLE + primes non imposables
        brut_total = brut_imposable + primes['transport_non_imposable']
        
        # 8. NET_PAIE = BRUT_TOTAL - RET - assurance
        net_paie = brut_total - ret - assurance
        
        # 9. NET FINAL = NET_PAIE - CMU
        net_final = net_paie - cmu
        
        return round(net_final, 0)
    
    def _calculer_sursalaire_inverse(self):
        """
        Calcule le sursalaire par méthode dichotomique OPTIMISÉE
        avec vérification de cohérence
        """
        self.ensure_one()
        
        if not self.net_souhaite or self.net_souhaite <= 0:
            raise UserError("Veuillez saisir un salaire net souhaité valide.")
        
        if not self.wage or self.wage <= 0:
            raise UserError("Veuillez saisir un salaire de base valide.")
        
        if not self.employee_id:
            raise UserError("Veuillez associer un employé au dossier salarial.")
        
        employee = self.employee_id
        
        # Prime d'ancienneté
        anciennete = employee.seniority_employee or 0
        prime_anciennete = self._get_prime_anciennete(self.wage, anciennete)
        
        # Primes fixes
        primes = self._get_primes_fixes()
        
        # BASE FIXE = salaire_base + prime_ancienneté
        # Le TRSP est entièrement non-imposable → n'entre pas dans le BRUT
        base_fixe = self.wage + prime_anciennete
        
        # Paramètres dichotomie optimisés
        sursalaire_min = 0.0
        sursalaire_max = 50000000.0  # Large pour couvrir tous cas
        tolerance = 10  # Tolérance très stricte : 10 FCFA
        max_iterations = 150
        
        best_sursalaire = 0
        best_ecart = float('inf')
        
        _logger.info(f"Début calcul inverse - Net souhaité: {self.net_souhaite}, Base: {self.wage}")
        
        for iteration in range(max_iterations):
            # Point milieu
            sursalaire_test = (sursalaire_min + sursalaire_max) / 2.0
            
            # BRUT_IMPOSABLE = BASE_FIXE + SURSALAIRE
            brut_imposable = base_fixe + sursalaire_test
            
            # Calcul net correspondant
            net_calcule = self._calculer_net_depuis_brut(brut_imposable, employee)
            
            # Écart
            ecart = net_calcule - self.net_souhaite
            
            # Mémoriser le meilleur résultat
            if abs(ecart) < abs(best_ecart):
                best_ecart = ecart
                best_sursalaire = sursalaire_test
            
            # Log tous les 20 itérations
            if iteration % 20 == 0:
                _logger.info(
                    f"Iter {iteration}: sursalaire={sursalaire_test:.2f}, "
                    f"brut={brut_imposable:.2f}, net={net_calcule:.2f}, écart={ecart:.2f}"
                )
            
            # Vérification convergence
            if abs(ecart) <= tolerance:
                _logger.info(f"✓ Convergence atteinte à iter {iteration + 1}, écart={ecart:.2f}")
                return round(sursalaire_test, 0)
            
            # Ajustement bornes
            if ecart < 0:  # Net trop petit → augmenter sursalaire
                sursalaire_min = sursalaire_test
            else:  # Net trop grand → diminuer sursalaire
                sursalaire_max = sursalaire_test
            
            # Arrêt si intervalle trop petit
            if abs(sursalaire_max - sursalaire_min) < 0.01:
                _logger.warning(f"Intervalle minimal atteint à iter {iteration + 1}")
                break
        
        _logger.warning(
            f"Calcul terminé sans convergence exacte après {iteration + 1} iter. "
            f"Meilleur sursalaire: {best_sursalaire:.2f}, écart: {best_ecart:.2f}"
        )
        
        return round(best_sursalaire, 0)
    
    @api.depends('wage', 'extra_pay', 'employee_id', 'employee_id.seniority_employee',
                 'employee_id.part_igr', 'employee_id.part_cmu',
                 'fixed_premiums_ids', 'fixed_premiums_ids.amount')
    def _compute_elements_paie(self):
        """Calcule tous les éléments de paie"""
        for version in self:
            if not version.employee_id:
                version.brut_imposable_calcule = 0
                version.its_calcule = 0
                version.cnps_calcule = 0
                version.cmu_calcule = 0
                version.net_a_payer_calcule = 0
                continue

            employee = version.employee_id
            anciennete = employee.seniority_employee or 0

            prime_anciennete = version._get_prime_anciennete(version.wage, anciennete)
            primes = version._get_primes_fixes()

            version.brut_imposable_calcule = (
                version.wage +
                version.extra_pay +
                prime_anciennete
            )

            version.its_calcule = version._calculer_its(
                version.brut_imposable_calcule,
                employee.part_igr
            )

            base_cnps = min(version.brut_imposable_calcule, 3375000)
            version.cnps_calcule = round(base_cnps * 0.063, 0)

            version.cmu_calcule = (
                primes['cmu'] if primes['cmu'] > 0
                else version._get_montant_cmu(employee)
            )

            version.net_a_payer_calcule = version._calculer_net_depuis_brut(
                version.brut_imposable_calcule,
                employee
            )
    
    def action_calculer_sursalaire(self):
        """Calcule le sursalaire nécessaire"""
        self.ensure_one()
        
        try:
            # Calcul
            sursalaire_calcule = self._calculer_sursalaire_inverse()
            
            # Mise à jour
            self.write({'extra_pay': sursalaire_calcule})
            
            # Forcer recalcul
            self._compute_elements_paie()
            
            # Vérification
            ecart = self.net_a_payer_calcule - self.net_souhaite
            
            # Type notification
            if abs(ecart) <= 50:
                notif_type = 'success'
                icon = '✅'
                precision = 'EXCELLENT'
            elif abs(ecart) <= 200:
                notif_type = 'success'
                icon = '✓'
                precision = 'TRÈS BON'
            elif abs(ecart) <= 500:
                notif_type = 'warning'
                icon = '⚠️'
                precision = 'ACCEPTABLE'
            else:
                notif_type = 'warning'
                icon = '⚠️'
                precision = 'À VÉRIFIER'
            
            message = (
                f'{icon} CALCUL TERMINÉ - Précision: {precision}\n\n'
                f'💰 RÉSULTATS:\n'
                f'  • Sursalaire calculé : {sursalaire_calcule:>15,.0f} FCFA\n'
                f'  • Net obtenu        : {self.net_a_payer_calcule:>15,.0f} FCFA\n'
                f'  • Net souhaité      : {self.net_souhaite:>15,.0f} FCFA\n'
                f'  • Écart             : {ecart:>+16,.0f} FCFA\n\n'
                f'📊 DÉTAILS PAIE:\n'
                f'  • Brut imposable    : {self.brut_imposable_calcule:>15,.0f} FCFA\n'
                f'  • ITS               : {self.its_calcule:>15,.0f} FCFA\n'
                f'  • CNPS (6.3%)       : {self.cnps_calcule:>15,.0f} FCFA\n'
                f'  • CMU               : {self.cmu_calcule:>15,.0f} FCFA'
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': f'{icon} Calcul Sursalaire - {precision}',
                    'message': message,
                    'type': notif_type,
                    'sticky': True,
                }
            }
            
        except Exception as e:
            _logger.error(f"Erreur calcul sursalaire: {str(e)}", exc_info=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '❌ Erreur',
                    'message': f'Erreur lors du calcul : {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_simuler_paie(self):
        """Simulation détaillée de la paie"""
        self.ensure_one()
        
        if not self.employee_id:
            raise UserError("Veuillez associer un employé au dossier salarial.")
        
        employee = self.employee_id
        anciennete = employee.seniority_employee or 0
        
        # Calculs
        prime_anciennete = self._get_prime_anciennete(self.wage, anciennete)
        primes = self._get_primes_fixes()
        
        brut_imposable = (
            self.wage + self.extra_pay + 
            prime_anciennete + primes['transport_imposable']
        )
        
        its = self._calculer_its(brut_imposable, employee.part_igr)
        cnps = round(min(brut_imposable, 3375000) * 0.063, 0)
        cmu = primes['cmu'] if primes['cmu'] > 0 else self._get_montant_cmu(employee)
        transport_ni = primes['transport_non_imposable']
        assurance = primes['assurance']
        
        brut_total = brut_imposable + transport_ni
        ret = its + cnps
        net_paie = brut_total - ret - assurance
        net_final = net_paie - cmu
        
        # Info CMU
        cmu_info = ""
        if hasattr(employee, 'cmu_contributor'):
            if employee.cmu_contributor == 'do_not_contribute':
                cmu_info = " (Ne cotise pas)"
            elif employee.cmu_contributor == 'supported_fifty':
                cmu_info = f" ({employee.part_cmu} parts × 500)"
            elif employee.cmu_contributor == 'fully_supported':
                cmu_info = " (Prise en charge totale)"
            else:
                cmu_info = f" ({employee.part_cmu} parts × 500)"
        
        message = f"""
╔════════════════════════════════════════════════════╗
║        SIMULATION DÉTAILLÉE DE PAIE                ║
╚════════════════════════════════════════════════════╝

👤 EMPLOYÉ : {employee.name}
   Ancienneté : {anciennete} ans (Prime: {min(max(2 + anciennete - 2, 0), 25)}%)
   Part IGR   : {employee.part_igr}
   Part CMU   : {employee.part_cmu}{cmu_info}

┌────────────────────────────────────────────────────┐
│ 💼 ÉLÉMENTS IMPOSABLES                             │
├────────────────────────────────────────────────────┤
│ Salaire de base      : {self.wage:>18,.0f} FCFA │
│ Sursalaire          : {self.extra_pay:>18,.0f} FCFA │
│ Prime ancienneté    : {prime_anciennete:>18,.0f} FCFA │
│ Transport imposable : {primes['transport_imposable']:>18,.0f} FCFA │
├────────────────────────────────────────────────────┤
│ BRUT IMPOSABLE      : {brut_imposable:>18,.0f} FCFA │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ 🎁 ÉLÉMENTS NON IMPOSABLES                         │
├────────────────────────────────────────────────────┤
│ Transport (exonéré) : {transport_ni:>18,.0f} FCFA │
├────────────────────────────────────────────────────┤
│ BRUT TOTAL          : {brut_total:>18,.0f} FCFA │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ 📉 RETENUES OBLIGATOIRES                           │
├────────────────────────────────────────────────────┤
│ ITS                 : {its:>18,.0f} FCFA │
│ CNPS (6.3%)         : {cnps:>18,.0f} FCFA │
│ CMU                 : {cmu:>18,.0f} FCFA │
│ Assurance maladie   : {assurance:>18,.0f} FCFA │
├────────────────────────────────────────────────────┤
│ TOTAL RETENUES      : {its + cnps + cmu + assurance:>18,.0f} FCFA │
└────────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════╗
║ 💰 NET À PAYER      : {net_final:>18,.0f} FCFA ║
╚════════════════════════════════════════════════════╝
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '📊 Simulation de Paie Complète',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_reinitialiser_calcul(self):
        """Réinitialise les calculs"""
        self.ensure_one()
        self.write({
            'net_souhaite': 0.0,
            'extra_pay': 0.0
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '🔄 Réinitialisé',
                'message': 'Les champs ont été réinitialisés.',
                'type': 'info',
            }
        }