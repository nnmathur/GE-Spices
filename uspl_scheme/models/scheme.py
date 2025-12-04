from odoo import models, fields, api

class Scheme(models.Model):
    _name = "scheme.scheme"
    _inherit = [ 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Scheme"
    _rec_name = 'scheme_name'
    _order = 'id desc'

    name = fields.Char(string="Reference #", required=True, index=True, readonly=True, tracking=3, copy=False, default='New')
    state = fields.Selection([
                            ('draft', 'Draft'), 
                            ('running', 'Running'), 
                            ('expired', 'Expired'), 
                            ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    scheme_name = fields.Char(string="Scheme Name")
    scheme_erp_id = fields.Char(string="Scheme ERP Id")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    scheme_category = fields.Selection([
                                ('1', 'Primary'),
                                ('2', 'Secondary'),
                                ('3', 'Tertiary'),
                            ], string="Scheme Category")
    scheme_description = fields.Text(string="Scheme Description")
    payout_type = fields.Selection([
                                    ('1', 'FOC'),('2', 'Article'),('3', 'Discount '),('4', 'Product'),
                                    ('5', 'Top Up Discount'),('6', 'Per Unit Discount'),('7', 'Basket'),('8', 'Fixed Value Discount'),
                                    ('9', 'Percentage Discount On MRP'),('10', 'Per Unit Product'),('11', 'Product Scheme New'),
                                ], string="Pay Out Type")
    payout_calculation_type = fields.Selection([
                                        ('1', 'Step'),('2', 'Continuous'),('3', 'ProRata'),
                                        ('4', 'Recurring'),('5', 'StepMultiplier'),
                                    ], string="Pay Out Calculation Type")
    constraint_on = fields.Selection([
                                    ('1', 'Amount'),('2', 'Quantity'),('3', 'Standard Unit'),
                                    ('4', 'Super Unit')
                                    ],string="Constraint On")
    payout_in = fields.Selection([
                                ('1', 'Amount'),('2', 'Quantity'),('3', 'Standard Unit'),
                            ],string="Pay Out In")
    scheme_budget = fields.Float(string="Scheme Budget")
    applicable_at_level = fields.Selection([
                                ('0', 'Company'),('1', 'Zone'),('2', 'Region'),('3', 'Distributor')
                                ], string="Applicable At Level")
    applicable_on_entity = fields.Char(string="Applicable On Entity")
    scheme_on = fields.Selection([
                                ('1', 'Primary Category'),('2', 'Secondary Category'),('3', 'Product'),('4', 'All'),('5', 'Alternate Category')
                                ], string="Scheme On")
    scheme_on_entity = fields.Char(string="Scheme On Entity")
    eligible_on = fields.Selection([
                                ('1', 'Primary'),('2', 'Secondary')
                                ],string="Eligible On")
    eligible_on_entity = fields.Char(string="Eligible On Entity")
    scheme_type = fields.Selection([
                                ('1', 'Primary'),('2', 'Secondary')
                                ],string="Scheme Type")
    scheme_sub_type1 = fields.Selection([
                                ('1', 'Extendable'),('2', 'Non Extendable'),('3', 'Claimable'),('4', 'Non Claimable'),('5', 'NonExtendableCompanytoSSAndStockistOnly')
                                ], string="Scheme Sub Type 1")
    scheme_sub_type2 = fields.Selection([
                                ('1', 'Extendable'),('2', 'Non Extendable'),('3', 'Claimable'),('4', 'Non Claimable'),('5', 'NonExtendableCompanytoSSAndStockistOnly')
                                ], string="Scheme Sub Type 2")
    is_inclusive = fields.Boolean(string="Is Inclusive")
    outlet_constraints = fields.Selection([
                                ('1', 'RequiredIsFocused'),('2', 'RequiredChannels'),('3', 'RequiredSegmentations'),('4', 'RequiredShopTypes'),('5', 'RequiredOutletErpIds')
                                ], string="Outlet Constraints")
    product_filter_constraints = fields.Selection([
                                ('1', 'MRP'),('2', 'PTR'),
                                ], string="Product Filter Constraints")
    scheme_slabs = fields.Selection([
                                ('1', 'ConstraintValue'),('2', 'Payout'),('3', 'PayoutDescription'),('4', 'PayoutProductERPID')
                                ], string="Scheme Slabs")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.name = self.env['ir.sequence'].next_by_code('scheme.scheme') or 'New' # Generate Referencce Number
        return res

    # def write(self, vals):
    #     for rec in self:
    #         res = super().write(vals)
    #         if 'price_unit' in vals:
    #             rec.po_line_id.price_unit = rec.price_unit
    #         return res

    def action_running(self):
        for rec in self:
            rec.state = 'running'

    def action_expired(self):
        for rec in self:
            rec.state = 'expired'