# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Contact (USPL)',
    'summary': 'Custom Contact (USPL)',
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'CRM',
    'depends': ['contacts', 'purchase', 'account', 'crm', 'hr'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        # 'data/data.xml',
        'views/beats_outlet_view.xml',
        'views/contact_view.xml',
        'views/employee_view_inherit.xml',
        # 'reports/custom_layout.xml',
        # 'reports/invoice_template.xml',

        # 'reports/purchase_template.xml',
        # 'reports/report_action.xml',
        # 'reports/sale_template.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
