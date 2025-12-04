# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Contact(models.Model):
    _inherit = "res.partner"

    sales_officer_id = fields.Many2one('hr.employee', string='Sales Officer')
    sales_manager_id = fields.Many2one('hr.employee', string='Sales Manager')

class Employee(models.Model):
    _inherit = "hr.employee"

    sales_officer_ids = fields.One2many('res.partner', 'sales_officer_id', string='Sales Officer')
    sales_manager_ids = fields.One2many('res.partner', 'sales_manager_id', string='Sales Manager')
    is_sales_officer = fields.Boolean(string='Is Sales Officer')
    is_sales_manager = fields.Boolean(string='Is Sales Manager')