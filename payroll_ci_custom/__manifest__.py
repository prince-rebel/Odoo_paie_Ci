# -*- coding: utf-8 -*-
{
    'name': 'Calcul Salarial Côte d\'Ivoire',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Calcul inversé du sursalaire pour atteindre un net souhaité - Côte d\'Ivoire',
    'description': """
Calcul Salarial Côte d'Ivoire
==============================

Ce module permet de calculer automatiquement le sursalaire nécessaire 
pour qu'un employé atteigne le salaire net souhaité.

Fonctionnalités principales :
-----------------------------
* Calcul inversé : du net souhaité au sursalaire
* Calcul automatique de l'ITS selon le nouveau barème ivoirien
* Gestion des primes non imposables (transport, salissure)
* Calcul des cotisations CNPS (salariale et patronale)
* Prise en compte de l'ancienneté automatique
* Gestion des parts IGR pour les réductions d'impôt

Utilisation :
-------------
1. Ouvrir un contrat employé
2. Aller dans l'onglet "Calcul Salarial CI"
3. Saisir le net souhaité par l'employé
4. Cliquer sur "Calculer Sursalaire"
5. Le système génère automatiquement le sursalaire optimal

Le calcul prend en compte :
* Salaire de base
* Prime d'ancienneté (1% par an, max 30%)
* Primes non imposables (à saisir manuellement)
* ITS selon le barème progressif
* Cotisations CNPS (6,3% salariale, 7,7% patronale)
* Parts IGR pour les réductions d'impôt

Barème ITS 2025 :
* 0 à 75 000 : 0%
* 75 001 à 240 000 : 16%
* 240 001 à 800 000 : 21%
* 800 001 à 2 400 000 : 24%
* 2 400 001 à 8 000 000 : 28%
* Au-delà de 8 000 000 : 32%
    """,
    'author': 'Traore Djakaridja',
    'website': 'https://github.com/prince-rebel',
    'depends': [
        'hr',
        'hr_payroll',
        'hr_payroll_custom',
    ],
    'data': [
        'views/hr_contract_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}