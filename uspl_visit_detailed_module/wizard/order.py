from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class VisitDetailedWizard(models.Model):
    _name = 'visit.detailed.wizard'

    dumy = fields.Char(string="Dumy")
    distributer_id = fields.Many2one('res.partner', string='Distributor Name')
    line_ids = fields.One2many('visit.wizard.line', 'wizard_id')

    def action_create_sale_order(self):
        sale_id = self.env['visitor.sales']
        converted_lines = self.line_ids.filtered(lambda l: l.selct and l.converted_quantity > 0)
        if converted_lines:
            vals = {
                'partner_id' : self.distributer_id.id,
                'employee_name' : self.dumy,
                'visitor_line_ids' : [(0, 0, {'product_id': line.product_id.id, 'outletname': line.visit_line_id.detailed_visit_id.outletname, 'unit_price': line.price, 'quantity': line.converted_quantity}) for line in converted_lines]
            }
            sale_id = sale_id.sudo().create(vals)
            for line in converted_lines:
                line.visit_line_id.converted_in_so_quantity += line.converted_quantity
                
                line.visit_line_id.detailed_visit_id.sale_ids = [(4, sale_id.id)]
                sale_id.visit_detailed_ids = [(4, line.visit_line_id.detailed_visit_id.id)]

            assists_ids = self.line_ids.mapped('visit_line_id').mapped('detailed_visit_id')
            assist_lst = list(dict.fromkeys(assists_ids))
            for assist in assist_lst:
                lines = assist.sales_visit_ids
                pending_lines = lines.filtered(lambda l: l.pending_convert_in_so_quantity == 0)
                not_convert_lines = lines.filtered(lambda l: l.converted_in_so_quantity == 0)
                if len(not_convert_lines) == len(lines):
                    assist.state = 'draft'
                elif len(pending_lines) == len(lines):
                    assist.state = 'fully_converted'
                else:
                    assist.state = 'partially_converted'

class VisitWizardLine(models.Model):
    _name = 'visit.wizard.line'

    wizard_id = fields.Many2one('visit.detailed.wizard', string='Wizard')
    visit_line_id = fields.Many2one('visit.detailed.sale.line', string='Visit Line Id')
    product_id = fields.Many2one('product.product', string="Product Name")
    quantity = fields.Float(string="Quantity")
    converted_quantity = fields.Float(string="To Deliver")
    price = fields.Float(string="Price")
    selct = fields.Boolean(string="Selct")


    @api.onchange('converted_quantity')
    def _onchane_check_delivered_qty(self):
        if self.converted_quantity > self.quantity:
            raise UserError('You are not allow to convert more then pending quantity.')