# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
class Product(models.Model):
    _inherit = 'product.template'

    mrp = fields.Float(string='MRP')