# -*- coding: utf-8 -*-
{
    'name': "USPL Sales Report",
    'version': "0.1",
    'sequence': 50,
    'version': '1.0',
    'license': 'LGPL-3',
    'support': 'unilinkindia.com',
    'author': 'UnilinkIndia Software Pvt. Ltd.',
    'website': 'http://unilinkindia.com',
    'category': 'Sales',
    'summary': "Added Sales Report",
    'depends': ['sale', 'product'], 
    'data': [
        # 'data/sequence.xml',
        'security/ir.model.access.csv',
        "views/views.xml",
        "report/emp_wd_report_view.xml",
        "report/emp_distributor_report_view.xml",
        # "wizard/order_view.xml",
    ],
    'installable': True,
    'application': True,
}
