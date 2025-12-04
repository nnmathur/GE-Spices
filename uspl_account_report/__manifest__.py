# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Report (USPL)',
    'summary': 'Account Report (USPL)',
    'sequence': 100,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'account',
    'depends': ['base', 'account', 'l10n_in','sale', 'sale_management', 'sale_pdf_quote_builder'],
    'data': [
        # Security
        # 'security/ir.model.access.csv',
        
        # Views
        'data/data.xml',
        'reports/custom_layout.xml',
        'reports/invoice_template.xml',

        'reports/report_action.xml',
        # 'reports/sale_template.xml',

        # 'reports/sale_template_2.xml',
        
        # 'views/account_move.xml',
        # 'views/sale_inherit_view.xml',
        'views/invoice_inherit_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
