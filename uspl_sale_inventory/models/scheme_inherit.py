# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Scheme(models.Model):
    _inherit = "scheme.scheme"

    pricelist_id = fields.Many2one('product.pricelist', string='Applicable On Pricelist')
