from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_fixed_discount = fields.Monetary(
        string="Total Fixed Discount", compute="_compute_amount_fixed_discount",
        store=True, readonly=True
    )

    @api.depends('order_line.fixed_discount','order_line.damage_discount','order_line.spl_discount')
    def _compute_amount_fixed_discount(self):
        for order in self:
            order.amount_fixed_discount = sum(order.order_line.mapped('fixed_discount_amt')) + sum(order.order_line.mapped('damage_discount_amt')) + sum(order.order_line.mapped('spl_discount_amt'))

    '''
    def _compute_tax_totals(self):
        """
        Override sale order tax_totals to subtract fixed discounts.
        """
        AccountTax = self.env['account.tax']
        for order in self:
            # Prepare base lines (normal Odoo logic)
            
            # base_lines = order.order_line._prepare_tax_base_line_vals()
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            # Let Odoo compute taxes normally
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

            # Total fixed discount from lines
            fixed_discount_total = order.amount_fixed_discount
            amount_untaxed = sum(order.order_line.mapped('price_subtotal'))
            amount_total = sum(order.order_line.mapped('price_total'))
            order.amount_untaxed = amount_untaxed
            order.amount_total = amount_total
            order.amount_tax = sum(order.order_line.mapped('price_total')) - sum(order.order_line.mapped('price_subtotal'))

            if fixed_discount_total:
                # Also adjust the subtotal block ("Untaxed Amount")
                for subtotal in tax_totals.get('subtotals', []):
                    if subtotal.get('name') == 'Untaxed Amount':
                        
                        subtotal['base_amount_currency'] = max(
                            0, subtotal['base_amount_currency'] - fixed_discount_total
                        )
                        subtotal['base_amount'] = max(
                            0, subtotal['base_amount'] - fixed_discount_total
                        )
                    
                    for tax_subtotal in subtotal.get('tax_groups'):
                        tax_id = self.env['account.tax'].sudo().search([('id', 'in', tax_subtotal.get('involved_tax_ids'))])
                        so_lines = order.order_line.filtered(lambda l: tax_id.id in l.tax_id.ids)
                        total_tax = sum(so_lines.mapped('price_total')) - sum(so_lines.mapped('price_subtotal'))
                        if tax_id and not so_lines:
                            tax_id = self.env['account.tax'].sudo().search([]).filtered(lambda l: tax_subtotal.get('involved_tax_ids')[0] in l.children_tax_ids.ids)
                            so_lines = order.order_line.filtered(lambda l: tax_id.id in l.tax_id.ids)
                        
                            total_tax = (sum(so_lines.mapped('price_total')) - sum(so_lines.mapped('price_subtotal'))) / 2
                                                
                        tax_subtotal['tax_amount_currency'] = max(
                            0, total_tax
                        )
                        tax_subtotal['tax_amount'] = max(
                            0, total_tax
                        )

                # Adjust untaxed and total amounts
                tax_totals['base_amount_currency'] = max(
                    0, amount_untaxed
                )

                tax_totals['base_amount'] = max(
                    0, amount_untaxed
                )
                tax_totals['total_amount_currency'] = max(
                    0, amount_total
                )
                tax_totals['total_amount'] = max(
                    0, amount_total
                )
            # Assign the modified dict
            order.tax_totals = tax_totals
    '''

    def _create_invoices(self, grouped=False, final=False, date=None):
        # Call original method
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)

        for order in self:
            # Get the delivery order(s) (stock pickings)
            pickings = order.picking_ids.filtered(lambda p: p.state in ['done'])

            # Optionally pick the latest or the first
            picking = pickings[:1]

            # Assign to the invoice
            for invoice in invoices:
                invoice.stock_picking_id = picking.id

        return invoices


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_qty = fields.Float(string="Quantity", digits='Product Unit of Measure', default=1.0, readonly=False, required=True)

    fixed_discount = fields.Float(string="Fixed Dist.(%)", default=0.0)
    damage_discount = fields.Float(string="Scheme Dist.(%)", default=0.0)
    spl_discount = fields.Float(string="Spl Dist.(%)", default=0.0)

    # fixed_discount_amt = fields.Float(string="Fixed Amt.", compute='_compute_discounts')
    fixed_discount_amt = fields.Float(string="Fixed Amt.")
    damage_discount_amt = fields.Float(string="Scheme Amt.")
    spl_discount_amt = fields.Float(string="Spl Amt.")

    # @api.depends('fixed_discount','damage_discount','spl_discount', 'price_unit', 'product_uom_qty')
    # def _compute_discounts(self):
    #     for rec in self:
    #         rec.fixed_discount_amt = ((rec.product_uom_qty * rec.price_unit) * rec.fixed_discount) / 100
    #         rec.damage_discount_amt = ((rec.product_uom_qty * rec.price_unit) * rec.damage_discount) / 100
    #         rec.spl_discount_amt = ((rec.product_uom_qty * rec.price_unit) * rec.spl_discount) / 100
    #         rec.discount = rec.fixed_discount_amt + rec.damage_discount_amt + rec.spl_discount_amt

    # @api.depends(
    #     'product_uom_qty', 'discount', 'price_unit',
    #     'tax_id', 'fixed_discount', 'damage_discount', 'spl_discount' , 'damage_discount_amt', 'fixed_discount_amt', 'spl_discount_amt'
    # )

    # @api.depends('display_type', 'product_id', 'product_packaging_qty', 'fixed_discount', 'damage_discount', 'spl_discount')
    # def _compute_product_uom_qty(self):
    #     for line in self:
    #         qty = ((line.custom_qty * line.price_unit) - line.fixed_discount - line.damage_discount - line.spl_discount) / line.price_unit
    #         line.product_uom_qty = qty
    #         # if line.display_type:
    #         #     line.product_uom_qty = 0.0
    #         #     continue

    #         # if not line.product_packaging_id:
    #         #     continue
    #         # packaging_uom = line.product_packaging_id.product_uom_id
    #         # qty_per_packaging = line.product_packaging_id.qty
    #         # product_uom_qty = packaging_uom._compute_quantity(
    #         #     line.product_packaging_qty * qty_per_packaging, line.product_uom)
    #         # if float_compare(product_uom_qty, line.product_uom_qty, precision_rounding=line.product_uom.rounding) != 0:
    #         #     line.product_uom_qty = product_uom_qty

    '''
    def _compute_amount(self):
        """
        Override to subtract fixed discount as well as percentage discount.
        """
        for line in self:
            # Base price after percentage discount
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # Compute subtotal (without taxes)
            subtotal = price * line.product_uom_qty

            # Subtract fixed discount
            subtotal -= line.fixed_discount_amt
            subtotal -= line.damage_discount_amt
            subtotal -= line.spl_discount_amt

            # Apply taxes
            taxes = line.tax_id.compute_all(
                subtotal / line.product_uom_qty if line.product_uom_qty else 0.0,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id
            )

            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    '''