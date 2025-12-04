from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class VisitorSales(models.Model):
    _inherit = "visitor.sales"

    visit_detailed_ids = fields.Many2many('visit.detailed', string='Visit Details')
    visit_count = fields.Integer(string='Visit Count', compute='_compute_count_visits')

    def _compute_count_visits(self):
        for rec in self:
            rec.visit_count = len(self.visit_detailed_ids)

    def action_open_visits(self):
        records = self.visit_detailed_ids
        action = self.env['ir.actions.actions']._for_xml_id('uspl_visit_detailed_module.action_visit_detailed')
        action['domain'] = [('id','in', records.ids)]
        return action