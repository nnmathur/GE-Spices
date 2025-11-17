from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class VisitDetailed(models.Model):
    _name = 'visit.detailed'
    _description = 'Visit Detailed'
    _order = "id desc"

    name = fields.Char(string="Reference #", required=True, index=True, readonly=True, tracking=3, copy=False, default='New')
    visitguid = fields.Char(string="Visit Guid")
    visitid = fields.Char(string="Visit Id")
    invoicenumber = fields.Char(string="Invoice Number")
    employeename = fields.Char(string="Employee Name")
    employeeguid = fields.Char(string="Employee Guid")
    position = fields.Char(string="Position")
    positioncode = fields.Char(string="Position Code")
    distributorerpid = fields.Char(string="Distributor Erp Id")
    superstockistname = fields.Char(string="Super Stockist Name")
    superstockisterpid = fields.Char(string="Super Stockist ErpId")
    employeedesignation = fields.Char(string="Employee Designation")
    empoyeeerpid = fields.Char(string="Empoyee ERP Id")
    employeetype = fields.Char(string="Employee Type")
    outletname = fields.Char(string="Outlet Name")
    outleterpid = fields.Char(string="Outlet ERP Id")
    isfocused = fields.Boolean(string="Is Focused")

    beatname = fields.Char(string="Beat Name")
    distributor_id = fields.Many2one('res.partner', string="Distributor Name")

    beaterpid = fields.Char(string="Beat ERP Id")
    vanname = fields.Char(string="Van Name")
    vanchasisnumber = fields.Char(string="Van Chasis Number")
    warehouseerpid = fields.Char(string="Warehouse Erp Id")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    productive = fields.Boolean(string="IS Productive")
    valid = fields.Boolean(string="IS Valid")
    nosalesreason = fields.Char(string="No Sales Reason")
    remarksmanagement = fields.Char(string="Remarks Management")
    remarksdistributor = fields.Char(string="Remarks Distributor")
    remarksother = fields.Char(string="Remarks Other")
    time = fields.Date(string="Time")
    synctime = fields.Date(string="Sync Time")
    discount = fields.Char(string="Discount")
    modeofpayment = fields.Char(string="Mode Of Payment")
    sales = fields.Char(string="Sales")
    outofturn = fields.Boolean(string="Is Out Of Turn")
    istelephonic = fields.Boolean(string="Is Telephonic")
    outlet = fields.Char(string="Outlet")
    employeelocalname = fields.Char(string="Employee Local Name")
    routeerpid = fields.Char(string="Route Erp Id")
    callstarttime = fields.Date(string="Call Start Time")
    callendtime = fields.Date(string="Call End Time")
    orderinunits = fields.Float(string="Order In Units")
    orderinvalue = fields.Float(string="Order In Value")
    totalgst = fields.Float(string="Total GST")
    totaldiscount = fields.Float(string="Total Discount")
    netvalue = fields.Float(string="Net Value")
    grossvalue = fields.Float(string="Gross Value")
    isnewoutlet = fields.Boolean(string="Is New Outlet")
    internationdiscounts = fields.Char(string="Internation Discounts")
    secondarysalestype = fields.Char(string="Secondary Sales Type")
    isovc = fields.Boolean(string="Is OVC")
    nosalereasoncategory = fields.Char(string="No Sale Reason Category")
    ordersource = fields.Char(string="Order Source")
    expecteddeliverydate = fields.Char(string="Expected Delivery Date")
    isverified = fields.Boolean(string="Is Verified")

    sales_visit_ids = fields.One2many('visit.detailed.sale.line', 'detailed_visit_id')
    
    state = fields.Selection([
                            ('draft', 'Draft'), 
                            ('partially_converted', 'Partially Allocated'), 
                            ('fully_converted', 'Fully Allocated'), 
                            ('cancelled', 'Cancelled'), 
                            ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    sale_ids = fields.Many2many('visitor.sales', string='Sale Order')
    sale_count = fields.Integer(string='Sale Count', compute='_compute_count_sales')

    def _compute_count_sales(self):
        for rec in self:
            rec.sale_count = len(self.sale_ids)

    def action_open_sales(self):
        records = self.sale_ids
        action = self.env['ir.actions.actions']._for_xml_id('uspl_distributer_sale.action_visitor_sales')
        action['domain'] = [('id','in', records.ids)]
        return action

    def action_cancel(self):
        for rec in self.filtered(lambda l: l.state == 'draft'):
            rec.state = 'cancelled'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.name = self.env['ir.sequence'].next_by_code('visit.detailed') or 'New' # Generate Referencce Number
        return res

    def action_create_sale_order(self):
        employeename_lst = self.mapped('employeename')
        sigle_lst = list(dict.fromkeys(employeename_lst))
        if len(sigle_lst) > 1:
            raise UserError('Only one employee records can be converted into sales in one time.')

        line_ids = self.filtered(lambda l: l.state != 'cancelled').mapped('sales_visit_ids').filtered(lambda l: l.pending_convert_in_so_quantity > 0 and not l.is_cancel )
        wizard_id = self.env['visit.detailed.wizard'].create({'dumy' : sigle_lst[0]})
        for line in line_ids:
            vals = {
                'wizard_id' : wizard_id.id,
                'visit_line_id' : line.id,
                'product_id' : line.product_id.id,
                'quantity' : line.pending_convert_in_so_quantity,
                'price' : line.price,
                'selct' : True,
            }
            line_id = self.env['visit.wizard.line'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'name': '.',
            'view_mode': 'form',
            'res_model': 'visit.detailed.wizard',
            'res_id': wizard_id.id,
            'context': "{'create': False}",
            'target': 'new',
        }

    def action_create_sale_order_with_all_distributor(self):        
        employeename_lst = self.filtered(lambda l: l.state != 'cancelled').mapped('employeename')
        sigle_lst = list(dict.fromkeys(employeename_lst))
        
        # if len(sigle_lst) > 1:
        #     raise UserError('Only one employee records can be converted into sales in one time.')

        for emp in sigle_lst:
            distributor_ids = self.filtered(lambda l: l.state != 'cancelled').filtered(lambda l: l.employeename == emp).mapped('distributor_id')
            distributor_lst = list(dict.fromkeys(distributor_ids))
            for dist in distributor_lst:
                records = self.filtered(lambda l: l.state != 'cancelled').filtered(lambda l: l.employeename == emp and dist.id == l.distributor_id.id)
                line_ids = records.mapped('sales_visit_ids').filtered(lambda l: l.pending_convert_in_so_quantity > 0 and not l.is_cancel)
                # wizard_id = self.env['visit.detailed.wizard'].create({'dumy' : sigle_lst[0]})
                if line_ids:
                    vals = {
                        'partner_id' : dist.id,
                        'employee_name' : emp,
                        'visitor_line_ids' : [(0, 0, {'product_id': line.product_id.id, 'outletname': line.detailed_visit_id.outletname, 'unit_price': line.price, 'quantity': line.pending_convert_in_so_quantity}) for line in line_ids]
                    }
                    sale_id = self.env['visitor.sales'].create(vals)
                    for line in line_ids:                        
                        line.detailed_visit_id.sale_ids = [(4, sale_id.id)]
                        sale_id.visit_detailed_ids = [(4, line.detailed_visit_id.id)]

                records.write({'state': 'fully_converted'})
                for line in line_ids:
                    line.converted_in_so_quantity = line.quantity

    # Delete Record Validation
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(
                    'Sorry, This record delete only draft state')
        return super().unlink()
        
class VisitDetailedLine(models.Model):
    _name = 'visit.detailed.sale.line'

    detailed_visit_id = fields.Many2one('visit.detailed', string='Visit ID')
    product_erp_id = fields.Char(string="Product ERP Id")
    product_id = fields.Many2one('product.product', string="Product Name")
    product_name = fields.Char(string="Product Name")
    product_division = fields.Char(string="Product Division")
    variant = fields.Char(string="Variant")
    material = fields.Char(string="Material")
    quantity = fields.Float(string="Quantity")
    pending_convert_in_so_quantity = fields.Float(string="Pending Quantity", compute='_compute_pending_qty')
    converted_in_so_quantity = fields.Float(string="Converted in SO Quantity")
    price = fields.Float(string="Price")
    order_type = fields.Selection([
        ('online', 'Online'),
        ('offline', 'Offline'),
    ], string="Order Type")
    order_type_char = fields.Char(string="Order Type")
    discount_product = fields.Float(string="Discount Product")
    scheme_cash_discount = fields.Float(string="Scheme Cash Discount")
    scheme_quantity = fields.Float(string="Scheme Quantity")
    scheme_erp_id = fields.Char(string="Scheme ERP Id")
    suggestive_quantity = fields.Float(string="Suggestive Quantity")
    visit_id = fields.Char(string="Visit Id")
    alternate_category = fields.Char(string="Alternate Category")
    distributor_erp_id = fields.Char(string="Distributor ERP Id")
    original_ptr = fields.Float(string="Original PTR")
    distributor_type = fields.Char(string="Distributor Type")
    fa_unify_source = fields.Char(string="FA Unify Source")
    product_unit = fields.Char(string="Product Unit")
    cgst = fields.Float(string="CGST")
    sgst = fields.Float(string="SGST")
    igst = fields.Float(string="IGST")
    vat = fields.Float(string="VAT")
    first_level_discount_amount = fields.Float(string="First Level Discount Amount")
    second_level_discount_amount = fields.Float(string="Second Level Discount Amount")
    is_product_must_sell = fields.Boolean(string="Is Product Must Sell")
    is_focused = fields.Boolean(string="Is Focused")
    is_assorted = fields.Boolean(string="Is Assorted")
    additional_product_attributes = fields.Text(string="Additional Product Attributes")

    is_cancel = fields.Boolean(string='Cancel Line')

    def _compute_pending_qty(self):
        for rec in self:
            rec.pending_convert_in_so_quantity = rec.quantity - rec.converted_in_so_quantity

    def action_cancel(self):
        self.is_cancel = True