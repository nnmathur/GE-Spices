from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class VisitDetailedWizard(models.Model):
    _name = 'delivered.qty.wizard'

    sale_id = fields.Many2one('visitor.sales', string="Sale")
    line_ids = fields.One2many('delivered.qty.line', 'wizard_id')

    def action_release_qty(self):
        non_delivered = self.line_ids.filtered(lambda l: l.delivery_quantity == 0)
        if len(non_delivered) == len(self.line_ids):
            raise UserError('You are not entering the delivered quantity, please enter the delivered quantity or discard this screen.')

        for line in self.line_ids.filtered(lambda l: l.delivery_quantity > 0):
            line.sale_line_id.delivered_quantity += line.delivery_quantity

        pending_lines = self.line_ids.filtered(lambda l: l.delivery_quantity < l.quantity)
        if pending_lines:
            self.sale_id.state = 'partially_delivered'
        else:
            self.sale_id.state = 'delivered'

class VisitWizardLine(models.Model):
    _name = 'delivered.qty.line'

    wizard_id = fields.Many2one('delivered.qty.wizard', string='Wizard')
    sale_line_id = fields.Many2one('visitor.sales.line', string='Sale Line Id')
    product_id = fields.Many2one('product.product', string="Product Name")
    quantity = fields.Float(string="Quantity to Delivered")
    delivery_quantity = fields.Float(string="Delivery Quantity")

    @api.onchange('delivery_quantity')
    def _onchane_check_delivered_qty(self):
        if self.delivery_quantity > self.quantity:
            raise UserError('You are not allow to deliver more then pending quantity.')