# -*- coding: utf-8 -*-
from odoo import models, fields, api

# Mapping: DGI field code → (odoo_report_line_code, expression_label, period)
# period: 'current' or 'previous'
ACTIF_MAPPING = {}
for alias in ['AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AP','AQ','AR','AS','AZ',
              'BA','BB','BG','BH','BI','BJ','BK','BQ','BR','BS','BT','BU','BZ']:
    code = f'SYSCOHADA_{alias}'
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_1'] = (code, 'gross', 'current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_2'] = (code, 'depr',  'current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_3'] = (code, 'balance','current')
    ACTIF_MAPPING[f'NO_ACTIF_{alias}_4'] = (code, 'balance','previous')

PASSIF_MAPPING = {}
for alias in ['CA','CB','CD','CE','CF','CG','CH','CJ','CL','CM','CP',
              'DA','DB','DC','DD','DF','DH','DI','DJ','DK','DM','DN','DP',
              'DQ','DR','DT','DV','DZ']:
    code = f'SYSCOHADA_{alias}'
    PASSIF_MAPPING[f'NO_PASSIF_{alias}_1'] = (code, 'balance','current')
    PASSIF_MAPPING[f'NO_PASSIF_{alias}_2'] = (code, 'balance','previous')

RESULTAT_MAPPING = {
    'NO_RESULTAT_TA_1': ('SYSCOHADA_Ventes_de_marchandises',   'balance','current'),
    'NO_RESULTAT_TA_2': ('SYSCOHADA_Ventes_de_marchandises',   'balance','previous'),
    'NO_RESULTAT_RA_1': ('SYSCOHADA_Achats_de_marchandises',   'balance','current'),
    'NO_RESULTAT_RA_2': ('SYSCOHADA_Achats_de_marchandises',   'balance','previous'),
    'NO_RESULTAT_RB_1': ('SYSCOHADA_Variation_de_stocks_mar',  'balance','current'),
    'NO_RESULTAT_RB_2': ('SYSCOHADA_Variation_de_stocks_mar',  'balance','previous'),
    'NO_RESULTAT_XA_1': ('SYSCOHADA_Marge_commerciale ',       'balance','current'),
    'NO_RESULTAT_XA_2': ('SYSCOHADA_Marge_commerciale ',       'balance','previous'),
    'NO_RESULTAT_TB_1': ('SYSCOHADA_Ventes_prod_fab',          'balance','current'),
    'NO_RESULTAT_TB_2': ('SYSCOHADA_Ventes_prod_fab',          'balance','previous'),
    'NO_RESULTAT_TC_1': ('SYSCOHADA_Travaux_services_vn',      'balance','current'),
    'NO_RESULTAT_TC_2': ('SYSCOHADA_Travaux_services_vn',      'balance','previous'),
    'NO_RESULTAT_TD_1': ('SYSCOHADA_Produits_accessoires',     'balance','current'),
    'NO_RESULTAT_TD_2': ('SYSCOHADA_Produits_accessoires',     'balance','previous'),
    'NO_RESULTAT_XB_1': ('SYSCOHADA_Chiffres_affaires',        'balance','current'),
    'NO_RESULTAT_XB_2': ('SYSCOHADA_Chiffres_affaires',        'balance','previous'),
    'NO_RESULTAT_TE_1': ('SYSCOHADA_Produc_stck',              'balance','current'),
    'NO_RESULTAT_TE_2': ('SYSCOHADA_Produc_stck',              'balance','previous'),
    'NO_RESULTAT_TF_1': ('SYSCOHADA_Produc_immo',              'balance','current'),
    'NO_RESULTAT_TF_2': ('SYSCOHADA_Produc_immo',              'balance','previous'),
    'NO_RESULTAT_TG_1': ('SYSCOHADA_Sub_exp',                  'balance','current'),
    'NO_RESULTAT_TG_2': ('SYSCOHADA_Sub_exp',                  'balance','previous'),
    'NO_RESULTAT_TH_1': ('SYSCOHADA_Autres_prod',              'balance','current'),
    'NO_RESULTAT_TH_2': ('SYSCOHADA_Autres_prod',              'balance','previous'),
    'NO_RESULTAT_TI_1': ('SYSCOHADA_Transf_chrg_exp',          'balance','current'),
    'NO_RESULTAT_TI_2': ('SYSCOHADA_Transf_chrg_exp',          'balance','previous'),
    'NO_RESULTAT_RC_1': ('SYSCOHADA_Achats_mat_prem',          'balance','current'),
    'NO_RESULTAT_RC_2': ('SYSCOHADA_Achats_mat_prem',          'balance','previous'),
    'NO_RESULTAT_RD_1': ('SYSCOHADA_Var_stocks_mp',            'balance','current'),
    'NO_RESULTAT_RD_2': ('SYSCOHADA_Var_stocks_mp',            'balance','previous'),
    'NO_RESULTAT_RE_1': ('SYSCOHADA_Autres_achats',            'balance','current'),
    'NO_RESULTAT_RE_2': ('SYSCOHADA_Autres_achats',            'balance','previous'),
    'NO_RESULTAT_RF_1': ('SYSCOHADA_Var_stocks_autres_app',    'balance','current'),
    'NO_RESULTAT_RF_2': ('SYSCOHADA_Var_stocks_autres_app',    'balance','previous'),
    'NO_RESULTAT_RG_1': ('SYSCOHADA_Transports',               'balance','current'),
    'NO_RESULTAT_RG_2': ('SYSCOHADA_Transports',               'balance','previous'),
    'NO_RESULTAT_RH_1': ('SYSCOHADA_Services_ext',             'balance','current'),
    'NO_RESULTAT_RH_2': ('SYSCOHADA_Services_ext',             'balance','previous'),
    'NO_RESULTAT_RI_1': ('SYSCOHADA_impots_et_taxes',          'balance','current'),
    'NO_RESULTAT_RI_2': ('SYSCOHADA_impots_et_taxes',          'balance','previous'),
    'NO_RESULTAT_RJ_1': ('SYSCOHADA_Autres_charges',           'balance','current'),
    'NO_RESULTAT_RJ_2': ('SYSCOHADA_Autres_charges',           'balance','previous'),
    'NO_RESULTAT_XC_1': ('SYSCOHADA_Val_ajoutee',              'balance','current'),
    'NO_RESULTAT_XC_2': ('SYSCOHADA_Val_ajoutee',              'balance','previous'),
    'NO_RESULTAT_RK_1': ('SYSCOHADA_Charges_pers',             'balance','current'),
    'NO_RESULTAT_RK_2': ('SYSCOHADA_Charges_pers',             'balance','previous'),
    'NO_RESULTAT_XD_1': ('SYSCOHADA_EBE',                      'balance','current'),
    'NO_RESULTAT_XD_2': ('SYSCOHADA_EBE',                      'balance','previous'),
    'NO_RESULTAT_TJ_1': ('SYSCOHADA_Reprise_amr_prov_dep',     'balance','current'),
    'NO_RESULTAT_TJ_2': ('SYSCOHADA_Reprise_amr_prov_dep',     'balance','previous'),
    'NO_RESULTAT_RL_1': ('SYSCOHADA_Dot_am_prov_dep',          'balance','current'),
    'NO_RESULTAT_RL_2': ('SYSCOHADA_Dot_am_prov_dep',          'balance','previous'),
    'NO_RESULTAT_XE_1': ('SYSCOHADA_Resultat_exp',             'balance','current'),
    'NO_RESULTAT_XE_2': ('SYSCOHADA_Resultat_exp',             'balance','previous'),
    'NO_RESULTAT_TK_1': ('SYSCOHADA_Revenu_fin_ass',           'balance','current'),
    'NO_RESULTAT_TK_2': ('SYSCOHADA_Revenu_fin_ass',           'balance','previous'),
    'NO_RESULTAT_TL_1': ('SYSCOHADA_Reprise_prov_dep_fin',     'balance','current'),
    'NO_RESULTAT_TL_2': ('SYSCOHADA_Reprise_prov_dep_fin',     'balance','previous'),
    'NO_RESULTAT_TM_1': ('SYSCOHADA_Transferts_charges_fin',   'balance','current'),
    'NO_RESULTAT_TM_2': ('SYSCOHADA_Transferts_charges_fin',   'balance','previous'),
    'NO_RESULTAT_RM_1': ('SYSCOHADA_Frais_fin_chrg_ass',       'balance','current'),
    'NO_RESULTAT_RM_2': ('SYSCOHADA_Frais_fin_chrg_ass',       'balance','previous'),
    'NO_RESULTAT_RN_1': ('SYSCOHADA_Dot_prov_dep_fin',         'balance','current'),
    'NO_RESULTAT_RN_2': ('SYSCOHADA_Dot_prov_dep_fin',         'balance','previous'),
    'NO_RESULTAT_XF_1': ('SYSCOHADA_Resultat_fin',             'balance','current'),
    'NO_RESULTAT_XF_2': ('SYSCOHADA_Resultat_fin',             'balance','previous'),
    'NO_RESULTAT_XG_1': ('SYSCOHADA_Resultat_AO',              'balance','current'),
    'NO_RESULTAT_XG_2': ('SYSCOHADA_Resultat_AO',              'balance','previous'),
    'NO_RESULTAT_TN_1': ('SYSCOHADA_Prod_cess_immo',           'balance','current'),
    'NO_RESULTAT_TN_2': ('SYSCOHADA_Prod_cess_immo',           'balance','previous'),
    'NO_RESULTAT_TO_1': ('SYSCOHADA_Autres_prod_HAO',          'balance','current'),
    'NO_RESULTAT_TO_2': ('SYSCOHADA_Autres_prod_HAO',          'balance','previous'),
    'NO_RESULTAT_RO_1': ('SYSCOHADA_Val_comp_cess_immo',       'balance','current'),
    'NO_RESULTAT_RO_2': ('SYSCOHADA_Val_comp_cess_immo',       'balance','previous'),
    'NO_RESULTAT_RP_1': ('SYSCOHADA_Autres_chrg_HAO',          'balance','current'),
    'NO_RESULTAT_RP_2': ('SYSCOHADA_Autres_chrg_HAO',          'balance','previous'),
    'NO_RESULTAT_XH_1': ('SYSCOHADA_Resultat_HAO',             'balance','current'),
    'NO_RESULTAT_XH_2': ('SYSCOHADA_Resultat_HAO',             'balance','previous'),
    'NO_RESULTAT_RQ_1': ('SYSCOHADA_Part_trav',                'balance','current'),
    'NO_RESULTAT_RQ_2': ('SYSCOHADA_Part_trav',                'balance','previous'),
    'NO_RESULTAT_RS_1': ('SYSCOHADA_Impots_resultat',          'balance','current'),
    'NO_RESULTAT_RS_2': ('SYSCOHADA_Impots_resultat',          'balance','previous'),
    'NO_RESULTAT_XI_1': ('SYSCOHADA_XI',                       'balance','current'),
    'NO_RESULTAT_XI_2': ('SYSCOHADA_XI',                       'balance','previous'),
}

TFT_MAPPING = {}
for alias in ['ZA','FA','FB','FC','FD','FE','ZB','FF','FG','FH','FI','FJ','ZC',
              'FK','FL','FM','FN','ZD','FO','FP','FQ','ZE','ZF','ZG','ZH']:
    code = f'CI_TFT_{alias}'
    TFT_MAPPING[f'NO_TFT_{alias}_1'] = (code, 'balance', 'current')
    TFT_MAPPING[f'NO_TFT_{alias}_2'] = (code, 'balance', 'previous')

ALL_FINANCIAL_MAPPINGS = {**ACTIF_MAPPING, **PASSIF_MAPPING, **RESULTAT_MAPPING, **TFT_MAPPING}

# Alias sets for ACTIF / PASSIF split
_ACTIF_ALIASES = frozenset([
    'AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AP',
    'AQ','AR','AS','AZ','BA','BB','BG','BH','BI','BJ','BK',
    'BQ','BR','BS','BT','BU','BZ',
])
_PASSIF_ALIASES = frozenset([
    'CA','CB','CD','CE','CF','CG','CH','CJ','CL','CM','CP',
    'DA','DB','DC','DD','DF','DH','DI','DJ','DK','DM','DN','DP',
    'DQ','DR','DT','DV','DZ',
])

# ── OHADA display definitions ────────────────────────────────────────────────
# (ref, label, note_ref, is_total, is_section)
_ACTIF_LINES = [
    ('AD', 'IMMOBILISATIONS INCORPORELLES',                         '3',  False, True),
    ('AE', 'Frais de développement et de prospection',              None, False, False),
    ('AF', 'Brevets, licences, logiciels et droits similaires',     None, False, False),
    ('AG', 'Fonds commercial et droit au bail',                     None, False, False),
    ('AH', 'Autres immobilisations incorporelles',                  None, False, False),
    ('AI', 'IMMOBILISATIONS CORPORELLES',                           '3',  False, True),
    ('AJ', 'Terrains',                                              None, False, False),
    ('AK', 'Bâtiments',                                             None, False, False),
    ('AL', 'Aménagements, agencements et installations',            None, False, False),
    ('AM', 'Matériel, mobilier et actifs biologiques',              None, False, False),
    ('AN', 'Matériel de transport',                                 None, False, False),
    ('AP', 'AVANCES ET ACOMPTES VERSÉS SUR IMMOBILISATIONS',        None, False, True),
    ('AQ', 'IMMOBILISATIONS FINANCIÈRES',                           '4',  False, True),
    ('AR', 'Titres de participation',                               None, False, False),
    ('AS', 'Autres immobilisations financières',                    None, False, False),
    ('AZ', 'TOTAL ACTIF IMMOBILISÉ',                                None, True,  False),
    ('BA', 'ACTIF CIRCULANT HAO',                                   '5',  False, True),
    ('BB', 'STOCKS ET ENCOURS',                                     '6',  False, True),
    ('BG', 'CRÉANCES ET EMPLOIS ASSIMILÉS',                         None, False, True),
    ('BH', 'Fournisseurs, avances versées',                         '17', False, False),
    ('BI', 'Clients',                                               '7',  False, False),
    ('BJ', 'Autres créances',                                       '8',  False, False),
    ('BK', 'TOTAL ACTIF CIRCULANT',                                 None, True,  False),
    ('BQ', 'Titres de placement',                                   '9',  False, False),
    ('BR', 'Valeurs à encaisser',                                   '10', False, False),
    ('BS', 'Banques, chèques postaux, caisse et assimilés',         '11', False, False),
    ('BT', 'TOTAL TRÉSORERIE-ACTIF',                                None, True,  False),
    ('BU', 'Écart de conversion-Actif',                             '12', False, False),
    ('BZ', 'TOTAL GÉNÉRAL',                                         None, True,  False),
]

# (ref, label, note_ref, is_total, is_section)
_PASSIF_LINES = [
    ('CA', 'Capital',                                                        '13', False, False),
    ('CB', "Apporteurs capital, capital non appelé (-)",                     '13', False, False),
    ('CD', 'Primes liées au capital social',                                 '14', False, False),
    ('CE', 'Écarts de réévaluation',                                         '3e', False, False),
    ('CF', 'Réserves indisponibles',                                         '14', False, False),
    ('CG', 'Réserves libres',                                                '14', False, False),
    ('CH', 'Report à nouveau (+ ou -)',                                      '14', False, False),
    ('CJ', "Résultat net de l'exercice (bénéfice + ou perte -)",             None, False, False),
    ('CL', "Subventions d'investissement",                                   '15', False, False),
    ('CM', 'Provisions réglementées',                                        '15', False, False),
    ('CP', 'TOTAL CAPITAUX PROPRES ET RESSOURCES ASSIMILÉES',                None, True,  False),
    ('DA', 'Emprunts et dettes financières',                                  '16', False, False),
    ('DB', 'Dettes de location-acquisition',                                  '16', False, False),
    ('DC', 'Provisions pour risques et charges',                              '16', False, False),
    ('DD', 'TOTAL DETTES FINANCIÈRES ET RESSOURCES ASSIMILÉES',              None, True,  False),
    ('DF', 'TOTAL RESSOURCES STABLES',                                        None, True,  False),
    ('DH', 'Dettes circulantes HAO',                                          '5',  False, False),
    ('DI', 'Clients, avances reçues',                                         '7',  False, False),
    ('DJ', "Fournisseurs d'exploitation",                                      '17', False, False),
    ('DK', 'Dettes fiscales et sociales',                                      '18', False, False),
    ('DM', 'Autres dettes',                                                    '19', False, False),
    ('DN', 'Provisions pour risques à court terme',                            '19', False, False),
    ('DP', 'TOTAL PASSIF CIRCULANT',                                           None, True,  False),
    ('DQ', "Banques, crédits d'escompte",                                     '20', False, False),
    ('DR', 'Banques, établissements financiers et crédits de trésorerie',     '20', False, False),
    ('DT', 'TOTAL TRÉSORERIE-PASSIF',                                          None, True,  False),
    ('DV', 'Écart de conversion-Passif',                                       '12', False, False),
    ('DZ', 'TOTAL GÉNÉRAL',                                                    None, True,  False),
]

# alias → Odoo report line code (for compte de résultat)
_RESULTAT_CODE_MAP = {
    'TA': 'SYSCOHADA_Ventes_de_marchandises',
    'RA': 'SYSCOHADA_Achats_de_marchandises',
    'RB': 'SYSCOHADA_Variation_de_stocks_mar',
    'XA': 'SYSCOHADA_Marge_commerciale ',
    'TB': 'SYSCOHADA_Ventes_prod_fab',
    'TC': 'SYSCOHADA_Travaux_services_vn',
    'TD': 'SYSCOHADA_Produits_accessoires',
    'XB': 'SYSCOHADA_Chiffres_affaires',
    'TE': 'SYSCOHADA_Produc_stck',
    'TF': 'SYSCOHADA_Produc_immo',
    'TG': 'SYSCOHADA_Sub_exp',
    'TH': 'SYSCOHADA_Autres_prod',
    'TI': 'SYSCOHADA_Transf_chrg_exp',
    'RC': 'SYSCOHADA_Achats_mat_prem',
    'RD': 'SYSCOHADA_Var_stocks_mp',
    'RE': 'SYSCOHADA_Autres_achats',
    'RF': 'SYSCOHADA_Var_stocks_autres_app',
    'RG': 'SYSCOHADA_Transports',
    'RH': 'SYSCOHADA_Services_ext',
    'RI': 'SYSCOHADA_impots_et_taxes',
    'RJ': 'SYSCOHADA_Autres_charges',
    'XC': 'SYSCOHADA_Val_ajoutee',
    'RK': 'SYSCOHADA_Charges_pers',
    'XD': 'SYSCOHADA_EBE',
    'TJ': 'SYSCOHADA_Reprise_amr_prov_dep',
    'RL': 'SYSCOHADA_Dot_am_prov_dep',
    'XE': 'SYSCOHADA_Resultat_exp',
    'TK': 'SYSCOHADA_Revenu_fin_ass',
    'TL': 'SYSCOHADA_Reprise_prov_dep_fin',
    'TM': 'SYSCOHADA_Transferts_charges_fin',
    'RM': 'SYSCOHADA_Frais_fin_chrg_ass',
    'RN': 'SYSCOHADA_Dot_prov_dep_fin',
    'XF': 'SYSCOHADA_Resultat_fin',
    'XG': 'SYSCOHADA_Resultat_AO',
    'TN': 'SYSCOHADA_Prod_cess_immo',
    'TO': 'SYSCOHADA_Autres_prod_HAO',
    'RO': 'SYSCOHADA_Val_comp_cess_immo',
    'RP': 'SYSCOHADA_Autres_chrg_HAO',
    'XH': 'SYSCOHADA_Resultat_HAO',
    'RQ': 'SYSCOHADA_Part_trav',
    'RS': 'SYSCOHADA_Impots_resultat',
    'XI': 'SYSCOHADA_XI',
}

# (ref, label, ab_col, sign, note_ref, is_total)
_RESULTAT_LINES = [
    ('TA', 'Ventes de marchandises',                                           'A',  '+',  '21', False),
    ('RA', 'Achats de marchandises',                                           None, '-',  '22', False),
    ('RB', 'Variation de stocks de marchandises',                              None, '±',  None, False),
    ('XA', 'MARGE COMMERCIALE (Somme TA à RB)',                                None, '+',  None, True),
    ('TB', 'Ventes de produits fabriqués',                                     'B',  '+',  '21', False),
    ('TC', 'Travaux, services vendus',                                         'C',  '+',  '21', False),
    ('TD', 'Produits accessoires',                                             'D',  '+',  '21', False),
    ('XB', "CHIFFRE D'AFFAIRES (A + B + C + D)",                              None, '+',  None, True),
    ('TE', 'Production stockée ou déstockée (+ ou -)',                        None, '±',  None, False),
    ('TF', 'Production immobilisée',                                           None, '+',  None, False),
    ('TG', "Subventions d'exploitation",                                       None, '+',  None, False),
    ('TH', 'Autres produits',                                                  None, '+',  None, False),
    ('TI', 'Transferts de charges',                                            None, '+',  None, False),
    ('RC', 'Achats de matières premières et fournitures liées',                None, '-',  '22', False),
    ('RD', 'Variation de stocks de matières premières',                        None, '±',  None, False),
    ('RE', 'Autres achats',                                                    None, '-',  '22', False),
    ('RF', "Variation de stocks d'autres approvisionnements",                  None, '±',  None, False),
    ('RG', 'Transports',                                                       None, '-',  '23', False),
    ('RH', 'Services extérieurs',                                              None, '-',  '24', False),
    ('RI', 'Impôts et taxes',                                                  None, '-',  '25', False),
    ('RJ', 'Autres charges',                                                   None, '-',  '26', False),
    ('XC', 'VALEUR AJOUTÉE (XB + RA + RB à RJ)',                              None, '+',  None, True),
    ('RK', 'Charges de personnel',                                             None, '-',  '27', False),
    ('XD', "EXCÉDENT BRUT D'EXPLOITATION (XC + RK)",                         None, '+',  None, True),
    ('TJ', "Reprises d'amortissements, provisions et dépréciations",          None, '+',  None, False),
    ('RL', 'Dotations aux amortissements, aux provisions et dépréciations',   None, '-',  '28', False),
    ('XE', "RÉSULTAT D'EXPLOITATION (XD + TJ + RL)",                         None, '+',  None, True),
    ('TK', 'Revenus financiers et produits assimilés',                         None, '+',  '29', False),
    ('TL', 'Reprises de provisions et dépréciations financières',             None, '+',  None, False),
    ('TM', 'Transferts de charges financières',                                None, '+',  None, False),
    ('RM', 'Frais financiers et charges assimilées',                           None, '-',  '29', False),
    ('RN', 'Dotations aux provisions et dépréciations financières',           None, '-',  None, False),
    ('XF', 'RÉSULTAT FINANCIER (TK + TL + TM + RM + RN)',                    None, '+',  None, True),
    ('XG', 'RÉSULTAT DES ACTIVITÉS ORDINAIRES (XE + XF)',                    None, '+',  None, True),
    ('TN', "Produits des cessions d'immobilisations",                          None, '+',  '30', False),
    ('TO', 'Autres Produits HAO',                                              None, '+',  '30', False),
    ('RO', "Valeurs comptables des cessions d'immobilisations",               None, '-',  '30', False),
    ('RP', 'Autres Charges HAO',                                               None, '-',  '30', False),
    ('XH', 'RÉSULTAT HORS ACTIVITÉS ORDINAIRES (TN + TO + RO + RP)',         None, '+',  None, True),
    ('RQ', 'Participation des travailleurs',                                   None, '-',  None, False),
    ('RS', "Impôts sur le résultat",                                           None, '-',  '37', False),
    ('XI', 'RÉSULTAT NET (XG + XH + RQ + RS)',                                None, '+',  None, True),
]

# (ref, label, letter, note_ref, is_total, is_subtitle)
_TFT_LINES = [
    ('ZA', "Trésorerie nette au 1er janvier (Tréso. actif N-1 − Tréso. passif N-1)", 'A', None, False, False),
    (None, 'FLUX DE TRÉSORERIE PROVENANT DES ACTIVITÉS OPÉRATIONNELLES',              None, None, False, True),
    ('FA', "Capacité d'autofinancement globale (CAFG)",                               'B', None, False, False),
    ('FB', "(-) Acquisitions moins cessions d'actifs courants HAO",                   'C', None, False, False),
    ('FC', "(-) Variation du besoin en fonds de roulement lié à l'activité",          'D', None, False, False),
    ('FD', '     Dont variation des stocks',                                           None, None, False, False),
    ('FE', '     Dont variation des créances',                                         None, None, False, False),
    ('ZB', "FLUX DE TRÉSORERIE GÉNÉRÉ PAR L'ACTIVITÉ OPÉRATIONNELLE (B+C+D)",        None, None, True,  False),
    (None, "FLUX DE TRÉSORERIE PROVENANT DES ACTIVITÉS D'INVESTISSEMENT",             None, None, False, True),
    ('FF', "(-) Acquisitions d'immobilisations incorporelles",                         'E', None, False, False),
    ('FG', "(-) Acquisitions d'immobilisations corporelles",                           'E', None, False, False),
    ('FH', "(-) Acquisitions d'immobilisations financières",                           'E', None, False, False),
    ('FI', "(+) Cessions d'immobilisations incorporelles et corporelles",              'E', None, False, False),
    ('FJ', "(+) Cessions ou remboursements d'immobilisations financières",             'E', None, False, False),
    ('ZC', "FLUX DE TRÉSORERIE LIÉS AUX OPÉRATIONS D'INVESTISSEMENT (E)",            None, None, True,  False),
    (None, 'FLUX DE TRÉSORERIE PROVENANT DES ACTIVITÉS DE FINANCEMENT',               None, None, False, True),
    ('FK', 'Augmentations de capital par apports nouveaux',                            'F', None, False, False),
    ('FL', "Subventions d'investissement reçues",                                      'F', None, False, False),
    ('FM', 'Remboursements des capitaux propres',                                      'F', None, False, False),
    ('FN', 'Emprunts',                                                                 'F', None, False, False),
    ('FO', "Remboursements d'emprunts",                                                'G', None, False, False),
    ('FP', 'Augmentations des dettes financières',                                     'G', None, False, False),
    ('FQ', 'Remboursements des dettes financières',                                    'G', None, False, False),
    ('ZD', 'FLUX DE TRÉSORERIE LIÉS AUX OPÉRATIONS DE FINANCEMENT (F+G)',            None, None, True,  False),
    ('ZE', 'VARIATION DE LA TRÉSORERIE NETTE DE LA PÉRIODE (ZB+ZC+ZD)',              None, None, True,  False),
    ('ZF', 'Trésorerie nette au 31 décembre (ZA+ZE = ZF)',                            'H', None, True,  False),
    ('ZG', 'Contrôle : Trésorerie actif N − Trésorerie passif N',                    None, None, False, False),
    ('ZH', 'Écart (ZF − ZG)',                                                          None, None, False, False),
]

_FICHE_R4_NOTES = [
    ('NOTE 1',      'DETTES GARANTIES PAR DES SÛRETÉS RÉELLES ET ENGAGEMENTS FINANCIERS'),
    ('NOTE 2',      'INFORMATIONS OBLIGATOIRES'),
    ('NOTE 3A',     'IMMOBILISATIONS BRUTES'),
    ('NOTE 3B',     'BIENS PRIS EN LOCATION-ACQUISITION'),
    ('NOTE 3C',     'IMMOBILISATIONS : AMORTISSEMENTS'),
    ('NOTE 3C bis', 'IMMOBILISATIONS : DÉPRÉCIATIONS'),
    ('NOTE 3D',     'IMMOBILISATIONS : PLUS-VALUES ET MOINS-VALUES DE CESSION'),
    ('NOTE 3E',     'INFORMATIONS SUR LES RÉÉVALUATIONS'),
    ('NOTE 4',      'IMMOBILISATIONS FINANCIÈRES ET ENTREPRISES LIÉES'),
    ('NOTE 5',      'ACTIF ET PASSIF CIRCULANT HAO'),
    ('NOTE 6',      'STOCKS ET ENCOURS'),
    ('NOTE 7',      'CLIENTS'),
    ('NOTE 8',      'AUTRES CRÉANCES'),
    ('NOTE 8A',     'CHARGES IMMOBILISÉES'),
    ('NOTE 8B',     'PROVISIONS POUR CHARGES À RÉPARTIR'),
    ('NOTE 8C',     'PROVISIONS POUR ENGAGEMENTS DE RETRAITE ET OBLIGATIONS SIMILAIRES'),
    ('NOTE 9',      'TITRES DE PLACEMENT'),
    ('NOTE 10',     'VALEURS À ENCAISSER'),
    ('NOTE 11',     'DISPONIBILITÉS'),
    ('NOTE 12',     'ÉCARTS DE CONVERSION'),
    ('NOTE 13',     'CAPITAL'),
    ('NOTE 14',     'PRIMES ET RÉSERVES'),
    ('NOTE 15A',    "SUBVENTIONS D'INVESTISSEMENT ET PROVISIONS RÉGLEMENTÉES"),
    ('NOTE 15B',    'AUTRES FONDS PROPRES'),
    ('NOTE 16A',    'DETTES FINANCIÈRES ET RESSOURCES ASSIMILÉES'),
    ('NOTE 16B',    'ENGAGEMENTS DE RETRAITE'),
    ('NOTE 16B bis','ACTIFS ET PASSIFS DES RÉGIMES FINANCÉS'),
    ('NOTE 16C',    'ACTIFS ET PASSIFS ÉVENTUELS'),
    ('NOTE 17',     "FOURNISSEURS D'EXPLOITATION"),
    ('NOTE 18',     'DETTES FISCALES ET SOCIALES'),
    ('NOTE 19',     'AUTRES DETTES'),
    ('NOTE 20',     'BANQUES ET ÉTABLISSEMENTS FINANCIERS'),
    ('NOTE 21',     "CHIFFRE D'AFFAIRES ET AUTRES PRODUITS"),
    ('NOTE 22',     'ACHATS'),
    ('NOTE 23',     'TRANSPORTS'),
    ('NOTE 24',     'SERVICES EXTÉRIEURS'),
    ('NOTE 25',     'IMPÔTS ET TAXES'),
    ('NOTE 26',     'AUTRES CHARGES'),
    ('NOTE 27A',    'CHARGES DE PERSONNEL'),
    ('NOTE 27B',    'EFFECTIFS, MASSE SALARIALE ET FRAIS DE PERSONNEL'),
    ('NOTE 28',     'DOTATIONS ET CHARGES PROVISIONNÉES'),
    ('NOTE 29',     'CHARGES ET REVENUS FINANCIERS'),
    ('NOTE 30',     'AUTRES CHARGES ET PRODUITS HAO'),
    ('NOTE 31',     'RÉPARTITION DU RÉSULTAT'),
    ('NOTE 32',     "DÉTAIL DE LA PRODUCTION DE L'EXERCICE"),
    ('NOTE 33',     'DÉTAIL DES ACHATS DESTINÉS À LA PRODUCTION'),
    ('NOTE 34',     'INDICATEURS FINANCIERS DE SYNTHÈSE'),
    ('NOTE 35',     'INFORMATIONS SOCIALES ET SOCIÉTALES'),
    ('NOTE 36',     'TABLE DES CODES'),
    ('NOTE 37',     "DÉTERMINATION DE L'IMPÔT SUR LE RÉSULTAT"),
    ('NOTE 38',     'ÉVÉNEMENTS POSTÉRIEURS À LA CLÔTURE'),
    ('NOTE 39',     "CHANGEMENTS DE MÉTHODES ET CORRECTIONS D'ERREURS"),
]


class L10nCiLiasseExport(models.AbstractModel):
    _name = 'l10n.ci.liasse.export'
    _description = 'CI Liasse Fiscale XML Export Helper'

    # ──────────────────────────────────────────────────────────
    #  Report data helpers (XML + Excel)
    # ──────────────────────────────────────────────────────────

    def _get_report_options(self, report, date_from, date_to, company, previous=False):
        from dateutil.relativedelta import relativedelta
        if previous:
            date_from = date_from - relativedelta(years=1)
            date_to   = date_to   - relativedelta(years=1)
        return report.get_options({
            'date': {
                'date_from': fields.Date.to_string(date_from),
                'date_to':   fields.Date.to_string(date_to),
                'mode':      'range',
                'filter':    'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })

    def _fetch_report_values(self, report_xmlid, date_from, date_to, company):
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return {}, {}

        line_code_by_id = {
            rec.id: rec.code
            for rec in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        result_cur, result_prev = {}, {}
        for period, target in [('current', result_cur), ('previous', result_prev)]:
            options = self._get_report_options(report, date_from, date_to, company, period == 'previous')
            lines   = report._get_lines(options)
            col_defs = options.get('columns', [])
            for line in lines:
                line_id = line.get('id')
                code = line_code_by_id.get(line_id) if isinstance(line_id, int) else None
                if not code:
                    continue
                col_vals = {}
                for col, col_def in zip(line.get('columns', []), col_defs):
                    label = col_def.get('expression_label', '')
                    col_vals[label] = col.get('no_format', 0) or 0
                target[code] = col_vals

        return result_cur, result_prev

    def _get_expression_value(self, vals_cur, vals_prev, odoo_code, label, period):
        source = vals_cur if period == 'current' else vals_prev
        return (source.get(odoo_code, {}).get(label, 0) or 0)

    # ──────────────────────────────────────────────────────────
    #  XML generation
    # ──────────────────────────────────────────────────────────

    def generate_xml(self, date_from, date_to, company, liasse_type='NO'):
        from lxml import etree
        import math

        def fmt(val):
            if val is None:
                return ''
            try:
                v = float(val)
                if math.isnan(v) or math.isinf(v):
                    return ''
                return str(int(round(v)))
            except (TypeError, ValueError):
                return str(val)

        bilan_cur, bilan_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
            date_from, date_to, company,
        )
        cr_cur, cr_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_pl',
            date_from, date_to, company,
        )
        tft_cur, tft_prev = self._fetch_report_values(
            'l10n_ci_liasse_fiscale.l10n_ci_tft',
            date_from, date_to, company,
        )

        all_cur  = {**bilan_cur,  **cr_cur,  **tft_cur}
        all_prev = {**bilan_prev, **cr_prev, **tft_prev}

        root = etree.Element('liasse')
        root.set('type', liasse_type)
        root.set('ncc', company.vat or '')
        root.set('exercice', str(date_to.year))

        entete = etree.SubElement(root, 'entete')
        etree.SubElement(entete, 'raison_sociale').text = company.name or ''
        etree.SubElement(entete, 'date_debut').text = fields.Date.to_string(date_from)
        etree.SubElement(entete, 'date_fin').text   = fields.Date.to_string(date_to)
        etree.SubElement(entete, 'monnaie').text    = company.currency_id.name or 'XOF'

        champs = etree.SubElement(root, 'champs')
        for dgi_code, (odoo_code, label, period) in ALL_FINANCIAL_MAPPINGS.items():
            source    = all_cur if period == 'current' else all_prev
            line_data = source.get(odoo_code, {})
            val = line_data.get(label, 0) or 0
            el  = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = fmt(val)

        company_fields = {
            'NO_FR1_ZA1_1': fields.Date.to_string(date_from),
            'NO_FR1_ZA2_1': fields.Date.to_string(date_to),
            'NO_FR1_ZK4_1': company.city or '',
            'NO_FR1_ZL_1':  company.street or '',
            'NO_FR1_ZK2_1': company.zip or '',
            'NO_FR1_ZK1_1': company.email or '',
        }
        for dgi_code, val in company_fields.items():
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = str(val)

        return etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)

    # ──────────────────────────────────────────────────────────
    #  Excel styling helpers
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _xl_palette():
        return {
            'dark':  '1F4E79',  # deep blue — company / col headers
            'mid':   '2E75B6',  # medium blue — period rows
            'total': 'DEEAF1',  # very light blue — level-0 totals
            'sect':  'BDD7EE',  # light blue — level-1 sections
            'white': 'FFFFFF',
            'fill':  'FFF2CC',  # light yellow — editable cells
            'gray':  'F2F2F2',
        }

    def _xl_hdr(self, cell, bg, fg='FFFFFF', bold=True, sz=10, halign='center'):
        from openpyxl.styles import Font, PatternFill, Alignment
        cell.font      = Font(name='Calibri', bold=bold, color=fg, size=sz)
        cell.fill      = PatternFill(fill_type='solid', fgColor=bg)
        cell.alignment = Alignment(horizontal=halign, vertical='center', wrap_text=True)

    @staticmethod
    def _xl_num(val):
        if val is None:
            return None
        try:
            v = float(val)
            return int(round(v)) if v != 0.0 else None
        except (TypeError, ValueError):
            return None

    # ──────────────────────────────────────────────────────────
    #  OHADA standard company header (rows 1-7)
    # ──────────────────────────────────────────────────────────

    def _xl_ohada_header(self, ws, company, date_to_str, page_title, ncols=9):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        fill_in = PatternFill(fill_type='solid', fgColor='EBF3FA')
        lbl_font = Font(name='Calibri', bold=True, size=9)
        val_font = Font(name='Calibri', size=9)

        # Row 1: page type top-right
        if ncols > 2:
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols - 2)
        c = ws.cell(row=1, column=max(1, ncols - 1), value=page_title)
        if ncols > 2:
            ws.merge_cells(start_row=1, start_column=ncols - 1, end_row=1, end_column=ncols)
        c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
        c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = 32

        def lbl(r, col, text):
            c2 = ws.cell(row=r, column=col, value=text)
            c2.font = lbl_font

        def val(r, col, text, end_col=None):
            c2 = ws.cell(row=r, column=col, value=text)
            c2.font = val_font
            c2.fill = fill_in
            if end_col and end_col > col:
                ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=end_col)
            return c2

        # Row 2: separator
        ws.row_dimensions[2].height = 4

        # Row 3: Dénomination | value ……… Sigle usuel | value
        lbl(3, 1, "Dénomination sociale de l'entité :")
        val(3, 2, company.name or '', end_col=min(5, ncols - 2))
        lbl(3, min(6, ncols - 1), 'Sigle usuel :')
        val(3, min(7, ncols), '', end_col=ncols)
        ws.row_dimensions[3].height = 14

        # Row 4: Adresse
        lbl(4, 1, 'Adresse :')
        addr = ' '.join(filter(None, [company.street or '', company.zip or '', company.city or '']))
        val(4, 2, addr, end_col=ncols)
        ws.row_dimensions[4].height = 14

        # Row 5: NCC | date clos | durée
        lbl(5, 1, 'N° compte contribuable (NCC) :')
        val(5, 2, company.vat or '')
        lbl(5, 3, 'Exercice clos le :')
        val(5, 4, date_to_str)
        lbl(5, 5, 'Durée (en mois) :')
        val(5, 6, 12)
        ws.row_dimensions[5].height = 14

        # Row 6: NTD
        lbl(6, 1, 'N° de télédéclarant (NTD) :')
        val(6, 2, '', end_col=4)
        ws.row_dimensions[6].height = 14

        ws.row_dimensions[7].height = 6  # spacer before column headers

    # ──────────────────────────────────────────────────────────
    #  OHADA financial states
    # ──────────────────────────────────────────────────────────

    def _xl_add_actif_ohada(self, wb, company, date_from_str, date_to_str, date_from, date_to):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='ACTIF')

        # Column widths: A=5 B=52 C=4 D=4 E=6 F=16 G=16 H=16 I=16
        for col, w in zip('ABCDEEFGHI', [5, 52, 3, 3, 6, 16, 16, 16, 16]):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(list('ABCDEFGHI').index(col) + 1)].width = w
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 52
        ws.column_dimensions['C'].width = 3
        ws.column_dimensions['D'].width = 3
        ws.column_dimensions['E'].width = 6
        ws.column_dimensions['F'].width = 16
        ws.column_dimensions['G'].width = 16
        ws.column_dimensions['H'].width = 16
        ws.column_dimensions['I'].width = 16

        self._xl_ohada_header(ws, company, date_to_str,
                              f'BILAN SYSTÈME NORMAL\nPAGE 1/2', ncols=9)

        # Row 8: column headers
        hdrs = [('REF', 1), ('ACTIF', 2), ('NOTE', 5),
                ('BRUT', 6), ('AMORT. ET DÉPRÉC.', 7), ('NET', 8), ('NET N-1', 9)]
        for text, col in hdrs:
            c = ws.cell(row=8, column=col, value=text)
            c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells(start_row=8, start_column=2, end_row=8, end_column=4)
        ws.row_dimensions[8].height = 28

        # Fetch data
        vals_cur, vals_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
            date_from, date_to, company,
        )

        row = 9
        for ref, label, note_ref, is_total, is_section in _ACTIF_LINES:
            odoo_code = f'SYSCOHADA_{ref}'
            brut = self._xl_num((vals_cur.get(odoo_code) or {}).get('gross', 0))
            depr = self._xl_num((vals_cur.get(odoo_code) or {}).get('depr', 0))
            net  = self._xl_num((vals_cur.get(odoo_code) or {}).get('balance', 0))
            net1 = self._xl_num((vals_prev.get(odoo_code) or {}).get('balance', 0))

            bold = is_total or is_section
            bg = P['total'] if is_total else (P['sect'] if is_section else None)

            def _cell(r, col, val_v, halign='center', bold_=None):
                c = ws.cell(row=r, column=col, value=val_v)
                c.font = Font(name='Calibri', bold=bold_ if bold_ is not None else bold, size=9)
                c.alignment = Alignment(horizontal=halign, vertical='center')
                if bg:
                    c.fill = PatternFill(fill_type='solid', fgColor=bg)
                if val_v and isinstance(val_v, int):
                    c.number_format = '#,##0'
                return c

            _cell(row, 1, ref)
            c_lbl = ws.cell(row=row, column=2, value=label)
            c_lbl.font = Font(name='Calibri', bold=bold, size=9)
            c_lbl.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                c_lbl.fill = PatternFill(fill_type='solid', fgColor=bg)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)

            _cell(row, 5, note_ref or '')
            _cell(row, 6, brut, halign='right')
            _cell(row, 7, depr, halign='right')
            _cell(row, 8, net,  halign='right')
            _cell(row, 9, net1, halign='right')
            ws.row_dimensions[row].height = 14
            row += 1

    def _xl_add_passif_ohada(self, wb, company, date_from_str, date_to_str, date_from, date_to):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='PASSIF')

        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 60
        ws.column_dimensions['C'].width = 3
        ws.column_dimensions['D'].width = 3
        ws.column_dimensions['E'].width = 3
        ws.column_dimensions['F'].width = 3
        ws.column_dimensions['G'].width = 6
        ws.column_dimensions['H'].width = 16
        ws.column_dimensions['I'].width = 16

        self._xl_ohada_header(ws, company, date_to_str,
                              f'BILAN SYSTÈME NORMAL\nPAGE 2/2', ncols=9)

        hdrs = [('REF', 1), ('PASSIF', 2), ('NOTE', 7), ('NET N', 8), ('NET N-1', 9)]
        for text, col in hdrs:
            c = ws.cell(row=8, column=col, value=text)
            c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells(start_row=8, start_column=2, end_row=8, end_column=6)
        ws.row_dimensions[8].height = 28

        vals_cur, vals_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_bilan',
            date_from, date_to, company,
        )

        row = 9
        for ref, label, note_ref, is_total, is_section in _PASSIF_LINES:
            odoo_code = f'SYSCOHADA_{ref}'
            net  = self._xl_num((vals_cur.get(odoo_code) or {}).get('balance', 0))
            net1 = self._xl_num((vals_prev.get(odoo_code) or {}).get('balance', 0))

            bold = is_total or is_section
            bg = P['total'] if is_total else (P['sect'] if is_section else None)

            def _c(r, col, val_v, halign='center'):
                c = ws.cell(row=r, column=col, value=val_v)
                c.font = Font(name='Calibri', bold=bold, size=9)
                c.alignment = Alignment(horizontal=halign, vertical='center')
                if bg:
                    c.fill = PatternFill(fill_type='solid', fgColor=bg)
                if val_v and isinstance(val_v, int):
                    c.number_format = '#,##0'
                return c

            _c(row, 1, ref)
            c_lbl = ws.cell(row=row, column=2, value=label)
            c_lbl.font = Font(name='Calibri', bold=bold, size=9)
            c_lbl.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                c_lbl.fill = PatternFill(fill_type='solid', fgColor=bg)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)

            _c(row, 7, note_ref or '')
            _c(row, 8, net,  halign='right')
            _c(row, 9, net1, halign='right')
            ws.row_dimensions[row].height = 14
            row += 1

    def _xl_add_resultat_ohada(self, wb, company, date_from_str, date_to_str, date_from, date_to):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='RESULTAT')

        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 58
        ws.column_dimensions['C'].width = 3
        ws.column_dimensions['D'].width = 3
        ws.column_dimensions['E'].width = 3
        ws.column_dimensions['F'].width = 5
        ws.column_dimensions['G'].width = 4
        ws.column_dimensions['H'].width = 6
        ws.column_dimensions['I'].width = 16
        ws.column_dimensions['J'].width = 16

        self._xl_ohada_header(ws, company, date_to_str,
                              'COMPTE DE RÉSULTAT\nSYSTÈME NORMAL', ncols=10)

        hdrs = [('REF',1),('LIBELLÉS',2),('A/B/C/D',6),('+/-',7),('NOTE',8),('N',9),('N-1',10)]
        for text, col in hdrs:
            c = ws.cell(row=8, column=col, value=text)
            c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells(start_row=8, start_column=2, end_row=8, end_column=5)
        ws.row_dimensions[8].height = 28

        vals_cur, vals_prev = self._fetch_report_values(
            'l10n_syscohada_reports.account_financial_report_syscohada_pl',
            date_from, date_to, company,
        )

        row = 9
        for ref, label, ab_col, sign, note_ref, is_total in _RESULTAT_LINES:
            odoo_code = _RESULTAT_CODE_MAP.get(ref, '')
            val_n  = self._xl_num((vals_cur.get(odoo_code) or {}).get('balance', 0)) if odoo_code else None
            val_n1 = self._xl_num((vals_prev.get(odoo_code) or {}).get('balance', 0)) if odoo_code else None

            bold = is_total
            bg = P['total'] if is_total else None

            def _c(r, col, val_v, halign='center'):
                c = ws.cell(row=r, column=col, value=val_v)
                c.font = Font(name='Calibri', bold=bold, size=9)
                c.alignment = Alignment(horizontal=halign, vertical='center')
                if bg:
                    c.fill = PatternFill(fill_type='solid', fgColor=bg)
                if val_v and isinstance(val_v, int):
                    c.number_format = '#,##0'
                return c

            _c(row, 1, ref or '')
            c_lbl = ws.cell(row=row, column=2, value=label)
            c_lbl.font = Font(name='Calibri', bold=bold, size=9)
            c_lbl.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                c_lbl.fill = PatternFill(fill_type='solid', fgColor=bg)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=5)

            _c(row, 6, ab_col or '')
            _c(row, 7, sign or '')
            _c(row, 8, note_ref or '')
            _c(row, 9,  val_n,  halign='right')
            _c(row, 10, val_n1, halign='right')
            ws.row_dimensions[row].height = 14
            row += 1

    def _xl_add_tft_ohada(self, wb, company, date_from_str, date_to_str, date_from, date_to):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='TFT')

        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 64
        ws.column_dimensions['C'].width = 3
        ws.column_dimensions['D'].width = 3
        ws.column_dimensions['E'].width = 3
        ws.column_dimensions['F'].width = 3
        ws.column_dimensions['G'].width = 5
        ws.column_dimensions['H'].width = 6
        ws.column_dimensions['I'].width = 16
        ws.column_dimensions['J'].width = 16

        self._xl_ohada_header(ws, company, date_to_str,
                              'TABLEAU DES FLUX\nDE TRÉSORERIE', ncols=10)

        hdrs = [('REF',1),('LIBELLÉS',2),('Lettre',7),('NOTE',8),('N',9),('N-1',10)]
        for text, col in hdrs:
            c = ws.cell(row=8, column=col, value=text)
            c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells(start_row=8, start_column=2, end_row=8, end_column=6)
        ws.row_dimensions[8].height = 28

        vals_cur, vals_prev = self._fetch_report_values(
            'l10n_ci_liasse_fiscale.l10n_ci_tft',
            date_from, date_to, company,
        )

        row = 9
        for ref, label, letter, note_ref, is_total, is_subtitle in _TFT_LINES:
            if is_subtitle:
                ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
                c = ws.cell(row=row, column=1, value=label)
                c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                c.fill = PatternFill(fill_type='solid', fgColor=P['mid'])
                c.alignment = Alignment(horizontal='left', vertical='center')
                ws.row_dimensions[row].height = 14
                row += 1
                continue

            odoo_code = f'CI_TFT_{ref}' if ref else ''
            val_n  = self._xl_num((vals_cur.get(odoo_code) or {}).get('balance', 0)) if odoo_code else None
            val_n1 = self._xl_num((vals_prev.get(odoo_code) or {}).get('balance', 0)) if odoo_code else None

            bg = P['total'] if is_total else None
            bold = is_total

            def _c(r, col, val_v, halign='center'):
                c = ws.cell(row=r, column=col, value=val_v)
                c.font = Font(name='Calibri', bold=bold, size=9)
                c.alignment = Alignment(horizontal=halign, vertical='center')
                if bg:
                    c.fill = PatternFill(fill_type='solid', fgColor=bg)
                if val_v and isinstance(val_v, int):
                    c.number_format = '#,##0'
                return c

            _c(row, 1, ref or '')
            c_lbl = ws.cell(row=row, column=2, value=label)
            c_lbl.font = Font(name='Calibri', bold=bold, size=9)
            c_lbl.alignment = Alignment(horizontal='left', vertical='center')
            if bg:
                c_lbl.fill = PatternFill(fill_type='solid', fgColor=bg)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)

            _c(row, 7, letter or '')
            _c(row, 8, note_ref or '')
            _c(row, 9,  val_n,  halign='right')
            _c(row, 10, val_n1, halign='right')
            ws.row_dimensions[row].height = 14
            row += 1

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: financial reports
    # ──────────────────────────────────────────────────────────

    def _xl_add_sheet_report(self, wb, report_xmlid, sheet_title, date_from_str, date_to_str, company):
        from openpyxl.utils import get_column_letter
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()

        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return

        options = report.get_options({
            'date': {
                'date_from': date_from_str,
                'date_to':   date_to_str,
                'mode':      'range',
                'filter':    'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })
        lines    = report._get_lines(options)
        col_defs = options.get('columns', [])
        # Add a Variation % column after the standard columns
        ncols = 2 + len(col_defs) + 1  # +1 for Variation%

        line_code_map = {
            r.id: r.code
            for r in self.env['account.report.line'].search([
                ('report_id', '=', report.id),
                ('code', '!=', False),
            ])
        }

        ws = wb.create_sheet(title=sheet_title[:31])

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 52
        for ci in range(len(col_defs)):
            ws.column_dimensions[get_column_letter(3 + ci)].width = 18
        ws.column_dimensions[get_column_letter(3 + len(col_defs))].width = 14

        # OHADA header rows 1-7
        self._xl_ohada_header(ws, company, date_to_str,
                              f'{sheet_title}\nSYSTÈME NORMAL', ncols=ncols)

        # Row 7: note full title (merged)
        ws.merge_cells(start_row=7, start_column=1, end_row=7, end_column=ncols)
        c = ws.cell(row=7, column=1, value=report.name)
        c.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        c.fill = PatternFill(fill_type='solid', fgColor=P['mid'])
        c.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[7].height = 18

        # Row 8: column headers
        self._xl_hdr(ws.cell(row=8, column=1, value='Code'), bg=P['dark'], sz=9)
        self._xl_hdr(ws.cell(row=8, column=2, value='Libellé'), bg=P['dark'], halign='left', sz=9)
        for ci, cd in enumerate(col_defs):
            self._xl_hdr(ws.cell(row=8, column=3 + ci, value=cd.get('name', '')), bg=P['dark'], sz=9)
        self._xl_hdr(ws.cell(row=8, column=3 + len(col_defs), value='Variation %'), bg=P['dark'], sz=9)
        ws.row_dimensions[8].height = 28

        row = 9
        for line in lines:
            lid   = line.get('id')
            code  = line_code_map.get(lid, '') if isinstance(lid, int) else ''
            name  = line.get('name', '')
            level = line.get('level', 2)
            cols  = line.get('columns', [])

            is_total = (level == 0)
            is_sect  = (level == 1)
            bg   = P['total'] if is_total else (P['sect'] if is_sect else None)
            bold = is_total or is_sect

            c_code = ws.cell(row=row, column=1, value=code or None)
            c_name = ws.cell(row=row, column=2, value='  ' * max(0, level - 1) + name)
            c_name.alignment = Alignment(horizontal='left', vertical='center')
            c_name.font = Font(name='Calibri', bold=bold, size=9)
            if bg:
                self._xl_hdr(c_code, bg=bg, fg='000000', bold=bold, sz=9, halign='center')
                self._xl_hdr(c_name, bg=bg, fg='000000', bold=bold, sz=9, halign='left')

            last_n, last_n1 = None, None
            for ci, col_val in enumerate(cols):
                v = self._xl_num(col_val.get('no_format'))
                c = ws.cell(row=row, column=3 + ci, value=v)
                c.alignment = Alignment(horizontal='right', vertical='center')
                c.font = Font(name='Calibri', bold=bold, size=9)
                if v is not None:
                    c.number_format = '#,##0'
                if bg:
                    self._xl_hdr(c, bg=bg, fg='000000', bold=bold, sz=9, halign='right')
                if ci == 0:
                    last_n = v
                if ci == 1:
                    last_n1 = v

            # Variation %
            var_col = 3 + len(col_defs)
            if last_n is not None and last_n1 and last_n1 != 0:
                pct = round((last_n - last_n1) / abs(last_n1) * 100, 1)
                c_var = ws.cell(row=row, column=var_col, value=pct)
                c_var.number_format = '0.0"%"'
            else:
                c_var = ws.cell(row=row, column=var_col, value=None)
            c_var.alignment = Alignment(horizontal='right', vertical='center')
            c_var.font = Font(name='Calibri', bold=bold, size=9)
            if bg:
                self._xl_hdr(c_var, bg=bg, fg='000000', bold=bold, sz=9, halign='right')

            ws.row_dimensions[row].height = 14
            row += 1

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: administrative / identification
    # ──────────────────────────────────────────────────────────

    def _xl_add_couverture(self, wb, company, date_from_str, date_to_str, liasse_type):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='COUVERTURE')

        labels = {'NO': 'SYSTÈME NORMAL', 'SI': 'SYSTÈME SIMPLIFIÉ', 'RS': 'RÉSUMÉ'}
        year = date_to_str[:4]

        rows = [
            ("REPUBLIQUE DE CÔTE D'IVOIRE",                           P['dark'], 16, True,  35),
            ("Union — Discipline — Travail",                           P['dark'], 11, False, 22),
            ("",                                                        P['mid'],  10, False, 10),
            ("MINISTERE DU BUDGET ET DU PORTEFEUILLE DE L'ETAT",      P['mid'],  12, True,  28),
            ("DIRECTION GENERALE DES IMPOTS",                          P['dark'], 14, True,  30),
            ("",                                                        P['dark'], 10, False, 10),
            ("LIASSE FISCALE DGI — CÔTE D'IVOIRE",                    P['dark'], 20, True,  45),
            (labels.get(liasse_type, liasse_type),                     P['mid'],  14, True,  32),
            (f"Exercice {year}",                                        P['mid'],  12, True,  28),
            ("",                                                        P['white'],10, False, 15),
            (f"Dénomination : {company.name}",                         P['white'],13, True,  26),
            (f"NCC : {company.vat or ''}",                             P['white'],11, False, 22),
            (f"Période : du {date_from_str} au {date_to_str}",         P['white'],11, False, 22),
            (f"Monnaie : {company.currency_id.name or 'XOF'}",         P['white'],11, False, 22),
        ]
        for i, (text, bg, sz, bold, ht) in enumerate(rows, start=1):
            ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=8)
            cell = ws.cell(row=i, column=1, value=text)
            fg = '000000' if bg == P['white'] else 'FFFFFF'
            cell.font      = Font(name='Calibri', bold=bold, size=sz, color=fg)
            cell.fill      = PatternFill(fill_type='solid', fgColor=bg)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[i].height = ht

        for ci in 'ABCDEFGH':
            ws.column_dimensions[ci].width = 15

    def _xl_add_garde(self, wb, company, date_from_str, date_to_str, sheet_title='GARDE'):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title=sheet_title[:31])

        for col, w in zip('ABCDE', [22, 22, 22, 22, 22]):
            ws.column_dimensions[col].width = w

        def hdr(r, text, bg, sz=11, bold=True, fg='FFFFFF', ncols=5):
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
            c = ws.cell(row=r, column=1, value=text)
            c.font = Font(name='Calibri', bold=bold, size=sz, color=fg)
            c.fill = PatternFill(fill_type='solid', fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')

        hdr(1,  "REPUBLIQUE DE CÔTE D'IVOIRE",                       P['dark'], sz=13)
        hdr(2,  'Union — Discipline — Travail',                       P['dark'], sz=10, bold=False)
        hdr(3,  '',                                                    P['white'])
        hdr(4,  "MINISTÈRE DU BUDGET ET DES FINANCES",                P['mid'],  sz=11)
        hdr(5,  'DIRECTION GÉNÉRALE DES IMPÔTS',                      P['dark'], sz=12)
        hdr(6,  f"CENTRE DE DÉPÔT — {(company.city or '').upper()}",  P['dark'], sz=10)
        hdr(7,  '',                                                    P['white'])
        hdr(8,  'ÉTATS FINANCIERS NORMALISÉS',                        P['dark'], sz=16)
        hdr(9,  'SYSTÈME COMPTABLE OHADA (SYSCOHADA RÉVISÉ)',          P['mid'],  sz=11)
        hdr(10, f"Exercice clos le {date_to_str}",                    P['mid'],  sz=11)
        hdr(11, '',                                                    P['white'])

        for r, h in enumerate([1,16,20,16,16,16,12,28,20,18,10], start=1):
            ws.row_dimensions[r].height = h

        # Company info block
        info = [
            ("Dénomination sociale :",  company.name or ''),
            ("N° Compte Contribuable :", company.vat or ''),
            ("Adresse :",               company.street or ''),
            ("Ville :",                 company.city or ''),
            ("Téléphone :",             company.phone or ''),
            ("Email :",                 company.email or ''),
            ("Exercice du :",           f"{date_from_str} au {date_to_str}"),
        ]
        for i, (label, val) in enumerate(info, start=12):
            ws.cell(row=i, column=1, value=label).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=1).fill = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.merge_cells(start_row=i, start_column=2, end_row=i, end_column=5)
            c = ws.cell(row=i, column=2, value=val)
            c.font = Font(name='Calibri', size=10)
            c.fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 17

        sep = 12 + len(info) + 1
        hdr(sep, 'DOCUMENTS JOINTS (cocher la case)', P['dark'], sz=11)
        ws.row_dimensions[sep].height = 22

        docs = [
            "☐  Bilan Actif",
            "☐  Bilan Passif",
            "☐  Compte de Résultat",
            "☐  Tableau des Flux de Trésorerie (TFT)",
            "☐  Notes annexes 1 à 39",
            "☐  Tableau des amortissements (SUPPL4)",
            "☐  État complémentaire des charges (COMP-CHARGES)",
            "☐  État de la TVA (COMP-TVA)",
            "☐  Rapport du commissaire aux comptes",
        ]
        for j, doc in enumerate(docs, start=sep + 1):
            ws.cell(row=j, column=1, value=doc).font = Font(name='Calibri', size=10)
            ws.row_dimensions[j].height = 16

    def _xl_add_recevabilite(self, wb):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='RECEVABILITE')
        ws.column_dimensions['A'].width = 100

        def hdr(r, text, bg, sz=11, bold=True):
            c = ws.cell(row=r, column=1, value=text)
            c.font = Font(name='Calibri', bold=bold, size=sz, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=bg)
            c.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[r].height = 24

        hdr(1, "CONDITIONS DE RECEVABILITÉ DE LA LIASSE FISCALE — SYSTÈME OHADA (SYSCOHADA)", P['dark'], sz=12)

        lines = [
            ('', None),
            ("I. ÉTATS FINANCIERS PRÉSENTÉS SUR SUPPORT PAPIER", P['mid']),
            ('', None),
            ("Les états financiers sont recevables si :", None),
            ("  1.  Ils sont établis en langue française.", None),
            ("  2.  Ils sont présentés sur des formulaires conformes aux modèles OHADA.", None),
            ("  3.  Toutes les rubriques sont renseignées (aucune page blanche).", None),
            ("  4.  Ils sont signés et datés par le représentant légal et le comptable.", None),
            ("  5.  Le cachet de l'entreprise est apposé sur chaque page.", None),
            ("  6.  Le bilan est équilibré : Total Actif = Total Passif.", None),
            ("  7.  Le résultat du bilan correspond au résultat du Compte de Résultat.", None),
            ("  8.  Toutes les notes annexes obligatoires (1 à 39) sont jointes.", None),
            ("  9.  Le dépôt est effectué dans les délais légaux (avant le 30 avril N+1).", None),
            ('', None),
            ("II. ÉTATS FINANCIERS PRÉSENTÉS SUR SUPPORT INFORMATIQUE", P['mid']),
            ('', None),
            ("En plus des conditions du §I, les états sur support informatique doivent :", None),
            ("  1.  Être produits via le portail e-impôts DGI Côte d'Ivoire.", None),
            ("  2.  Contenir un fichier XML conforme au schéma DGI CI.", None),
            ("  3.  Inclure le N° de Télédéclarant (NTD) valide.", None),
            ("  4.  Être soumis avant la date limite de télédéclaration.", None),
            ("  5.  Faire l'objet d'un accusé de réception électronique DGI.", None),
            ('', None),
            ("Références :", None),
            ("  •  Acte Uniforme OHADA sur le Droit Comptable et l'Information Financière (AUDCIF)", None),
            ("  •  SYSCOHADA Révisé — Référentiel comptable 2017", None),
            ("  •  Code Général des Impôts de Côte d'Ivoire", None),
            ("  •  Circulaire DGI CI relative aux obligations déclaratives", None),
        ]
        for i, item in enumerate(lines, start=2):
            text, bg = item if isinstance(item, tuple) else (item, None)
            c = ws.cell(row=i, column=1, value=text)
            c.font = Font(name='Calibri', bold=(bg is not None), size=10,
                          color='FFFFFF' if bg else '000000')
            if bg:
                c.fill = PatternFill(fill_type='solid', fgColor=bg)
            ws.row_dimensions[i].height = 15

    def _xl_add_fiche_r1(self, wb, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R1')

        for col, w in zip('ABCDE', [6, 46, 3, 3, 40]):
            ws.column_dimensions[col].width = w

        ws.merge_cells('A1:E1')
        ws.cell(row=1, column=1, value="FICHE R1 — RENSEIGNEMENTS SUR L'ENTREPRISE")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        def row_field(r, code, label, value=''):
            ws.cell(row=r, column=1, value=code).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=r, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=r, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
            ws.cell(row=r, column=2, value=label).font = Font(name='Calibri', bold=True, size=9)
            ws.cell(row=r, column=2).fill = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=r, column=5, value=value).font = Font(name='Calibri', size=9)
            ws.cell(row=r, column=5).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 16

        fields_r1 = [
            ('ZA',  "EXERCICE COMPTABLE DU … AU",                    f"{date_from_str} / {date_to_str}"),
            ('ZB',  "DATE D'ARRÊTÉ EFFECTIF DES COMPTES",             ''),
            ('ZC',  "EXERCICE PRÉCÉDENT CLOS LE",                     ''),
            ('ZD',  "N° AU REGISTRE DU COMMERCE (RCCM)",              ''),
            ('ZE',  "GREFFE / LIEU D'IMMATRICULATION",                 ''),
            ('ZF',  "N° AU RÉPERTOIRE DES ENTREPRISES (REE)",         ''),
            ('ZG',  "N° CAISSE SOCIALE / NUMÉRO DE COTISANT",         ''),
            ('ZH',  "CODE IMPORTATEUR",                               ''),
            ('ZI',  "CODE D'ACTIVITÉ PRINCIPALE (CIAP)",              ''),
            ('ZJ',  "DÉSIGNATION DE L'ENTITÉ / SIGLE USUEL",          f"{company.name or ''} / "),
            ('ZK',  "ADRESSE POSTALE (Tél / Email / BP / Ville)",     f"{company.phone or ''} / {company.email or ''} / {company.zip or ''} / {company.city or ''}"),
            ('ZL',  "ADRESSE GÉOGRAPHIQUE",                           company.street or ''),
            ('ZM',  "ACTIVITÉ PRINCIPALE",                            ''),
            ('ZN',  "% CAPACITÉ DE PRODUCTION UTILISÉE",              ''),
            ('ZO',  "CONTACT : Nom, Prénom, Titre, Tél",              ''),
            ('ZP',  "EMAIL DU CONTACT",                               ''),
            ('ZQ',  "EXPERT-COMPTABLE (Nom & N° Agrément)",           ''),
            ('ZR',  "COMMISSAIRE AUX COMPTES (Nom & N° Agrément)",    ''),
            ('ZS',  "NOM DU SIGNATAIRE",                              ''),
            ('ZT',  "QUALITÉ DU SIGNATAIRE",                          ''),
            ('ZU',  "DATE DE SIGNATURE",                              ''),
            ('ZV',  "LIEU DE SIGNATURE",                              ''),
            ('ZW',  "DATE AG / DOMICILIATIONS BANCAIRES",             ''),
        ]
        for i, (code, label, value) in enumerate(fields_r1, start=3):
            row_field(i, code, label, value)

    def _xl_add_fiche_r2(self, wb, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R2')

        for col, w in zip('ABCDE', [6, 50, 3, 3, 34]):
            ws.column_dimensions[col].width = w

        ws.merge_cells('A1:E1')
        ws.cell(row=1, column=1, value="FICHE R2 — FORME JURIDIQUE, RÉGIME FISCAL ET ACTIVITÉ")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        def row_field(r, code, label, value=''):
            ws.cell(row=r, column=1, value=code).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=r, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=r, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
            ws.cell(row=r, column=2, value=label).font = Font(name='Calibri', bold=True, size=9)
            ws.cell(row=r, column=2).fill = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=r, column=5, value=value).font = Font(name='Calibri', size=9)
            ws.cell(row=r, column=5).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 16

        rows_r2 = [
            ('ZX',  "FORME JURIDIQUE (code — voir TABLE DES CODES)",          ''),
            ('ZY',  "RÉGIME FISCAL (code — voir TABLE DES CODES)",             ''),
            ('ZZ1', "PAYS DU SIÈGE SOCIAL",                                    "Côte d'Ivoire"),
            ('ZZ2', "NOMBRE D'ÉTABLISSEMENTS DANS LE PAYS",                    ''),
            ('ZZ3', "NOMBRE D'ÉTABLISSEMENTS HORS DU PAYS",                    ''),
            ('ZZ4', "PREMIÈRE ANNÉE D'EXERCICE DANS LE PAYS",                  ''),
        ]
        for i, (code, label, value) in enumerate(rows_r2, start=3):
            row_field(i, code, label, value)

        # Activity table header
        act_hdr_row = 3 + len(rows_r2) + 1
        ws.merge_cells(start_row=act_hdr_row, start_column=1, end_row=act_hdr_row, end_column=5)
        c = ws.cell(row=act_hdr_row, column=1, value="TABLEAU DES ACTIVITÉS (CODE CIAP + CHIFFRE D'AFFAIRES HT)")
        c.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
        c.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[act_hdr_row].height = 20

        hdrs = ['Code CIAP', "Désignation de l'activité", '', '', 'CA HT exercice N']
        for ci, h in enumerate(hdrs, start=1):
            ws.cell(row=act_hdr_row + 1, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=act_hdr_row + 1, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.merge_cells(start_row=act_hdr_row + 1, start_column=2,
                       end_row=act_hdr_row + 1, end_column=4)
        ws.row_dimensions[act_hdr_row + 1].height = 18

        for r in range(act_hdr_row + 2, act_hdr_row + 8):
            for ci in range(1, 6):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 16

    def _xl_add_fiche_r3(self, wb, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R3')

        col_widths = [30, 20, 18, 20, 24, 30]
        for ci, w in enumerate(col_widths, start=1):
            ws.column_dimensions[get_column_letter(ci)].width = w

        ws.merge_cells(f'A1:{get_column_letter(len(col_widths))}1')
        ws.cell(row=1, column=1, value="FICHE R3 — DIRIGEANTS ET CONSEIL D'ADMINISTRATION")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        # Section 1: Dirigeants
        ws.merge_cells('A3:F3')
        ws.cell(row=3, column=1, value="SECTION 1 — DIRIGEANTS").font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        ws.cell(row=3, column=1).fill = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=3, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 18

        hdrs1 = ['Nom et Prénoms', 'Nationalité', 'Autres nationalités', 'Qualité', 'N° identification fiscale', 'Adresse']
        for ci, h in enumerate(hdrs1, start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['mid'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.row_dimensions[4].height = 22
        for r in range(5, 12):
            for ci in range(1, 7):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 18

        # Section 2: Conseil d'administration
        ws.merge_cells('A13:F13')
        ws.cell(row=13, column=1, value="SECTION 2 — MEMBRES DU CONSEIL D'ADMINISTRATION").font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
        ws.cell(row=13, column=1).fill = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=13, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[13].height = 18

        hdrs2 = ['Nom et Prénoms', 'Structure représentée', '', 'Qualité', '', 'Adresse']
        for ci, h in enumerate(hdrs2, start=1):
            ws.cell(row=14, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=14, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['mid'])
            ws.cell(row=14, column=ci).alignment      = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.merge_cells('B14:C14')
        ws.merge_cells('D14:E14')
        ws.row_dimensions[14].height = 22
        for r in range(15, 24):
            for ci in range(1, 7):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 18

    def _xl_add_fiche_r4(self, wb):
        """FICHE RÉCAPITULATIVE DES NOTES ANNEXES PRÉSENTÉES."""
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='FICHE R4')

        ws.column_dimensions['A'].width = 14
        ws.column_dimensions['B'].width = 62
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 16

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value="FICHE RÉCAPITULATIVE DES NOTES ANNEXES PRÉSENTÉES")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        hdrs = ['NOTES', 'INTITULÉS', 'A (Annexée)', 'N/A (Non Applicable)']
        for ci, h in enumerate(hdrs, start=1):
            ws.cell(row=3, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=3, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=3, column=ci).alignment      = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.row_dimensions[3].height = 22

        for i, (note_ref, title) in enumerate(_FICHE_R4_NOTES, start=4):
            ws.cell(row=i, column=1, value=note_ref).font = Font(name='Calibri', bold=True, size=9)
            ws.cell(row=i, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=2, value=title).font = Font(name='Calibri', size=9)
            ws.cell(row=i, column=2).alignment = Alignment(horizontal='left', vertical='center')
            # Checkbox cells
            ws.cell(row=i, column=3, value='☐').alignment = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=4, value='☐').alignment = Alignment(horizontal='center', vertical='center')
            for ci in range(1, 5):
                fill_c = P['sect'] if i % 2 == 0 else P['white']
                ws.cell(row=i, column=ci).fill = PatternFill(fill_type='solid', fgColor=fill_c)
            ws.row_dimensions[i].height = 14

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: Note 36 reference tables
    # ──────────────────────────────────────────────────────────

    def _xl_add_note36_codes(self, wb):
        """TABLE DES CODES — Formes juridiques et régimes fiscaux CI."""
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='TABLE DES CODES')

        ws.column_dimensions['A'].width = 10
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 50

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value="NOTE 36 — TABLE DES CODES (FORMES JURIDIQUES & RÉGIMES FISCAUX)")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        # Formes juridiques
        ws.merge_cells('A3:B3')
        ws.cell(row=3, column=1, value="FORMES JURIDIQUES").font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        ws.cell(row=3, column=1).fill = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.row_dimensions[3].height = 20

        formes = [
            ('SA',   "Société Anonyme"),
            ('SARL', "Société à Responsabilité Limitée"),
            ('SNC',  "Société en Nom Collectif"),
            ('SCS',  "Société en Commandite Simple"),
            ('SCA',  "Société en Commandite par Actions"),
            ('GIE',  "Groupement d'Intérêt Économique"),
            ('SAS',  "Société par Actions Simplifiée"),
            ('COOP', "Coopérative"),
            ('ASS',  "Association"),
            ('EI',   "Entreprise Individuelle"),
            ('ETAB', "Établissement"),
            ('SUC',  "Succursale de société étrangère"),
            ('ORG',  "Organisme public ou semi-public"),
        ]
        for i, (code, label) in enumerate(formes, start=4):
            ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', size=10)
            ws.row_dimensions[i].height = 16

        # Régimes fiscaux
        ws.merge_cells('C3:D3')
        ws.cell(row=3, column=3, value="RÉGIMES FISCAUX").font = Font(name='Calibri', bold=True, size=11, color='FFFFFF')
        ws.cell(row=3, column=3).fill = PatternFill(fill_type='solid', fgColor=P['mid'])

        regimes = [
            ('BIC',  "Bénéfices Industriels et Commerciaux"),
            ('BNC',  "Bénéfices Non Commerciaux"),
            ('BA',   "Bénéfices Agricoles"),
            ('RSI',  "Régime Synthétique d'Imposition"),
            ('RNI',  "Régime du Réel Normal d'Imposition"),
            ('RSI',  "Régime Simplifié d'Imposition"),
            ('IS',   "Impôt sur les Sociétés"),
            ('IR',   "Impôt sur le Revenu"),
            ('IMF',  "Impôt Minimum Forfaitaire"),
            ('TVA',  "Assujetti à la TVA"),
            ('EXON', "Exonéré"),
        ]
        for i, (code, label) in enumerate(regimes, start=4):
            ws.cell(row=i, column=3, value=code).font = Font(name='Calibri', bold=True, size=10)
            ws.cell(row=i, column=3).fill              = PatternFill(fill_type='solid', fgColor=P['sect'])
            ws.cell(row=i, column=4, value=label).font = Font(name='Calibri', size=10)

    def _xl_add_note36_ciap(self, wb):
        """NOTE 36 Suite — Nomenclature CIAP (Classification des Activités)."""
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='Nomenclature CIAP')

        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 72

        ws.merge_cells('A1:B1')
        ws.cell(row=1, column=1,
                value="NOTE 36 Suite — NOMENCLATURE CIAP (Classification Ivoirienne des Activités et Produits)")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        sectors = [
            ('A', "Agriculture, sylviculture et pêche"),
            ('B', "Industries extractives"),
            ('C', "Industries manufacturières"),
            ('D', "Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné"),
            ('E', "Production et distribution d'eau ; assainissement, gestion des déchets et dépollution"),
            ('F', "Construction"),
            ('G', "Commerce de gros et de détail ; réparation de véhicules automobiles"),
            ('H', "Transports et entreposage"),
            ('I', "Hébergement et restauration"),
            ('J', "Information et communication"),
            ('K', "Activités financières et d'assurance"),
            ('L', "Activités immobilières"),
            ('M', "Activités spécialisées, scientifiques et techniques"),
            ('N', "Activités de services administratifs et de soutien"),
            ('O', "Administration publique"),
            ('P', "Enseignement"),
            ('Q', "Santé humaine et action sociale"),
            ('R', "Arts, spectacles et activités récréatives"),
            ('S', "Autres activités de services"),
            ('T', "Activités des ménages en tant qu'employeurs"),
            ('U', "Activités extraterritoriales"),
        ]
        for i, (code, label) in enumerate(sectors, start=3):
            ws.cell(row=i, column=1, value=code).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=i, column=1).alignment         = Alignment(horizontal='center', vertical='center')
            ws.cell(row=i, column=2, value=label).font = Font(name='Calibri', size=10)
            ws.row_dimensions[i].height = 16

    # ──────────────────────────────────────────────────────────
    #  Sheet generator: generic placeholder note
    # ──────────────────────────────────────────────────────────

    def _xl_add_note_placeholder(self, wb, sheet_title, note_ref, description,
                                fields_list=None, company=None, date_to_str=''):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title=sheet_title[:31])

        ws.column_dimensions['A'].width = 52
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20

        if company and date_to_str:
            self._xl_ohada_header(ws, company, date_to_str,
                                  f'NOTE {note_ref}\nSYSTÈME NORMAL', ncols=3)
            # Row 7: note title
            ws.merge_cells('A7:C7')
            c = ws.cell(row=7, column=1, value=f"NOTE {note_ref} — {description.upper()}")
            c.font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            c.fill = PatternFill(fill_type='solid', fgColor=P['mid'])
            c.alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[7].height = 18
            data_start = 9
        else:
            ws.merge_cells('A1:C1')
            ws.cell(row=1, column=1, value=f"NOTE {note_ref} — {description.upper()}")
            ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
            ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
            ws.row_dimensions[1].height = 26
            data_start = 3

        if not fields_list:
            ws.cell(row=data_start, column=1, value="[À compléter manuellement]")
            ws.cell(row=data_start, column=1).font = Font(name='Calibri', size=9, color='808080', italic=True)
            return

        hdr_row = data_start - 1
        for ci, h in enumerate(['Description / Libellé', 'Exercice N', 'Exercice N-1'], start=1):
            ws.cell(row=hdr_row, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=hdr_row, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=hdr_row, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[hdr_row].height = 22

        for i, (label, is_header) in enumerate(fields_list, start=data_start):
            bg = P['sect'] if is_header else P['fill']
            ws.cell(row=i, column=1, value=label).font = Font(name='Calibri', bold=is_header, size=9)
            ws.cell(row=i, column=1).fill              = PatternFill(fill_type='solid', fgColor=bg)
            if is_header:
                ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=3)
            else:
                ws.cell(row=i, column=2).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
                ws.cell(row=i, column=3).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[i].height = 15

    # ──────────────────────────────────────────────────────────
    #  Sheet generators: DGI supplements
    # ──────────────────────────────────────────────────────────

    def _xl_add_comp_charges(self, wb, date_from, date_to, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        from odoo import fields as ofields
        P = self._xl_palette()
        ws = wb.create_sheet(title='COMP-CHARGES')

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 52
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 18
        ws.column_dimensions['E'].width = 16
        ws.column_dimensions['F'].width = 12

        ws.merge_cells('A1:F1')
        ws.cell(row=1, column=1, value="ÉTAT COMPLÉMENTAIRE N°1 — DÉTAIL DES CHARGES PAR NATURE")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells('A2:F2')
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        hdrs = ['Code cpte', 'Désignation', 'N', 'N-1', 'Variation', 'Var %']
        for ci, h in enumerate(hdrs, start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 20

        # Alias groups: prefix patterns → (alias, label)
        _ALIAS_GROUPS = [
            (['601', '6011', '6012', '6013', '6014', '6015', '6016', '6017', '6018', '6019'], 'RA', 'Achats de marchandises'),
            (['6031'],                                                                          'RB', 'Variation de stocks de marchandises'),
            (['602', '6021', '6022', '6023', '6024', '6025', '6026', '6028', '6029'],          'RC', 'Achats de matières premières'),
            (['6032'],                                                                          'RD', 'Variation de stocks de matières premières'),
            (['604', '605', '606', '608', '6041', '6042', '6043', '6044', '6045', '6046',
              '6047', '6048', '6051', '6052', '6053', '6054', '6055', '6056', '6057', '6058',
              '6061', '6062', '6063', '6064', '6065', '6066', '6068', '6081', '6082', '6083',
              '6084', '6085', '6086', '6088'],                                                 'RE', 'Autres achats'),
            (['6033'],                                                                          'RF', "Variation de stocks d'autres approvisionnements"),
            (['61'],                                                                            'RG', 'Transports'),
            (['62', '63'],                                                                      'RH', 'Services extérieurs'),
            (['64'],                                                                            'RI', 'Impôts et taxes'),
            (['65'],                                                                            'RJ', 'Autres charges'),
            (['66'],                                                                            'RK', 'Charges de personnel'),
            (['681', '686', '691', '694', '696', '698'],                                       'RL', 'Dotations aux amortissements et provisions'),
            (['67'],                                                                            'RM', 'Frais financiers'),
            (['697'],                                                                           'RN', 'Dotations prov. financières'),
            (['81'],                                                                            'RO', "Val. comptables cessions d'immo."),
            (['83'],                                                                            'RP', 'Autres charges HAO'),
            (['87'],                                                                            'RQ', 'Participation des travailleurs'),
            (['89'],                                                                            'RS', 'Impôts sur le résultat'),
        ]

        try:
            from dateutil.relativedelta import relativedelta
            prev_from = date_from - relativedelta(years=1)
            prev_to   = date_to   - relativedelta(years=1)

            def _query(d_from, d_to):
                return self.env['account.move.line'].read_group(
                    domain=[
                        ('account_id.code', 'like', '6%'),
                        ('company_id', '=', company.id),
                        ('date', '>=', ofields.Date.to_string(d_from)),
                        ('date', '<=', ofields.Date.to_string(d_to)),
                        ('move_id.state', '=', 'posted'),
                    ],
                    fields=['account_id', 'balance:sum'],
                    groupby=['account_id'],
                    orderby='account_id',
                )

            groups      = _query(date_from, date_to)
            groups_prev = _query(prev_from, prev_to)

            # Build lookup: acc_code → (label, bal_n, bal_n1)
            by_code_n  = {}
            by_code_n1 = {}
            for g in groups:
                raw = g['account_id'][1] or ''
                parts = raw.split(' ', 1)
                acc_code = parts[0]
                acc_lbl  = parts[1] if len(parts) > 1 else raw
                by_code_n[acc_code] = (acc_lbl, g.get('balance', 0) or 0)
            for g in groups_prev:
                raw = g['account_id'][1] or ''
                parts = raw.split(' ', 1)
                acc_code = parts[0]
                acc_lbl  = parts[1] if len(parts) > 1 else raw
                by_code_n1[acc_code] = (acc_lbl, g.get('balance', 0) or 0)

            all_codes = sorted(set(list(by_code_n.keys()) + list(by_code_n1.keys())))

            # Map each code to an alias group
            def _alias_for(code):
                for prefixes, alias, lbl in _ALIAS_GROUPS:
                    for pfx in prefixes:
                        if code.startswith(pfx):
                            return alias, lbl
                return None, None

            # Group codes by alias
            from collections import defaultdict
            alias_codes = defaultdict(list)
            for code in all_codes:
                alias, _ = _alias_for(code)
                alias_codes[alias].append(code)

            row = 5
            written_aliases = set()
            # Write alias groups in order
            for prefixes, alias, alias_lbl in _ALIAS_GROUPS:
                codes = alias_codes.get(alias, [])
                if not codes:
                    continue
                if alias not in written_aliases:
                    written_aliases.add(alias)

                sub_n, sub_n1 = 0, 0
                for code in sorted(codes):
                    lbl_n,  bal_n  = by_code_n.get(code,  (code, 0))
                    lbl_n1, bal_n1 = by_code_n1.get(code, (code, 0))
                    lbl = lbl_n or lbl_n1
                    val_n  = int(round(-bal_n))  if bal_n  else None
                    val_n1 = int(round(-bal_n1)) if bal_n1 else None
                    sub_n  += (-bal_n  if bal_n  else 0)
                    sub_n1 += (-bal_n1 if bal_n1 else 0)

                    ws.cell(row=row, column=1, value=code).font = Font(name='Calibri', size=9)
                    ws.cell(row=row, column=2, value=lbl).font  = Font(name='Calibri', size=9)
                    for ci, v in [(3, val_n), (4, val_n1)]:
                        c = ws.cell(row=row, column=ci, value=v)
                        c.alignment = Alignment(horizontal='right', vertical='center')
                        c.font = Font(name='Calibri', size=9)
                        if v is not None:
                            c.number_format = '#,##0'
                    ws.row_dimensions[row].height = 14
                    row += 1

                # Subtotal row for alias
                var_val = int(round(sub_n - sub_n1)) if sub_n or sub_n1 else None
                pct = round((sub_n - sub_n1) / abs(sub_n1) * 100, 1) if sub_n1 else None

                ws.cell(row=row, column=1, value=alias).font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                ws.cell(row=row, column=1).fill = PatternFill(fill_type='solid', fgColor=P['dark'])
                ws.cell(row=row, column=2, value=f"TOTAL {alias} — {alias_lbl}").font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                ws.cell(row=row, column=2).fill = PatternFill(fill_type='solid', fgColor=P['dark'])
                for ci, v in [(3, int(round(sub_n)) if sub_n else None),
                              (4, int(round(sub_n1)) if sub_n1 else None),
                              (5, var_val)]:
                    c = ws.cell(row=row, column=ci, value=v)
                    c.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                    c.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    if v is not None:
                        c.number_format = '#,##0'
                c_pct = ws.cell(row=row, column=6, value=pct)
                c_pct.font = Font(name='Calibri', bold=True, size=9, color='FFFFFF')
                c_pct.fill = PatternFill(fill_type='solid', fgColor=P['dark'])
                c_pct.alignment = Alignment(horizontal='right', vertical='center')
                if pct is not None:
                    c_pct.number_format = '0.0"%"'
                ws.row_dimensions[row].height = 16
                row += 1

        except Exception:
            ws.cell(row=5, column=1, value="[Données non disponibles]")
            ws.cell(row=5, column=1).font = Font(name='Calibri', size=9, color='808080', italic=True)

    def _xl_add_comp_tva(self, wb, sheet_num, date_from, date_to, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        from odoo import fields as ofields
        P = self._xl_palette()

        title_map = {
            1: ('COMP-TVA',    "COMPLÉMENT TVA — TVA COLLECTÉE ET DÉDUCTIBLE"),
            2: ('COMP-TVA (2)',"COMPLÉMENT TVA (2) — TVA SUPPORTÉE NON DÉDUCTIBLE"),
        }
        sheet_name, heading = title_map.get(sheet_num, (f'COMP-TVA ({sheet_num})', 'TVA'))
        ws = wb.create_sheet(title=sheet_name[:31])

        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 48
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20

        ws.merge_cells('A1:D1')
        ws.cell(row=1, column=1, value=heading)
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells('A2:D2')
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        for ci, h in enumerate(['N° Compte', 'Intitulé', 'Base HT', 'Montant TVA'], start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 22

        prefixes = ['4457', '4456'] if sheet_num == 1 else ['4458']
        try:
            row = 5
            for pfx in prefixes:
                groups = self.env['account.move.line'].read_group(
                    domain=[
                        ('account_id.code', 'like', f'{pfx}%'),
                        ('company_id', '=', company.id),
                        ('date', '>=', ofields.Date.to_string(date_from)),
                        ('date', '<=', ofields.Date.to_string(date_to)),
                        ('move_id.state', '=', 'posted'),
                    ],
                    fields=['account_id', 'balance:sum'],
                    groupby=['account_id'],
                    orderby='account_id',
                )
                for g in groups:
                    acc_name = g['account_id'][1] or ''
                    parts    = acc_name.split(' ', 1)
                    acc_code = parts[0]
                    acc_lbl  = parts[1] if len(parts) > 1 else acc_name
                    bal      = g.get('balance', 0) or 0
                    val = int(round(abs(bal))) if bal != 0 else None
                    ws.cell(row=row, column=1, value=acc_code)
                    ws.cell(row=row, column=2, value=acc_lbl)
                    c = ws.cell(row=row, column=4, value=val)
                    c.alignment = Alignment(horizontal='right', vertical='center')
                    if val:
                        c.number_format = '#,##0'
                    row += 1
        except Exception:
            ws.cell(row=5, column=1, value="[Données non disponibles]")
            ws.cell(row=5, column=1).font = Font(name='Calibri', size=10, color='808080', italic=True)

    def _xl_add_suppl(self, wb, n, date_from_str, date_to_str, company):
        from openpyxl.styles import Font, PatternFill, Alignment
        from openpyxl.utils import get_column_letter
        P = self._xl_palette()

        configs = {
            1: ("SUPPL1 — COMPLÉMENTS NOTES 32, 27B, 33 ET BIENS D'OCCASION",
                ['Description', 'Montant N', 'Montant N-1']),
            2: ("SUPPL2 — RÉPARTITION RÉSULTAT FISCAL — SOCIÉTÉS DE PERSONNES",
                ['Associé / Actionnaire', 'Part (%)', 'Quote-part bénéfice', 'Quote-part déficit']),
            3: ("SUPPL3 — INFORMATIONS ENTITÉS INDIVIDUELLES",
                ['Rubrique', 'Valeur N', 'Valeur N-1']),
            4: ("SUPPL4 — TABLEAU DES AMORTISSEMENTS — INVENTAIRE IMMOBILISATIONS",
                ['N° immo', 'Désignation', 'Date acquis.', 'Valeur brute', 'Taux (%)',
                 'Dot. exercice', 'Amort. cumulé', 'Valeur nette']),
            5: ("SUPPL5 — FRAIS ACCESSOIRES SUR ACHATS",
                ['Fournisseur', 'Nature des frais', 'Montant HT', 'TVA récupérable']),
            6: ("SUPPL6 — AVANTAGES EN NATURE ET EN ESPÈCES",
                ['Bénéficiaire', 'Qualité', 'Nature de l\'avantage', 'Valeur N', 'Valeur N-1']),
            7: ("SUPPL7 — CRÉANCES ET DETTES ÉCHUES DE L'EXERCICE",
                ['Compte', 'Libellé', 'Montant échu N', 'Dont contentieux N']),
        }
        heading, cols = configs.get(n, (f'SUPPL{n}', ['Description', 'Montant']))
        ncols = len(cols)

        ws = wb.create_sheet(title=f'SUPPL{n}')

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
        ws.cell(row=1, column=1, value=heading)
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
        ws.cell(row=2, column=1,
                value=f"Exercice du {date_from_str} au {date_to_str} — {company.name}")
        ws.cell(row=2, column=1).font      = Font(name='Calibri', size=10, color='FFFFFF')
        ws.cell(row=2, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['mid'])
        ws.cell(row=2, column=1).alignment = Alignment(horizontal='center', vertical='center')

        for ci, h in enumerate(cols, start=1):
            ws.cell(row=4, column=ci, value=h).font = Font(name='Calibri', bold=True, size=10, color='FFFFFF')
            ws.cell(row=4, column=ci).fill           = PatternFill(fill_type='solid', fgColor=P['dark'])
            ws.cell(row=4, column=ci).alignment      = Alignment(horizontal='center', vertical='center')
            ws.column_dimensions[get_column_letter(ci)].width = max(16, len(h) + 3)
        ws.row_dimensions[4].height = 22

        for r in range(5, 22):
            for ci in range(1, ncols + 1):
                ws.cell(row=r, column=ci).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 17

    def _xl_add_commentaire(self, wb, company, date_from_str, date_to_str):
        from openpyxl.styles import Font, PatternFill, Alignment
        P = self._xl_palette()
        ws = wb.create_sheet(title='COMMENTAIRE')
        ws.column_dimensions['A'].width = 100

        ws.cell(row=1, column=1,
                value=f"COMMENTAIRES LIBRES — {company.name} — Exercice du {date_from_str} au {date_to_str}")
        ws.cell(row=1, column=1).font      = Font(name='Calibri', bold=True, size=12, color='FFFFFF')
        ws.cell(row=1, column=1).fill      = PatternFill(fill_type='solid', fgColor=P['dark'])
        ws.cell(row=1, column=1).alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 26

        ws.cell(row=3, column=1,
                value="[Espace réservé aux commentaires, observations et informations complémentaires]")
        ws.cell(row=3, column=1).font = Font(name='Calibri', size=11, color='808080', italic=True)
        ws.row_dimensions[3].height = 20

        for r in range(4, 35):
            ws.cell(row=r, column=1).fill = PatternFill(fill_type='solid', fgColor=P['fill'])
            ws.row_dimensions[r].height = 18

    # ──────────────────────────────────────────────────────────
    #  Main Excel generation
    # ──────────────────────────────────────────────────────────

    def generate_excel(self, date_from, date_to, company, liasse_type='NO'):
        try:
            import openpyxl
        except ImportError:
            from odoo.exceptions import UserError
            raise UserError("openpyxl est requis pour l'export Excel. Installez-le via pip.")

        from io import BytesIO

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        dfstr = fields.Date.to_string(date_from)
        dtstr = fields.Date.to_string(date_to)

        def safe(fn, *args, **kw):
            try:
                fn(*args, **kw)
            except Exception:
                pass

        # ── Bloc 1 : pages administratives ──────────────────────────
        safe(self._xl_add_couverture,     wb, company, dfstr, dtstr, liasse_type)
        safe(self._xl_add_garde,          wb, company, dfstr, dtstr, 'GARDE')
        safe(self._xl_add_recevabilite,   wb)
        safe(self._xl_add_note36_codes,   wb)
        safe(self._xl_add_note36_ciap,    wb)

        # ── Bloc 2 : fiches d'identification ────────────────────────
        safe(self._xl_add_fiche_r1, wb, company, dfstr, dtstr)
        safe(self._xl_add_fiche_r2, wb, company)
        safe(self._xl_add_fiche_r3, wb, company)
        safe(self._xl_add_fiche_r4, wb)

        # ── Bloc 3 : états financiers OHADA ──────────────────────────
        safe(self._xl_add_actif_ohada,    wb, company, dfstr, dtstr, date_from, date_to)
        safe(self._xl_add_passif_ohada,   wb, company, dfstr, dtstr, date_from, date_to)
        safe(self._xl_add_resultat_ohada, wb, company, dfstr, dtstr, date_from, date_to)
        safe(self._xl_add_tft_ohada,      wb, company, dfstr, dtstr, date_from, date_to)

        def note_ph(sheet_title, note_ref, description, fields_list=None):
            safe(self._xl_add_note_placeholder, wb, sheet_title, note_ref, description,
                 fields_list, company, dtstr)

        # ── Bloc 4 : notes 1–39 ─────────────────────────────────────
        note_ph('NOTE 1', '1', "DETTES GARANTIES ET ENGAGEMENTS FINANCIERS",
             [
                 ("NOTE 1A — Dettes garanties par des sûretés réelles", True),
                 ("Emprunts et dettes financières garantis (16x)",       False),
                 ("Dettes fournisseurs garanties (40x)",                 False),
                 ("Autres dettes garanties",                             False),
                 ("TOTAL dettes garanties",                              False),
                 ("NOTE 1B — Engagements financiers hors bilan",         True),
                 ("Cautions, avals et garanties donnés",                 False),
                 ("Engagements reçus",                                   False),
                 ("Crédits-bails et locations financières",              False),
                 ("Autres engagements hors bilan",                       False),
             ])
        note_ph('NOTE 2', '2', "MÉTHODES ET PRINCIPES COMPTABLES",
             [
                 ("Méthode de valorisation des stocks",                  False),
                 ("Méthode d'amortissement principal",                   False),
                 ("Méthode de conversion des opérations en devises",     False),
                 ("Méthode d'évaluation des provisions",                 False),
                 ("CHANGEMENTS DE MÉTHODES",                             True),
                 ("Description du changement",                           False),
                 ("Justification du changement",                         False),
                 ("Impact quantifié sur le résultat (FCFA)",             False),
             ])

        for xmlid, title in [
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3a',   'NOTE 3A'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3b',   'NOTE 3B'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3c',   'NOTE 3C'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3cbis','NOTE 3C BIS'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3d',   'NOTE 3D'),
            ('l10n_ci_liasse_fiscale.l10n_ci_note_3e',   'NOTE 3E'),
        ]:
            safe(self._xl_add_sheet_report, wb, xmlid, title, dfstr, dtstr, company)

        safe(self._xl_add_sheet_report, wb,
             'l10n_ci_liasse_fiscale.l10n_ci_note_4', 'NOTE 4', dfstr, dtstr, company)

        for n in range(5, 9):
            safe(self._xl_add_sheet_report, wb,
                 f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}', f'NOTE {n}', dfstr, dtstr, company)

        note_ph('NOTE 8A', '8A', "CHARGES IMMOBILISÉES",
             [("Valeur brute en début d'exercice (481)", False),
              ("Charges immobilisées de l'exercice",     False),
              ("Amortissements de l'exercice",            False),
              ("Valeur nette en fin d'exercice",         False)])
        note_ph('NOTE 8B', '8B', "PROVISIONS POUR CHARGES À RÉPARTIR",
             [("Provisions constituées (191–199)",       False),
              ("Reprises de l'exercice",                 False),
              ("Solde en fin d'exercice",                False)])
        note_ph('NOTE 8C', '8C', "PROVISIONS POUR ENGAGEMENTS DE RETRAITE",
             [("Effectif concerné",                      False),
              ("Provision constituée (196)",             False),
              ("Méthode actuarielle utilisée",           False),
              ("Taux d'actualisation (%)",               False),
              ("Taux de rotation du personnel (%)",      False)])

        for n in range(9, 15):
            safe(self._xl_add_sheet_report, wb,
                 f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}', f'NOTE {n}', dfstr, dtstr, company)

        note_ph('NOTE 15A', '15A', "SUBVENTIONS D'INVESTISSEMENT ET PROVISIONS RÉGLEMENTÉES",
             [("SUBVENTIONS D'INVESTISSEMENT (14x)",     True),
              ("Montant brut en début d'exercice",       False),
              ("Subventions reçues",                     False),
              ("Virements au compte de résultat",        False),
              ("Montant brut en fin d'exercice",         False),
              ("PROVISIONS RÉGLEMENTÉES (15x)",          True),
              ("Montant en début d'exercice",            False),
              ("Dotations de l'exercice",                False),
              ("Reprises de l'exercice",                 False),
              ("Montant en fin d'exercice",              False)])
        note_ph('NOTE 15B', '15B', "AUTRES FONDS PROPRES",
             [("Nature des autres fonds propres",        False),
              ("Montant en début d'exercice",            False),
              ("Augmentations",                          False),
              ("Diminutions",                            False),
              ("Montant en fin d'exercice",              False)])

        safe(self._xl_add_sheet_report, wb,
             'l10n_ci_liasse_fiscale.l10n_ci_note_16a', 'NOTE 16A', dfstr, dtstr, company)

        note_ph('NOTE 16B', '16B', "ENGAGEMENTS DE RETRAITE (ACTUARIEL)",
             [("Obligation au titre des prestations définies", False),
              ("Juste valeur des actifs du régime",           False),
              ("Surplus / Déficit",                           False),
              ("Charge de retraite de l'exercice",           False),
              ("Taux d'actualisation (%)",                   False),
              ("Taux de rendement attendu des actifs (%)",   False)])
        note_ph('NOTE 16B BIS', '16B BIS', "ACTIFS ET PASSIFS DES RÉGIMES FINANCÉS",
             [("Valeur des actifs du régime en début d'ex.", False),
              ("Cotisations employeur",                      False),
              ("Cotisations salariés",                       False),
              ("Rendement réel des actifs",                  False),
              ("Valeur des actifs du régime en fin d'ex.",  False)])
        note_ph('NOTE 16C', '16C', "ACTIFS ET PASSIFS ÉVENTUELS (LITIGES)",
             [("ACTIFS ÉVENTUELS",                           True),
              ("Description du litige",                      False),
              ("Partie adverse",                             False),
              ("Montant estimé (FCFA)",                      False),
              ("PASSIFS ÉVENTUELS",                          True),
              ("Description du litige",                      False),
              ("Partie adverse",                             False),
              ("Montant estimé (FCFA)",                      False)])

        for n in range(17, 40):
            safe(self._xl_add_sheet_report, wb,
                 f'l10n_ci_liasse_fiscale.l10n_ci_note_{n}', f'NOTE {n}', dfstr, dtstr, company)

        # ── Bloc 5 : suppléments DGI ────────────────────────────────
        safe(self._xl_add_garde, wb, company, dfstr, dtstr, 'GARDE (DGI-INS)')
        note_ph('NOTES DGI-INS', 'DGI-INS', "DÉTERMINATION DE L'IMPÔT SUR LES SOCIÉTÉS",
             [("Résultat comptable (avant impôt)",           False),
              ("Réintégrations fiscales",                    False),
              ("Déductions fiscales",                        False),
              ("Résultat fiscal",                            False),
              ("Base imposable IS",                         False),
              ("Taux IS (%)",                               False),
              ("IS dû",                                     False),
              ("Crédit d'impôt / Acomptes versés",         False),
              ("IS net à payer",                            False)])
        safe(self._xl_add_comp_charges, wb, date_from, date_to, company, dfstr, dtstr)
        safe(self._xl_add_comp_tva, wb, 1, date_from, date_to, company, dfstr, dtstr)
        safe(self._xl_add_comp_tva, wb, 2, date_from, date_to, company, dfstr, dtstr)

        for n in range(1, 8):
            safe(self._xl_add_suppl, wb, n, dfstr, dtstr, company)

        safe(self._xl_add_garde, wb, company, dfstr, dtstr, 'GARDE(3)')
        safe(self._xl_add_commentaire, wb, company, dfstr, dtstr)

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()
