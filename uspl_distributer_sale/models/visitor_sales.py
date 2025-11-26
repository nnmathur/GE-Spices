from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class VisitorSales(models.Model):
    _name = "visitor.sales"
    _inherit = [ 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Visitor Sales"
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char(string="Reference #", required=True, index=True, readonly=True, tracking=3, copy=False, default='New')
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company, copy= False)
    partner_id = fields.Many2one('res.partner', string='Distributor')
    state = fields.Selection([
                            ('draft', 'Draft'), 
                            ('confirmed', 'Confirmed'), 
                            ('partially_delivered', 'Partially Delivered'), 
                            # ('fully_delivered', 'Fully Delivered'), 
                            ('delivered', 'Delivered'), 
                            ('cancel', 'Cancelled'), 
                            ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    expected_delivery_date = fields.Datetime(string='Expected Delivery Date', default=lambda self: fields.Datetime.now())
    visitor_line_ids = fields.One2many('visitor.sales.line', 'visit_sales_id', string='Order Lines')
    employee_name = fields.Char(string="Employee Name")
    notes = fields.Html(string='Internal Notes....')
    untaxed_amt = fields.Float(string='Untaxed Amount', compute='_compute_total_amt')
    total_tax_amt = fields.Float(string='Total Tax', compute='_compute_total_amt')
    total_amt = fields.Float(string='Total Amount', compute='_compute_total_amt')

    @api.depends('visitor_line_ids.quantity', 'visitor_line_ids.unit_price', 'visitor_line_ids.tax_id')
    def _compute_total_amt(self):
        for rec in self:
            rec.untaxed_amt = sum(rec.visitor_line_ids.mapped('untaxed_amt'))
            rec.total_tax_amt = sum(rec.visitor_line_ids.mapped('total_tax_amt'))
            rec.total_amt = sum(rec.visitor_line_ids.mapped('total_amt'))

    def action_create_sale_order(self):
        wizard_id = self.env['delivered.qty.wizard'].create({'sale_id' : self.id})
        for line in self.visitor_line_ids.filtered(lambda l: l.pending_quantity > 0):
            vals = {
                'wizard_id' : wizard_id.id,
                'sale_line_id' : line.id,
                'product_id' : line.product_id.id,
                'quantity' : line.pending_quantity,
            }
            line_id = self.env['delivered.qty.line'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': '.',
            'view_mode': 'form',
            'res_model': 'delivered.qty.wizard',
            'res_id': wizard_id.id,
            'context': "{'create': False}",
            'target': 'new',
        }


    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.name = self.env['ir.sequence'].next_by_code('visitor.sales') or 'New' # Generate Referencce Number
        return res

    # def write(self, vals):
    #     for rec in self:
    #         res = super().write(vals)
    #         if 'price_unit' in vals:
    #             rec.po_line_id.price_unit = rec.price_unit
    #         return res

    def action_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_delivered(self):
        for rec in self:
            return rec.action_create_sale_order()
            # rec.state = 'delivered'
    
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    # Delete Record Validation
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(
                    'Sorry, This record delete only draft state')
        return super().unlink()

class VisitorSalesLine(models.Model):
    _name = "visitor.sales.line"

    visit_sales_id = fields.Many2one('visitor.sales', string='Visitor Sales')
    product_id = fields.Many2one('product.product', string='Product')
    outletname = fields.Char(string="Outlet Name")
    quantity = fields.Float(string='Quantity', default=1)
    delivered_quantity = fields.Float(string='Delivered Quantity')
    pending_quantity = fields.Float(string='Pending Quantity', compute='_compute_pending_qty')
    uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id')
    unit_price = fields.Float(string='Unit Price')
    tax_id = fields.Many2one('account.tax', string='Taxes')
    untaxed_amt = fields.Float(string='Untaxed Amount', compute='_compute_total_amt')
    total_tax_amt = fields.Float(string='Total Tax', compute='_compute_total_amt')
    total_amt = fields.Float(string='Total Amount', compute='_compute_total_amt')
    state = fields.Selection([
                            ('delivered', 'Delivered'), 
                            ('cancel', 'Cancelled'), 
                            ], string='Status', readonly=True, copy=False)

    def action_delivered(self):
        for rec in self:
            rec.state = 'delivered'
            # return rec.action_create_sale_order()
            total_lines = rec.visit_sales_id.visitor_line_ids
            total_delivered = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: l.state == 'delivered')
            total_post = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: l.state)
            total_pending = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: not l.state)
            if len(total_lines) == len(total_post) and total_delivered:
                rec.visit_sales_id.state = 'delivered'
            elif total_delivered:
                rec.visit_sales_id.state = 'partially_delivered'
    
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            total_lines = rec.visit_sales_id.visitor_line_ids
            total_delivered = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: l.state == 'delivered')
            total_post = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: l.state)
            total_pending = rec.visit_sales_id.visitor_line_ids.filtered(lambda l: not l.state)

            if len(total_lines) == len(total_post) and total_delivered:
                rec.visit_sales_id.state = 'delivered'
            elif total_delivered:
                rec.visit_sales_id.state = 'partially_delivered'

    def _compute_pending_qty(self):
        for rec in self:
            rec.pending_quantity = rec.quantity - rec.delivered_quantity

    @api.depends('quantity', 'unit_price', 'tax_id')
    def _compute_total_amt(self):
        for rec in self:
            untaxed_amt = rec.quantity * rec.unit_price
            rec.untaxed_amt = untaxed_amt
            total_tax_amt = 0
            if rec.tax_id and rec.tax_id.amount_type == 'group':
                total_tax_amt = (untaxed_amt * rec.tax_id.children_tax_ids[0].amount) / 100
            if rec.tax_id and rec.tax_id.amount_type == 'percent':
                total_tax_amt = (untaxed_amt * rec.tax_id.amount) / 100

            rec.total_tax_amt = total_tax_amt
            rec.total_amt = untaxed_amt + total_tax_amt
