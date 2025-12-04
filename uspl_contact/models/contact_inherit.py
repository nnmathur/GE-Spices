# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Contact(models.Model):
    _inherit = "res.partner"

    Id = fields.Integer(string='Id', help='Id of the distributor.')
    SecondaryEmailId = fields.Char(string='Secondary Email Id', help='Secondary EmailId Id')
    Manager = fields.Char(string='Manager', help='Name of The contact Person')
    DistributorERPId = fields.Char(string='Distributorerpid', help='ERP or SAP id for the distributor.')
    LocalName = fields.Char(string='Local Name', help='Alternate/Local for the distributor.')
    Address = fields.Char(string='Address', help='Address of the Location of the distributor')
    Place = fields.Char(string='Place', help='Location/City of the distributor')
    # GSTIN = fields.Char(string='Gstin', help='GSTIN (Goods and Service Tax Identity Number) No.')
    TIN = fields.Char(string='Tin', help='TIN No.')
    # Pincode = fields.Char(string='Pincode', help='Pincode of the Locationof the distributor')
    Region = fields.Char(string='Region', help='Region of the distributor')
    Zone = fields.Char(string='Zone', help='Zone of the distributor')
    ZoneErpId = fields.Char(string='Zone Erp Id', help='Erp ID of the zone')
    # GeoLevel5Name = fields.Char(string='Geolevel5Name', help='Level 5 geo in the hierarchy of the concerned zone')
    # GeoLevel5ErpId = fields.Char(string='Geolevel5Erpid', help='Erp ID of the Level 5 geo')
    # GeoLevel6Name = fields.Char(string='Geolevel6Name', help='Level 6 geo in the hierarchy of the concerned zone')
    # GeoLevel6ErpId = fields.Char(string='Geolevel6Erpid', help='Erp ID of the Level 6 geo')
    # GeoLevel7Name = fields.Char(string='Geolevel7Name', help='Level 7 geo in the hierarchy of the concerned zone')
    # GeoLevel7ErpId = fields.Char(string='Geolevel7Erpid', help='Erp ID of the Level 7 geo')
    # IsDeactive = fields.Boolean(string='Isdeactive', help='Set if Distributor is deactive.. (Only for Updating) This Data will be Ignored if used during Distributor Creation')
    ParentERPId = fields.Char(string='Parent ERP Id', help='ERP or SAP id for the Super stockist. This data is used while creating sub stockist and will be ignored while listing')
    DistributorCategory = fields.Char(string='Distributor Category', help='Reference from Company defined Category List')
    DistributorGrade = fields.Char(string='Distributor Grade', help='Distributor grade should be valid Possible values are -1. Urban 2 Semi Urban 3. Metro 4. Non Metro 5. Rural.')
    DistributorChannelErpId = fields.Char(string='Distributor Channel Erp Id', help='Reference from Company defined Channel List Channel Erp Id of the distributor')
    # PANNumber = fields.Char(string='Pannumber', help='PAN Number of the distributor')
    FSSAINumber = fields.Char(string='FSSAI Number', help='FSSAI Number of the distributor')
    UdyamNumber = fields.Char(string='Udyam Number')
    FSSAIExiryDate = fields.Date(string='Fssai Expiry Date', help='FSSAI Expiry of the distributor')
    BankName = fields.Char(string='Bank Name', help='Bank Name of the distributor')
    BankAccountNumber = fields.Char(string='Bank Account Number', help='Bank Account Number of the distributor')
    BankIFSCCode = fields.Char(string='Bank IFSC Code', help='Bank IFSC Code of the distributor')
    # AttributeText1 = fields.Char(string='Attributetext1', help='Additional attribute of the distributor')
    # AttributeText2 = fields.Char(string='Attributetext2', help='Additional attribute of the distributor')
    # AttributeText3 = fields.Char(string='Attributetext3', help='Additional attribute of the distributor')
    # AttributeBoolean1 = fields.Boolean(string='Attributeboolean1', help='Additional attribute of the distributor')
    # AttributeBoolean2 = fields.Boolean(string='Attributeboolean2', help='Additional attribute of the distributor')
    # AttributeNumber1 = fields.Char(string='Attributenumber1', help='Additional attribute of the distributor')
    # AttributeNumber2 = fields.Char(string='Attributenumber2', help='Additional attribute of the distributor')
    # AttributeDate1 = fields.Date(string='Attributedate1', help='Additional attribute of the distributor')
    # AttributeDate2 = fields.Date(string='Attributedate2', help='Additional attribute of the distributor')
    StockistType = fields.Char(string='Stock Ist Type', help='Distributor StockistType should be valid Possible values are 0. Unknown 1. Stockist 2. Super Stockist 3. Sub Stockist 4. Mega Stockist')
    DistributorChannelIdErpId = fields.Char(string='Distributorchanneliderpid', help='Channel Erp Id of the distributor Channel')
    DistributorSegmentationIdErpId = fields.Char(string='Distributor Segmentation Id ERP Id', help='Segmentation Erp Id of the distributor Channel')
    State = fields.Char(string='State', help='State of the distributor')
    PlaceOfSupply = fields.Char(string='Place Of Supply', help='Place Of Supply')
    WarehouseId = fields.Char(string='Warehouse Id', help='Warehouse Id')
    WarehouseState = fields.Char(string='Warehouse State', help='Warehouse State')
    WarehouseCity = fields.Char(string='Warehouse City', help='Warehouse City')
    WarehouseAddress = fields.Char(string='Warehouse Address', help='Warehouse Address')
    WarehouseName = fields.Char(string='Warehouse Name', help='Warehouse Name')
    WarehouseErpId = fields.Char(string='Warehouse ErpId', help='Warehouse ErpId')
    SecurityDeposit = fields.Char(string='Security Deposit', help='Distributor Security Deposit of the distributor')
    DDNumber = fields.Char(string='DD Number', help='Distributor DD Number of the distributor')
    DateOfPayment = fields.Date(string='Distributor Date Of Payment', help='Distributor Date Of Payment of the distributor')
    PaymentMode = fields.Char(string='Distributor Payment Mode', help='Distributor Payment Mode of the distributor')
    IsGSTRegistered = fields.Boolean(string='IsGST Registered', help='IsGST Registered Mode of the distributor')
    IntransitPeriod = fields.Integer(string='Intransit Period', help='IntransitPeriod == Days of Transit in which the Shipment from the Seller reaches the DB')
    CreditDuration = fields.Integer(string='Credit Duration', help='Credit Duration')
    CreditValue = fields.Char(string='Credit Value', help='Credit Value')
    CreditInvoiceCount = fields.Integer(string='Credit Invoice Count', help='Credit Invoice Count')
    # Latitude = fields.Char(string='Latitude', help='Latitude')
    # Longitude = fields.Char(string='Longitude', help='Longitude')
    Aadhar = fields.Char(string='Aadhar', help='Aadhar')
    DOB = fields.Date(string='DOB', help='DOB')
    OwnerName = fields.Char(string='Owner Name', help='OwnerName')
    OwnerNo = fields.Char(string='Owner No', help='OwnerNo')
    CashDiscountLimit = fields.Char(string='Cash Discount Limit', help='CashDiscountLimit')

    payment_mode = fields.Selection([('cash', 'Cash'),('online', 'Online')], string='Distributor Payment Mode', help='Distributor Payment Mode of the distributor')
    cust_contact_type = fields.Selection([('distributors', 'WD Distributors (Customers)'),('super_stockist', 'Super Stockist'),('HORECA', ' HORECA')], string='Contact Type')

    beat_ids = fields.One2many('beat.beat', 'distributor_id', string='Beats')
    outlet_ids = fields.One2many('outlet.outlet', 'distributor_id', string='Outlets')

class Beat(models.Model):
    _name = 'beat.beat'

    distributor_id = fields.Many2one('res.partner', string='Distributor Id')
    name = fields.Char(string='Beat Name')

class Outlet(models.Model):
    _name = 'outlet.outlet'

    distributor_id = fields.Many2one('res.partner', string='Distributor Id')
    beat_id = fields.Many2one('beat.beat', string='Beat Name', domain="[('distributor_id', '=', distributor_id)]")
    name = fields.Char(string='Outlet Name')