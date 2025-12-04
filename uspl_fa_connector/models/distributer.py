import requests
from odoo import models, _, fields
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import json
import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"

    fa_distributor_id = fields.Char(string="FA Distributor ID")
    fa_sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ], default='pending', string="FA Sync Status")

    def action_get_beats(self):
        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        
        # FieldAssist Product API
        for rec in self.filtered(lambda l: l.DistributorERPId):
            distributer_url = "https://api.fieldassist.in/api/V3/Distributor/Beats/" + str(rec.DistributorERPId)
            response = requests.get(distributer_url, auth=(username, password))

            if response.status_code == 200:
                dist = response.json()
                for dis in dist:
                    print('\n\n====BEATS======',dis)
                    vals = {
                        'name' : dis["Name"],
                        'distributor_id' : rec.id,
                    }
                    beat_id = self.env['beat.beat'].create(vals)
            else:
                print("Error:", response.text)

    def action_get_outlets(self):
        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        
        # FieldAssist Product API
        for rec in self.filtered(lambda l: l.DistributorERPId):
            distributer_url = "https://api.fieldassist.in/api/V3/Distributor/Outlets/" + str(rec.DistributorERPId)
            response = requests.get(distributer_url, auth=(username, password))

            if response.status_code == 200:
                dist = response.json()
                for dis in dist:
                    vals = {
                        'name' : dis["OutletName"],
                        'distributor_id' : rec.id,
                    }
                    beat_id = self.env['outlet.outlet'].create(vals)
            else:
                print("Error:", response.text)

    def action_sync_to_fieldassist(self):
        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        today = datetime.today().strftime("%Y-%m-%d")
        
        # FieldAssist Product API
        distributer_url = "https://api.fieldassist.in/api/V3/Distributor/list"

        # Basic Auth with username & password
        params = {
            "fromDate": f"{today}T00:00:00",
            "toDate": f"{today}T23:59:59"
        }
        response = requests.get(distributer_url, params=params, auth=(username, password))

        if response.status_code == 200:
            distributers = response.json()
            self.action_create_distributer(distributers)  
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

    def action_create_distributer(self, distributers):
        for dist in distributers:
            partner_id = self.env['res.partner'].sudo().search(['|', ('name', '=', dist["Name"]), ('email', '=', dist["EmailId"])])
            if not partner_id or partner_id:
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

    # def action_sync_to_fieldassist(self):
    #     username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
    #     password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')

    #     # FieldAssist Product API
    #     distributer_url = "https://api.fieldassist.io/api/V3/Distributor/Create"

    #     headers = {
    #         "Content-Type": "application/json",
    #     }

    #     payload = [{
    #         "Name": "sample string 2",
    #         "ContactNo": "sample string 3",
    #         "EmailId": "sample string 4",
    #         "SecondaryEmailId": "sample string 5",
    #         "Manager": "sample string 6",
    #         "DistributorERPId": "sample string 7",
    #         "LocalName": "sample string 8",
    #         # "Address": "sample string 9",
    #         "City": "sample string 10",
    #         "Place": "sample string 11",
    #         "GSTIN": "qwe123rew4356re",
    #         "TIN": "qwer3456ytre4",
    #         "Pincode": "kjh789",
    #         "Region": "sample string 15",
    #         "IsActive": True
    #     }]

    #     try:
    #         response = requests.post(distributer_url, headers=headers, data=json.dumps(payload), auth=(username, password))
    #         # response = requests.post(distributer_url, headers=headers, data=json.dumps(payload))
    #         response_data = response.json()

    #         if response.status_code == 200 and response_data.get("IsSuccess"):
    #             self.fa_sync_status = "success"
    #             self.fa_distributor_id = response_data.get("DistributorId", "")
    #         else:
    #             self.fa_sync_status = "failed"
    #             _logger.error("FA Distributor Sync Failed: %s", response_data)

    #     except Exception as e:
    #         self.fa_sync_status = "failed"
    #         _logger.error("FA API Error: %s", e)