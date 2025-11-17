# -*- coding: utf-8 -*-
{
    'name': "USPL Visit Detailed",
    'version': "0.1",
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'Custom',
    'summary': "Visit Detailed Module from Field Assist",
    'depends': ['uspl_distributer_sale', 'base', 'product', 'sale'], 
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        "views/visit_detailed_view.xml",
        "views/sale_view_inherit.xml",
        "wizard/order_view.xml",
    ],
    'installable': True,
    'application': True,
}
