import requests
from odoo import models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_sync_to_fieldassist(self):
        return
        self.action_get_location()

        username = self.env['ir.config_parameter'].sudo().get_param('fa.api.url')
        password = self.env['ir.config_parameter'].sudo().get_param('fa.api.token')
        today = datetime.today().strftime("%m/%d/%Y")

        print('\n==password',password,username)

        login_url = "https://api.fieldassist.in/api/V3/Product/detailedProduct?lastProductId=9970839&includeUnproductive=false"
        # login_url = "https://api.fieldassist.in/api/V3/Product/detailedProduct"
        
        # FieldAssist Product API
        product_url = "https://api.fieldassist.in/api/V3/Product/list"
        product_url = "https://api.fieldassist.in/api/V3/Visit"

        # Basic Auth with username & password
        # response = requests.get(product_url, auth=('193173', 'MiStBgrRd!2mL(Q^2BSd'))

        params = {
            "fromDate": f"{today}T00:00:00",
            "toDate": f"{today}T23:59:59"
        }
        # params = {
        #     "lastModifiedDate": f"{today}T00:00:00"   # ISO datetime format
        # }
        response = requests.get(product_url, auth=(username, password))

        print("Status:", response.status_code)
        if response.status_code == 200:
            products = response.json()
            for p in products:
                # pass
                print(p, '\n\n==')
                rec_date = p.get("LastModifiedDate", "")[:10]
                print(rec_date)
                print(p['Id'])
                print(p['Name'])
        else:
            print("Error:", response.text)


        # Okay Working
        # login_url = "https://api.fieldassist.in/api/V3/Visit/detailedVisit?lastVisitId=1924724629&includeUnproductive=false"
        # payload = {
        #     "username": "193173",
        #     "password": "MiStBgrRd!2mL(Q^2BSd"
        # }
        # response = requests.get(login_url, auth=('193173', "MiStBgrRd!2mL(Q^2BSd"))

        # print("\n\n=====Got response:", response)
        # # response = requests.get(login_url, headers=payload)
        # token = response.json()

        # print("\n\n=====Got Token:", token)

        # last_product_id = 0
        # all_products = []

    def action_get_location(self):
        response = requests.get("https://ipinfo.io")
        data = response.json()
        loc = data['loc'].split(",")
        latitude, longitude = loc[0], loc[1]
        
        print("📍 IP Address :", data.get("ip"))
        print("🏙️ City       :", data.get("city"))
        print("🗺️ Region     :", data.get("region"))
        print("🇮🇳 Country    :", data.get("country"))
        print("🌐 Latitude   :", latitude)
        print("🌐 Longitude  :", longitude)

        raise UserError("📍 IP Address :" + data.get("ip")+"🏙️ City       :" + data.get("city")+"🗺️ Region     :"+ data.get("region")+"🇮🇳 Country    :"+ data.get("country")+ "🌐 Latitude   :"+ latitude+ "🌐 Longitude  :"+ longitude)