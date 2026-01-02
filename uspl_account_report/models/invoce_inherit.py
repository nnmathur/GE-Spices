from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pkd_date = fields.Date(string="PKD Date")
    mrp = fields.Float(string="Mrp")
    packing = fields.Float(string='Packaging')
    
    fixed_discount = fields.Float(string="Fixed Dist.(%)", default=0.0)
    damage_discount = fields.Float(string="Scheme Dist.(%)", default=0.0)
    spl_discount = fields.Float(string="Spl Dist.(%)", default=0.0)

    fixed_discount_amt = fields.Float(string="Fixed Amt.")
    damage_discount_amt = fields.Float(string="Scheme Amt.")
    spl_discount_amt = fields.Float(string="Spl Amt.")

    @api.depends('product_id')
    def _compute_mrp(self):
        for rec in self:
            company = rec.company_id.id
            rec.mrp = rec.product_id.with_company(company).new_mrp

    # @api.depends('fixed_discount','damage_discount','spl_discount', 'price_unit', 'quantity')
    # def _compute_discounts(self):
    #     for rec in self:
    #         rec.fixed_discount_amt = ((rec.quantity * rec.price_unit) * rec.fixed_discount) / 100
    #         rec.damage_discount_amt = ((rec.quantity * rec.price_unit) * rec.damage_discount) / 100
    #         rec.spl_discount_amt = ((rec.quantity * rec.price_unit) * rec.spl_discount) / 100
    #         rec.discount = rec.fixed_discount + rec.damage_discount + rec.spl_discount

    '''
    @api.depends(
        'price_unit', 'quantity', 'discount', 'tax_ids', 'fixed_discount', 'damage_discount', 'spl_discount', 'spl_discount_amt', 'damage_discount_amt', 'fixed_discount_amt'
    )
    def _compute_totals(self):
        """
        Override invoice line total calculation.
        """
        for line in self:
            if line.display_type in ('line_section', 'line_note'):
                line.price_subtotal = 0.0
                line.price_total = 0.0
                continue

            # Price after % discount
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # Subtotal
            subtotal = price * line.quantity

            # Apply fixed discount
            subtotal -= line.fixed_discount_amt
            subtotal -= line.damage_discount_amt
            subtotal -= line.spl_discount_amt

            # Taxes
            taxes_res = line.tax_ids.compute_all(
                subtotal / line.quantity if line.quantity else 0.0,
                line.move_id.currency_id,
                line.quantity,
                product=line.product_id,
                partner=line.move_id.partner_id,
            )

            line.price_subtotal = taxes_res['total_excluded']
            line.price_total = taxes_res['total_included']
    '''

class AccountMove(models.Model):
    _inherit = "account.move"

    amount_fixed_discount = fields.Monetary(
        string="Total Fixed Discount",
        compute="_compute_amount_fixed_discount",
        store=True, readonly=True
    )

    @api.depends('invoice_line_ids.fixed_discount')
    def _compute_amount_fixed_discount(self):
        for move in self:
            move.amount_fixed_discount = sum(move.invoice_line_ids.mapped('fixed_discount_amt')) + sum(move.invoice_line_ids.mapped('damage_discount_amt')) + sum(move.invoice_line_ids.mapped('spl_discount_amt'))

    # @api.depends(
    #     'invoice_line_ids.price_subtotal', 'invoice_line_ids.price_total',
    #     'amount_fixed_discount'
    # )
    # def _compute_amount(self):
    #     """
    #     Override totals on invoice to include fixed discount.
    #     """
    #     super()._compute_amount()
    #     for move in self:
    #         # Ensure fixed discount shows in totals (though already applied in lines)
    #         move.amount_total = sum(move.invoice_line_ids.mapped('price_total'))
    #         move.amount_untaxed = sum(move.invoice_line_ids.mapped('price_subtotal'))

    # @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.price_total')
    # def _compute_amount(self):
    #     """
    #     Override totals on invoice to include fixed discount.
    #     """
    #     for move in self:
    #         amount_untaxed = amount_tax = 0.0
    #         for line in move.invoice_line_ids:
    #             if line.display_type in ('line_section', 'line_note'):
    #                 continue
    #             amount_untaxed += line.price_subtotal
    #             amount_tax += line.price_total - line.price_subtotal

    #         move.amount_untaxed = amount_untaxed
    #         move.amount_tax = amount_tax
    #         move.amount_total = amount_untaxed + amount_tax
    #         move.amount_fixed_discount = sum(move.invoice_line_ids.mapped('fixed_discount'))
    
    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.balance',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'state', 'amount_fixed_discount', 'invoice_line_ids.price_total', 'line_ids.price_total')
    # def _compute_amount(self):
    #     for move in self:
    #         total_untaxed, total_untaxed_currency = 0.0, 0.0
    #         total_tax, total_tax_currency = 0.0, 0.0
    #         total_residual, total_residual_currency = 0.0, 0.0
    #         total, total_currency = 0.0, 0.0

    #         for line in move.line_ids:
    #             if move.is_invoice(True):
    #                 # === Invoices ===
    #                 if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
    #                     # Tax amount.
    #                     total_tax += line.balance
    #                     total_tax_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type in ('product', 'rounding'):
    #                     # Untaxed amount.
    #                     total_untaxed += line.balance
    #                     total_untaxed_currency += line.amount_currency
    #                     total += line.balance
    #                     total_currency += line.amount_currency
    #                 elif line.display_type == 'payment_term':
    #                     # Residual amount.
    #                     total_residual += line.amount_residual
    #                     total_residual_currency += line.amount_residual_currency
    #             else:
    #                 # === Miscellaneous journal entry ===
    #                 if line.debit:
    #                     total += line.balance
    #                     total_currency += line.amount_currency

    #         sign = move.direction_sign
    #         move.amount_untaxed = sign * total_untaxed_currency
    #         move.amount_tax = sign * total_tax_currency
    #         move.amount_total = sign * total_currency
    #         move.amount_residual = -sign * total_residual_currency
    #         move.amount_untaxed_signed = -total_untaxed
    #         move.amount_tax_signed = -total_tax
    #         move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
    #         move.amount_residual_signed = total_residual
    #         move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
