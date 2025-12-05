import requests
from odoo import models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class Partner(models.Model):
    _inherit = "visit.detailed"

    def action_sync_to_fieldassist(self):
        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        
        # FieldAssist Product API
        distributer_url = "https://api.fieldassist.in/api/V3/Visit/detailedVisit?lastVisitId=1924724630&includeUnproductive=false"
        response = requests.get(distributer_url, auth=(username, password))

        if response.status_code == 200:
            distributers = response.json()
            self.action_create_visits(distributers)  
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Detailed Visit Imported successfully!!",
                    "sticky": False,   # True = message tab tak rahega jab tak user close na kare
                    "type": "success", # success / warning / info / danger
                },
            }             
        else:
            print("Error:", response.text)

    def action_create_visits(self, distributers):
        for dist in distributers:
            distributor_id = False
            distributor = self.env['beat.beat'].search([('name', '=', dist["BeatName"])])
            if distributor:
                distributor_id = distributor[0].distributor_id.id

            vals = {
                    'visitguid'  : dist["VisitGuid"],
                    'visitid'  : dist["VisitId"],
                    'invoicenumber'  : dist["InvoiceNumber"],
                    'employeename'  : dist["EmployeeName"],
                    'employeeguid'  : dist["EmployeeGuid"],
                    'position'  : dist["Position"],
                    'positioncode'  : dist["PositionCode"],
                    'distributorerpid'  : dist["DistributorErpId"],
                    'superstockistname'  : dist["SuperStockistName"],
                    'superstockisterpid'  : dist["SuperStockistErpId"],
                    'employeedesignation'  : dist["EmployeeDesignation"],
                    'empoyeeerpid'  : dist["EmpoyeeERPId"],
                    'employeetype'  : dist["EmployeeType"],
                    'outlet'  : dist["Outlet"]["OutletId"],
                    'outletname'  : dist["OutletName"],
                    'outleterpid'  : dist["OutletERPId"],
                    'isfocused'  : dist["IsFocused"],

                    'beatname'  : dist["BeatName"],
                    'distributor_id'  : distributor_id,

                    'beaterpid'  : dist["BeatERPId"],
                    'vanname'  : dist["VanName"],
                    'vanchasisnumber'  : dist["VanChasisNumber"],
                    'warehouseerpid'  : dist["WarehouseErpId"],
                    'latitude'  : dist["Latitude"],
                    'longitude'  : dist["Longitude"],
                    'productive'  : dist["Productive"],
                    'valid'  : dist["Valid"],
                    'nosalesreason'  : dist["NoSalesReason"],
                    'remarksmanagement'  : dist["RemarksManagement"],
                    'remarksdistributor'  : dist["RemarksDistributor"],
                    'remarksother'  : dist["RemarksOther"],
                    'time'  : dist["Time"],
                    'synctime'  : dist["SyncTime"],
                    'discount'  : dist["Discount"],
                    'modeofpayment'  : dist["ModeOfPayment"],

                    'outofturn' : ["OutOfTurn"],
                    'istelephonic' : ["IsTelephonic"],   

                    'employeelocalname' : dist["EmployeeLocalName"],
                    'routeerpid' : dist["RouteErpId"],
                    'callstarttime' : dist["CallStartTime"],
                    'callendtime' : dist["CallEndTime"],
                    'orderinunits' : dist["OrderInUnits"],
                    'orderinvalue' : dist["OrderInValue"],
                    'totalgst' : dist["TotalGST"],
                    'totaldiscount' : dist["TotalDiscount"],
                    'netvalue' : dist["NetValue"],
                    'grossvalue' : dist["GrossValue"],
                    'isnewoutlet' : dist["IsNewOutlet"],

                    'secondarysalestype' : dist["SecondarySalesType"],
                    'isovc' : dist["IsOVC"],
                    'nosalereasoncategory' : dist["NoSaleReasonCategory"],
                    'ordersource' : dist["OrderSource"],
                    'expecteddeliverydate' : dist["ExpectedDeliveryDate"],
                    'isverified' : dist["IsVerified"],

                }

            distributer_id = self.env['visit.detailed'].sudo().create(vals)

            for line in dist["Sales"]:
                product_id = self.env['product.product'].search([('name', '=', line["ProductName"])])
                if not product_id:
                    product_id = self.env['product.product'].create({'name' : line["ProductName"]})
                vals_line = {
                      'detailed_visit_id' : distributer_id.id,
                      'product_erp_id' : line["ProductERPId"],
                      'product_id' : product_id.id,
                      # 'product_name' : line["ProductName"],
                      'product_division' : line["ProductDivision"],
                      'variant' : line["Variant"],
                      'material' : line["Material"],
                      'quantity' : line["Quantity"],
                      'price' : line["Price"],
                      
                      'order_type_char' : line["OrderType"],
                      
                      'discount_product' : line["Discount_Product"],
                      'scheme_cash_discount' : line["SchemeCashDiscount"],
                      'scheme_quantity' : line["SchemeQuantity"],
                      'scheme_erp_id' : line["SchemeErpId"],
                      'suggestive_quantity' : line["SuggestiveQuantity"],
                      'visit_id' : line["VisitId"],
                      'alternate_category' : line["AlternateCategory"],
                      'distributor_erp_id' : line["DistributorErpId"],
                      'original_ptr' : line["OriginalPTR"],
                      'distributor_type' : line["DistributorType"],
                      'fa_unify_source' : line["FAUnifySource"],
                      'product_unit' : line["ProductUnit"],
                      'cgst' : line["CGST"],
                      'sgst' : line["SGST"],
                      'igst' : line["IGST"],
                      'vat' : line["VAT"],
                      'first_level_discount_amount' : line["FirstLevelDiscountAmount"],
                      'second_level_discount_amount' : line["SecondLevelDiscountAmount"],
                    }
                distributer_line_id = self.env['visit.detailed.sale.line'].sudo().create(vals_line)
