# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Inventory (USPL)',
    'summary': 'Custom Sales Inventory (USPL)',
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'Sales',
    'depends': ['sale', 'purchase', 'uspl_scheme'],
    'data': [
        # Security
        # 'security/ir.model.access.csv',
        
        # Views
        # 'data/data.xml',
        'views/scheme_view_inherit.xml',
        'views/sale_pricelist_inherit_view.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
