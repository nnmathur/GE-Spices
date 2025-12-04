# -*- coding: utf-8 -*-
{
    'name': "USPL Schemes",
    'version': "0.1",
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'Custom',
    'summary': "Schemes Module from Field Assist",
    'depends': ['mail', 'base'], 
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/scheme_views.xml',
    ],
    'installable': True,
    'application': True,
}
