# Odoo Paie Côte d'Ivoire

Modules de gestion de la paie ivoirienne pour **Odoo 19.0 Enterprise**.

## Modules inclus

### `hr_custom`
Personnalisations RH de base :
- Gestion des conventions collectives et secteurs d'activité
- Catégories salariales avec grilles de salaires
- Champs spécifiques employé (CNPS, CMU, ancienneté, etc.)
- Alertes de fin de contrat/période d'essai

### `hr_holidays_custom`
Gestion des congés ivoiriens :
- Calcul des congés progressifs (jours calendaires ou ouvrables)
- Allocation congés selon ancienneté
- Reprise de service

### `hr_payroll_custom`
Module principal de paie ivoirienne :
- Règles salariales : IGR, ITS, CNPS (salariale & patronale), CMU, FDFP
- Déclarations fiscales : CNPS mensuelle, ITS mensuelle, CMU mensuelle, FDFP mensuelle, État 301, DISA
- Solde de tout compte
- Primes fixes par employé
- Livre de paie

### `payroll_ci_custom`
Calcul inversé du sursalaire :
- Calcul automatique du sursalaire pour atteindre un net souhaité
- Barème ITS 2025 intégré

## Dépendances

- Odoo 19.0 Enterprise
- `hr`, `hr_payroll`, `hr_payroll_holidays`
- `documents`, `report_xlsx`

## Installation

```bash
# Copier les modules dans le dossier addons
cp -r hr_custom hr_holidays_custom hr_payroll_custom payroll_ci_custom /opt/odoo/custom-addons/

# Mettre à jour la liste des modules puis installer
odoo-bin -d <database> -i hr_custom,hr_holidays_custom,hr_payroll_custom,payroll_ci_custom
```

## Ordre d'installation

1. `hr_custom`
2. `hr_holidays_custom`
3. `hr_payroll_custom`
4. `payroll_ci_custom`
