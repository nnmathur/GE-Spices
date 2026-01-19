# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

try:
   import qrcode
except ImportError:
   qrcode = None
try:
   import base64
except ImportError:
   base64 = None
from io import BytesIO

from collections import defaultdict
from datetime import timedelta, date
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, float_round, format_date, groupby

class AccountMove(models.Model):
    _inherit = 'account.move'

    #Additional fields
    ack_no = fields.Char("Ack Number")
    ack_date = fields.Date("Ack Date")
    buyers_po_date = fields.Date("Buyer's Order Date")
    stock_picking_id = fields.Many2one('stock.picking', string='Delivery Note')
    is_igst = fields.Boolean(compute='_compute_is_igst_invoice')

    transporter_id = fields.Many2one('res.partner','Transporter')
    # destinaltion_mode = fields.Char('Mode Of Transport')
    transporter = fields.Char("Transporter's Detail's")
    docket_no = fields.Char("LR/Docket No. ")
    vehicle_no = fields.Char("Vehicale Registration No.")
    trnsportation_mode = fields.Selection([
        ('Managed by Transporter','Managed by Transporter'),
        ('By Road','By Road'),
        ('Rail','Rail'),
        ('Air','Air'),
        ('Ship','Ship')
    ], string='Mode Of Transport')

    goods_covered = fields.Selection([
        ('Yes','Yes'),
        ('No','No')
    ], string='Wheather Goods Covered in Invoiced Under Hypothecation')

    packing_charges = fields.Float('Packing Charges')
    fg_charges = fields.Float('Freight Charges(Included)')
    inc_charges = fields.Float('Insurance Charges(Included)')
    other_charges = fields.Float('Other(Plz Specify) ')
    total_qty = fields.Float(string='Total Quantity', compute='_compute_total_qty')

    qr_code = fields.Binary('QR Code', compute="_generate_qr")

    def _compute_total_qty(self):
        for rec in self:
            if rec.invoice_line_ids:
                rec.total_qty = sum(rec.invoice_line_ids.mapped('quantity'))
            else:
                rec.total_qty = 0
    def _compute_is_igst_invoice(self):
        for rec in self:
            is_igst = False
            if rec.partner_id and rec.company_id:
                company_state = rec.company_id.state_id
                partner_state = rec.partner_id.state_id
                if company_state and partner_state:
                    if company_state.id != partner_state.id:
                        is_igst = True
            rec.is_igst = is_igst

    def compute_amount_in_words(self,n):
        for rec in self:
            words = rec.currency_id.amount_to_text(n)
            return words

    def get_customer_pannumber(self):
        if self.partner_id.vat and len(self.partner_id.vat) >= 15:
            return str(self.partner_id.vat[2:12])
        else:
            return '' 

    def get_other_tax_total_amount(self):
        total = 0
        for rec in self:
            total = rec.packing_charges+rec.fg_charges+rec.inc_charges+rec.other_charges
        return total
    def add_a_note(self):
        pass   

    def get_customer_account(self):
        ac_name = ''
        for rec in self:
            if rec.partner_id.bank_ids:
                ac_name = rec.partner_id.bank_ids[0].bank_id.name
            return ac_name

    def get_sale_order(self):
        for rec in self:
            order_name = ''
            sale_id = self.line_ids.sale_line_ids.order_id
            for sale in sale_id:
                if order_name:
                    order_name += ', ' + sale.name
                else: 
                    order_name = sale.name
            date_order = ''
            if sale_id:
                date_order = sale_id[0].date_order

            dic = {'order':order_name, 'date':date_order}
            return dic

    def get_ship_addres(self):
        for rec in self:
            shiping_add = rec.partner_id.child_ids.filtered(lambda l: l.type == 'delivery')
            return shiping_add

    def get_tax_amount(self):
        lst = []
        for rec in self:
            for line in rec.invoice_line_ids:
                gst_tax = line.tax_ids.filtered(lambda l: l.name == 'GST')
                gst_tax = line.tax_ids.search([('name', 'ilike', 'GST')])
                igst_tax = line.tax_ids.search([('name', 'ilike', 'IGST')])
                # igst_tax = line.tax_ids.filtered(lambda l: l.name == 'IGST')
                if line.tax_ids:
                    if line.tax_ids[0].amount_type == 'group':
                        vals = {
                        'type' : 'group',
                        'line_id' : line.id,
                        'cgst_rate' : str(line.tax_ids[0].amount/2) + '%',
                        'cgst_amt' : ((line.price_subtotal*line.tax_ids[0].amount)/100)/2,
                        'sgst_rate' : str(line.tax_ids[0].amount/2) + '%',
                        'sgst_amt' : ((line.price_subtotal*line.tax_ids[0].amount)/100)/2,
                        'total_tax' : ((line.price_subtotal*line.tax_ids[0].amount)/100)/2 + ((line.price_subtotal*line.tax_ids[0].amount)/100)/2
                        }
                        lst.append(vals)
                    elif line.tax_ids[0].amount_type == 'percent':
                        vals = {
                        'type' : 'percent',
                        'line_id' : line.id,
                        'igst_rate' : str(line.tax_ids[0].amount)+'%',
                        'igst_amt' : (line.price_subtotal*line.tax_ids[0].amount)/100,
                        'total_tax' : (line.price_subtotal*line.tax_ids[0].amount)/100,

                        }
                        lst.append(vals)
                    else:
                        vals = {
                        'type' : 'OTH',
                        'line_id' : line.id,
                        'igst_rate' : str(line.tax_ids[0].amount)+'%',
                        'igst_amt' : (line.price_subtotal*line.tax_ids[0].amount)/100,
                        'total_tax' : (line.price_subtotal*line.tax_ids[0].amount)/100
                        }
                        lst.append(vals)
            return lst

    def get_tax_total_amount(self):
        dictn = {'total_tax_amt':0, 'sgst':0,'cgst':0, 'igst':0, 'total_inv_amt':0}
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.tax_ids:
                    for tax in line.tax_ids:
                        if tax.amount_type == 'group':
                            dictn['total_tax_amt'] += line.price_subtotal
                            dictn['sgst'] += ((line.price_subtotal*tax.amount)/100)/2
                            dictn['cgst'] += ((line.price_subtotal*tax.amount)/100)/2
                            dictn['total_inv_amt'] += line.price_subtotal + ((line.price_subtotal*tax.amount)/100)/2 + ((line.price_subtotal*tax.amount)/100)/2
                            
                        elif tax.amount_type == 'percent':
                            dictn['total_tax_amt'] += line.price_subtotal
                            dictn['igst'] += ((line.price_subtotal*tax.amount)/100)
                            dictn['total_inv_amt'] += line.price_subtotal + ((line.price_subtotal*tax.amount)/100)
                        else:
                            dictn['total_tax_amt'] += 0
                            dictn['igst'] += 0
                            dictn['sgst'] += 0
                            dictn['cgst'] += 0
                            dictn['total_inv_amt'] += 0

            return dictn

    def get_tax_summry(self):        
        tax_lst = []
        total_tax_ids = self.invoice_line_ids.mapped('tax_ids')
        for tax in total_tax_ids:
            if self.is_igst:
                total_tax_lines = self.invoice_line_ids.filtered(lambda l: tax.id in l.tax_ids.ids)
                total_tax_amt = sum(total_tax_lines.mapped('price_total')) - sum(total_tax_lines.mapped('price_subtotal'))
                tax_type = 'IGST Output ' + str(tax.amount) + '%'
                dictn = {'tax_type':tax_type, 'amt':total_tax_amt}
                tax_lst.append(dictn)
            else:
                tax_amt = tax.children_tax_ids[0].amount
                total_tax_lines = self.invoice_line_ids.filtered(lambda l: tax.id in l.tax_ids.ids)
                total_tax_amt = (sum(total_tax_lines.mapped('price_total')) - sum(total_tax_lines.mapped('price_subtotal')))/2
                tax_type = str(tax_amt) + '%'
                dictn = {'tax_type':tax_type, 'amt':total_tax_amt}
                tax_lst.append(dictn)
        return tax_lst

    def _get_hsn_summry(self):        
        hsn_list = []
        summry_lst = []
        total_tax_ids = self.invoice_line_ids
        for line in total_tax_ids:
            hsn = line.product_id.l10n_in_hsn_code
            if hsn not in hsn_list:
                hsn_list.append(hsn)
                total_tax_lines = self.invoice_line_ids.filtered(lambda l: l.product_id.l10n_in_hsn_code == hsn)                
                price_subtotal = sum(total_tax_lines.mapped('price_subtotal'))
                price_total = sum(total_tax_lines.mapped('price_total'))
                tax_amt = sum(total_tax_lines.mapped('price_total')) - sum(total_tax_lines.mapped('price_subtotal'))

                rate = False
                rate_gst = 0
                if line.tax_ids:
                    rate = line.tax_ids[0].name
                    rate_gst = line.tax_ids[0].amount/2
                
                dictn = {'hsn':hsn, 'price_subtotal':price_subtotal, 'rate':rate, 'rate_gst':rate_gst, 'price_total':price_total, 'igst':tax_amt, 'gst':tax_amt/2}
                summry_lst.append(dictn)
        return summry_lst

class AccountLine(models.Model):
    _inherit = 'account.move.line'
    
    transportation = fields.Float(string='Transportation')

    # quantity = fields.Float(
    #     string='Quantity',
    #     compute='_compute_quantity', store=True, readonly=False, precompute=True,
    #     digits='Line Quantity',
    #     help="The optional quantity expressed by this line, eg: number of product sold. "
    #          "The quantity is not a legal requirement but is very useful for some reports.",
    # )

    cus_quantity = fields.Float(
        string='Quantity', store=True, readonly=False, precompute=True,
        digits='Product Unit of Measure',
        help="The optional quantity expressed by this line, eg: number of product sold. "
             "The quantity is not a legal requirement but is very useful for some reports.",
    )

    # @api.depends('display_type', 'packing', 'transportation', 'price_unit', 'cus_quantity')
    # def _compute_quantity(self):
    #     for line in self:
    #         price_unit = line.price_unit if line.price_unit else 1
    #         if line.display_type == 'product':
    #             line.cus_quantity = line.cus_quantity if line.cus_quantity else 1
    #             line.quantity = (line.packing + line.transportation)/price_unit + line.cus_quantity
    #         else:
    #             line.cus_quantity = False
    #             line.quantity = False

    def compute_other_tax(self):
        total = self.packing + self.transportation
        return total

class ResCompany(models.Model):
    _inherit = 'res.company'

    fssai_license_no = fields.Char("FSSAI License. No")
    udyam = fields.Char("UDYAM")
    bank_name = fields.Char('Bank Name')
    bank_ifsc = fields.Char('IFSC Code')
    bank_account = fields.Char('Account No.')
    payment_barcode = fields.Binary('Payment QR-Code')

    def get_company_pannumber(self):
        if self.vat and len(self.vat) >= 15:
            return str(self.vat[2:12])
        else:
            return ''

class ResPartner(models.Model):
    _inherit = 'res.partner'

    addhar_no = fields.Char("Adhaar No.")
    invoice_seq = fields.Char(string='Invoice Seq.')
    product_ids = fields.Many2many('product.product', string='Product #')

    # @api.onchange('vat')
    # def onchange_vat(self):
    #     if self.vat and self.check_vat_in(self.vat):
    #         state_id = self.env['res.country.state'].search([('l10n_in_tin', '=', self.vat[:2])], limit=1)
    #         if state_id:
    #             self.state_id = state_id
    #         if self.vat[2].isalpha():
    #             self.l10n_in_pan = self.vat[2:12]

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     if res.addhar_no:
    #         old_rec = self.env['res.partner'].search([('id', '!=', res.id)]).filtered(lambda l: l.addhar_no == res.addhar_no)
    #         name = old_rec.mapped('name')
    #         if old_rec:
    #             raise UserError('Adhaar No. already exist in other customer, Please check. \n' + str(name))
    #     if res.l10n_in_pan:
    #         old_rec = self.env['res.partner'].search([('id', '!=', res.id)]).filtered(lambda l: l.l10n_in_pan == res.l10n_in_pan)
    #         name = old_rec.mapped('name')
    #         if old_rec:
    #             raise UserError('PAN already exist in other customer, Please check. \n' + str(name))
    #     return res

    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         if rec.addhar_no:
    #             old_rec = self.env['res.partner'].search([('id', '!=', rec.id)]).filtered(lambda l: l.addhar_no == rec.addhar_no)
    #             name = old_rec.mapped('name')
    #             if old_rec:
    #                 raise UserError('Adhaar No. already exist in other customer, Please check. \n' + str(name))
    #         if rec.l10n_in_pan:
    #             old_rec = self.env['res.partner'].search([('id', '!=', rec.id)]).filtered(lambda l: l.l10n_in_pan == rec.l10n_in_pan)
    #             name = old_rec.mapped('name')
    #             if old_rec:
    #                 raise UserError('PAN already exist in other customer, Please check. \n' + str(name))
    #     return res
