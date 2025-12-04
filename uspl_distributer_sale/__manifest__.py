# -*- coding: utf-8 -*-
{
    'name': "USPL Distributer Sales",
    'version': "0.1",
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'Custom',
    'summary': "Sales module for outlet sale",
    'depends': ['stock', 'base'], 
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/visitor_sales_views.xml',
        'wizard/deliverd_qty_view.xml',
    ],
    'installable': True,
    'application': True,
}
