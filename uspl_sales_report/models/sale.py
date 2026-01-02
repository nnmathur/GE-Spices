# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    mrp = fields.Float(string='MRP', compute='_compute_mrp', store=True)
    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit_custom',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
    
    @api.depends('product_template_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit_custom(self):
        for rec in self:
            is_old = True
            pricelist_item_line = rec.order_id.pricelist_id.item_ids.filtered(lambda l: l.product_tmpl_id.id == rec.product_template_id.id)
            if pricelist_item_line:
                line = pricelist_item_line.base_pricelist_id.item_ids.filtered(lambda l: l.product_tmpl_id.id == rec.product_template_id.id)
                if line:
                    rec.discount = pricelist_item_line.percent_price
                    rec.price_unit = line.fixed_price
                else:
                    rec.price_unit = pricelist_item_line.fixed_price
                    rec.discount = pricelist_item_line.percent_price
            else:
                company = rec.company_id.id
                rec.price_unit = rec.product_id.with_company(company).lst_price
                rec.discount = 0

    @api.depends('product_id', 'product_template_id')
    def _compute_mrp(self):
        for rec in self:
            company = rec.company_id.id
            rec.mrp = rec.product_id.with_company(company).new_mrp

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)

        # res can be False in some edge cases
        if not res:
            return res

        # Add MRP (company-dependent value auto handled)
        res['mrp'] = self.mrp

        return res

class Product(models.Model):
    _inherit = 'product.template'

    mrp = fields.Float(string='MRP Old')

    # mrp = product.with_company(company).mrp
    new_mrp = fields.Float(string='MRP', company_dependent=True)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    mrp = fields.Float(string='MRP', compute='_compute_mrp', store=True)

    @api.depends('product_id')
    def _compute_mrp(self):
        for rec in self:
            company = rec.company_id.id
            rec.mrp = rec.product_id.with_company(company).new_mrp
