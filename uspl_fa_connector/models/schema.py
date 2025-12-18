import requests
from odoo import models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class Scheme(models.Model):
    _inherit = "scheme.scheme"

    def action_sync_to_fieldassist(self):
        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        today = datetime.today().strftime("%Y-%m-%d")
        
        # FieldAssist Product API
        scheme_url = "https://api.fieldassist.in/api/V3/Schemes/CreateMultiple"

        # Basic Auth with username & password
        response = requests.get(scheme_url, auth=(username, password))

        if response.status_code == 200:
            shceme = response.json()
            for sch in shceme:
                print('\n====')
                print('shceme',shceme)
            # self.action_create_distributer(shceme)  
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": "Distributor Imported successfully!!",
                    "sticky": False,   # True = message tab tak rahega jab tak user close na kare
                    "type": "success", # success / warning / info / danger
                },
            }             
        else:
            print("Error:", response.text)

    def action_create_distributer(self, shceme):
        for dist in shceme:
            return
            partner_id = self.env['res.partner'].sudo().search(['|', ('name', '=', dist["Name"]), ('email', '=', dist["EmailId"])])
            # if not partner_id or partner_id:
            vals = {
                    "name": dist["Name"],
                    "Id": dist["Id"],
                    "mobile": dist["ContactNo"],
                    "email": dist["EmailId"],
                    "SecondaryEmailId": dist["SecondaryEmailId"],
                    "Manager": dist["Manager"],
                    "DistributorERPId": dist["DistributorERPId"],
                    "LocalName": dist["LocalName"],
                    "street": dist["Address"],
                    "street2": dist["Place"],
                    "vat": dist["GSTIN"],
                    "TIN": dist["TIN"],
                    "zip": dist["Pincode"],
                    "city": dist["Region"],
                    # "RegionERPId": dist["RegionERPId"],
                    "Zone": dist["Zone"],
                    "ZoneErpId": dist["ZoneErpId"],
                    "ParentERPId": dist["ParentERPId"],
                    "DistributorCategory": dist["DistributorCategory"],
                    "DistributorGrade": dist["DistributorGrade"],
                    "DistributorChannelErpId": dist["DistributorChannelErpId"],
                    "l10n_in_pan": dist["PANNumber"],
                    "FSSAINumber": dist["FSSAINumber"],
                    "UdyamNumber": dist["MsmeNumber"],
                    "FSSAIExiryDate": dist["FSSAIExiryDate"],

                    "BankName": dist["BankName"],
                    "BankAccountNumber": dist["BankAccountNumber"],
                    "BankIFSCCode": dist["BankIFSCCode"],
                    "StockistType": dist["StockistType"],
                    
                    "DistributorChannelIdErpId": dist["DistributorChannelIdErpId"],
                    "DistributorSegmentationIdErpId": dist["DistributorSegmentationIdErpId"],
                    
                    # "State": dist["State"],

                    "PlaceOfSupply": dist["PlaceOfSupply"],
                    "WarehouseId": dist["WarehouseId"],
                    "WarehouseState": dist["WarehouseState"],
                    "WarehouseCity": dist["WarehouseCity"],
                    "WarehouseAddress": dist["WarehouseAddress"],
                    "WarehouseName": dist["WarehouseName"],
                    "WarehouseErpId": dist["WarehouseErpId"],
                    "SecurityDeposit": dist["SecurityDeposit"],
                    "DDNumber": dist["DDNumber"],
                    "DateOfPayment": dist["DateOfPayment"],
                    "PaymentMode": dist["PaymentMode"],
                    "IsGSTRegistered": dist["IsGSTRegistered"],
                    "IntransitPeriod": dist["IntransitPeriod"],
                    "CreditDuration": dist["CreditDuration"],
                    "CreditValue": dist["CreditValue"],
                    "CreditInvoiceCount": dist["CreditInvoiceCount" ],
                    # "Latitude": dist["Latitude"],
                    # "Longitude": dist["Longitude"],
                    "Aadhar": dist["Aadhar"],
                    "DOB": dist["DOB"],
                    "OwnerName": dist["OwnerName"],
                    "OwnerNo": dist["OwnerNo"],
                    "CashDiscountLimit": dist["CashDiscountLimit"],
                }            
            distributer_id = self.env['res.partner'].sudo().create(vals)