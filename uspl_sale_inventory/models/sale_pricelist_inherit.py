# -*- coding: utf-8 -*-
from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    scheme_id = fields.Many2one('scheme.scheme', string='Scheme')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.scheme_id.pricelist_id = res.id
        return res

    def write(self, vals):
        res = super().write(vals)
        self.scheme_id.pricelist_id = self.id
        return res

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    product_template_ids = fields.Many2many('product.template', string='Products', copy=False)
    category_ids = fields.Many2many('product.category', string='Category', copy=False)

    @api.onchange('product_template_ids')
    def _onchane_product(self):
        self.category_ids = False
        if self.product_template_ids:
            self.product_tmpl_id = self.product_template_ids[0].id

    @api.onchange('category_ids')
    def _onchane_category(self):
        self.product_template_ids = False
        if self.category_ids:
            self.categ_id = self.category_ids[0].id

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.display_applied_on == '1_product' and res.product_template_ids:
            for prod in res.product_template_ids.filtered(lambda l: l.id != res.product_tmpl_id.id):
                new_rec = res.copy()
                new_rec.product_tmpl_id = prod.id
        if res.display_applied_on == '2_product_category' and res.category_ids:
            for catg in res.category_ids.filtered(lambda l: l.id != res.categ_id.id):
                new_rec = res.copy()
                new_rec.categ_id = catg.id
        
        return res
