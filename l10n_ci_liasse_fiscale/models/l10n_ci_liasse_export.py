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


class L10nCiLiasseExport(models.AbstractModel):
    _name = 'l10n.ci.liasse.export'
    _description = 'CI Liasse Fiscale XML Export Helper'

    def _get_report_options(self, report, date_from, date_to, company, previous=False):
        """Build account.report options dict for a given period."""
        if previous:
            from dateutil.relativedelta import relativedelta
            date_from = date_from - relativedelta(years=1)
            date_to = date_to - relativedelta(years=1)
        return report._get_options({
            'date': {
                'date_from': fields.Date.to_string(date_from),
                'date_to': fields.Date.to_string(date_to),
                'mode': 'range',
                'filter': 'custom',
            },
            'multi_company': [{'id': company.id, 'name': company.name}],
        })

    def _fetch_report_values(self, report_xmlid, date_from, date_to, company):
        """
        Returns two dicts: current_vals, previous_vals
        Each dict maps line_code → {label: value}
        """
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            return {}, {}

        result_cur, result_prev = {}, {}

        for period, target in [('current', result_cur), ('previous', result_prev)]:
            previous = (period == 'previous')
            options = self._get_report_options(report, date_from, date_to, company, previous)
            lines = report._get_lines(options)
            for line in lines:
                code = line.get('columns_label') or ''
                # line code is stored in line['id'] as model_id or via line_model
                line_model = line.get('line_model')
                if line_model:
                    rec = self.env[line_model].browse(line['id'])
                    code = getattr(rec, 'code', '') or ''
                if not code:
                    continue
                col_vals = {}
                for col, col_def in zip(line.get('columns', []), options.get('columns', [])):
                    label = col_def.get('expression_label', '')
                    val = col.get('no_format', 0) or 0
                    col_vals[label] = val
                target[code] = col_vals

        return result_cur, result_prev

    def _get_expression_value(self, vals_cur, vals_prev, odoo_code, label, period):
        """Retrieve a single value from pre-fetched report data."""
        source = vals_cur if period == 'current' else vals_prev
        line_data = source.get(odoo_code, {})
        return line_data.get(label, 0) or 0

    def generate_xml(self, date_from, date_to, company, liasse_type='NO'):
        """
        Generate DGI e-impôts XML for the given company and fiscal period.
        Returns the XML string (bytes).
        """
        from lxml import etree
        import math

        def fmt(val):
            """Format numeric value: integer (no decimal), empty string for zero."""
            if val is None:
                return ''
            try:
                v = float(val)
                if math.isnan(v) or math.isinf(v):
                    return ''
                return str(int(round(v)))
            except (TypeError, ValueError):
                return str(val)

        # --- Fetch financial data ---
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

        # Merge into unified lookup by odoo_code
        all_cur = {**bilan_cur, **cr_cur, **tft_cur}
        all_prev = {**bilan_prev, **cr_prev, **tft_prev}

        # --- Build XML ---
        root = etree.Element('liasse')
        root.set('type', liasse_type)
        root.set('ncc', company.vat or '')
        root.set('exercice', str(date_to.year))

        # Header / identification
        entete = etree.SubElement(root, 'entete')
        etree.SubElement(entete, 'raison_sociale').text = company.name or ''
        etree.SubElement(entete, 'date_debut').text = fields.Date.to_string(date_from)
        etree.SubElement(entete, 'date_fin').text = fields.Date.to_string(date_to)
        etree.SubElement(entete, 'monnaie').text = company.currency_id.name or 'XOF'

        # Fixed financial fields
        champs = etree.SubElement(root, 'champs')

        for dgi_code, (odoo_code, label, period) in ALL_FINANCIAL_MAPPINGS.items():
            source = all_cur if period == 'current' else all_prev
            line_data = source.get(odoo_code, {})
            val = line_data.get(label, 0) or 0
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = fmt(val)

        # FR1 identification fields (company info)
        company_fields = {
            'NO_FR1_ZA1_1': fields.Date.to_string(date_from),
            'NO_FR1_ZA2_1': fields.Date.to_string(date_to),
            'NO_FR1_ZK4_1': company.city or '',
            'NO_FR1_ZL_1': company.street or '',
            'NO_FR1_ZK2_1': company.zip or '',
            'NO_FR1_ZK1_1': company.email or '',
        }
        for dgi_code, val in company_fields.items():
            el = etree.SubElement(champs, 'champ')
            el.set('code', dgi_code)
            el.text = str(val)

        xml_bytes = etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        return xml_bytes
