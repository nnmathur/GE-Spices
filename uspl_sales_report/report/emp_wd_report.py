# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import io
import xlsxwriter
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from itertools import groupby
from operator import attrgetter


class EMPPromarySales(models.TransientModel):
    _name = 'emp.primary.sales.wiz'
    _description = 'Employe Primary Excel Report Wizard'

    report_file = fields.Binary('Download Report')
    report_name = fields.Char('Report Name', default='report.xlsx')
    period_from = fields.Date("Period From")
    period_to = fields.Date("Period To")

    def generate_excel_report(self):
        output = io.BytesIO()
        # Create an Excel workbook and worksheet
        workbook = xlsxwriter.Workbook(output)
        centered_format = workbook.add_format({'align': 'left', 'valign': 'vcenter'})
        right_format = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'num_format': '0.00'})
        right_format_head = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'num_format': '0.00','bold': True, 'font_size': '12px'})
        centered_format_head = workbook.add_format({'align': 'center', 'valign': 'vcenter','bold': True, 'font_size': '12px'})
        head_main = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '14px', 'bg_color': '#DEE6EF'})
        head = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '12px', 'bg_color': '#DEE6EF'})
        head2 = workbook.add_format({'align': 'left', 'bold': True, 'font_size': '11px'})
        head_right = workbook.add_format({'align': 'right', 'bold': True, 'font_size': '11px'})

        title = 'Start From ' +  str(self.period_from.strftime("%b %d, %Y")) + ' To ' + str(self.period_to.strftime("%b %d, %Y"))
        worksheet = workbook.add_worksheet()
        worksheet.merge_range('A1:R1', 'Employe Primary Sales Report', head_main)
        worksheet.merge_range('A2:R2', title, head)
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 30)
        worksheet.set_column(5, 5, 30)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 15)
        worksheet.set_column(10, 10, 15)
        worksheet.set_column(11, 11, 15)
        worksheet.set_column(12, 12, 15)
        worksheet.set_column(13, 13, 15)
        worksheet.set_column(14, 14, 15)
        worksheet.set_column(15, 15, 22)
        worksheet.set_column(16, 16, 22)
        worksheet.set_column(17, 17, 22)
        worksheet.set_column(18, 18, 20)
        
        # Write some data to the worksheet
        worksheet.write(2, 0, 'State', head2)
        worksheet.write(2, 1, 'District', head2)
        worksheet.write(2, 2, 'Town', head2)
        worksheet.write(2, 3, 'Employee', head2)
        # worksheet.write(2, 4, 'Month', head2)
        worksheet.write(2, 4, 'Product Category', head2)
        worksheet.write(2, 5, 'Product', head2)
        worksheet.write(2, 6, 'Weight (packing)', head_right)
        worksheet.write(2, 7, 'MRP', head_right)
        worksheet.write(2, 8, 'Quantity (KG)', head_right)
        worksheet.write(2, 9, 'Value', head_right)
        worksheet.write(2, 10, 'WD', head_right)
        worksheet.write(2, 11, 'SS', head_right)
        worksheet.write(2, 12, ' HORECA', head_right)
        worksheet.write(2, 13, 'LM', head_right)
        worksheet.write(2, 14, 'LYSM', head_right)
        worksheet.write(2, 15, 'Growth Over LM (+/-)', head_right)
        worksheet.write(2, 16, 'Growth Over LYSM (+/-)', head_right)
        worksheet.write(2, 17, 'YTD', head_right)
        lm_dt = self.period_from.replace(day=1) - relativedelta(months=1)
        lm_dtt = self.period_from.replace(day=1) - timedelta(days=1)
        lysm_dt = self.period_from.replace(day=1) - relativedelta(years=1)
        lysm_dtt = lysm_dt + relativedelta(months=1) - timedelta(days=1)
        # sale_order_ids = self.env['sale.order'].search([('delivery_status', 'in', ['full','partial'])], order='create_date asc').filtered(lambda l: self.period_from.replace(day=1) <= l.create_date.date() <= self.period_to)
        sale_order_ids = self.env['sale.order'].search([('state', 'in', ['done', 'sale'])], order='create_date asc').filtered(lambda l: self.period_from.replace(day=1) <= l.create_date.date() <= self.period_to)
        lm_sale_order_ids = self.env['sale.order'].search([('state', 'in', ['done', 'sale'])], order='create_date asc').filtered(lambda l: lm_dt <= l.create_date.date() <= lm_dtt)
        lysm_sale_order_ids = self.env['sale.order'].search([('state', 'in', ['done', 'sale'])], order='create_date asc').filtered(lambda l: lysm_dt <= l.create_date.date() <= lysm_dtt)
        sales_person_ids = sale_order_ids.mapped('user_id')

        new_row1 = 3

        total_qty = 0
        total_value = 0
        total_wd = 0
        total_ss = 0
        total_horeca = 0
        total_lm = 0
        total_lysm = 0
        total_gr_lm = 0
        total_gr_lysm = 0

        for emp in sales_person_ids:
            worksheet.write(new_row1, 3, emp.name, centered_format)
            emp_so_ids = sale_order_ids.filtered(lambda l: l.user_id.id == emp.id)
            order_lines = emp_so_ids.mapped('order_line')
            products = order_lines.mapped('product_id')
            lm_emp_so_ids = lm_sale_order_ids.filtered(lambda l: l.user_id.id == emp.id)
            lm_order_lines = lm_emp_so_ids.mapped('order_line')
            lysm_emp_so_ids = lysm_sale_order_ids.filtered(lambda l: l.user_id.id == emp.id)
            lysm_order_lines = lysm_emp_so_ids.mapped('order_line')
            for product in products:
                total_line = order_lines.filtered(lambda l: l.product_id.id == product.id)
                lm_total_line = lm_order_lines.filtered(lambda l: l.product_id.id == product.id)
                lysm_total_line = lysm_order_lines.filtered(lambda l: l.product_id.id == product.id)
                wd = total_line.filtered(lambda l: l.order_id.partner_id.cust_contact_type == 'distributors')
                ss = total_line.filtered(lambda l: l.order_id.partner_id.cust_contact_type == 'super_stockist')
                horeca = total_line.filtered(lambda l: l.order_id.partner_id.cust_contact_type == 'HORECA')
                
                worksheet.write(new_row1, 4, product.categ_id.display_name, centered_format)
                worksheet.write(new_row1, 5, product.display_name, centered_format)
                worksheet.write(new_row1, 6, product.weight, right_format)
                worksheet.write(new_row1, 7, product.mrp, right_format)
                worksheet.write(new_row1, 8, sum(total_line.mapped('product_uom_qty')), right_format)
                worksheet.write(new_row1, 9, round(sum(total_line.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 10, round(sum(wd.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 11, round(sum(ss.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 12, round(sum(horeca.mapped('price_total'))), right_format)

                worksheet.write(new_row1, 13, round(sum(lm_total_line.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 14, round(sum(lysm_total_line.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 15, round(sum(total_line.mapped('price_total')) - sum(lm_total_line.mapped('price_total'))), right_format)
                worksheet.write(new_row1, 16, round(sum(total_line.mapped('price_total')) - sum(lysm_total_line.mapped('price_total'))), right_format)
                new_row1 += 1

                total_qty += round(sum(total_line.mapped('product_uom_qty')))
                total_value += round(sum(total_line.mapped('price_total')))
                total_wd += round(sum(wd.mapped('price_total')))
                total_ss += round(sum(ss.mapped('price_total')))
                total_horeca += round(sum(horeca.mapped('price_total')))
                
                total_lm += round(sum(lm_total_line.mapped('price_total')))
                total_lysm += round(sum(lysm_total_line.mapped('price_total')))
                total_gr_lm += round(sum(total_line.mapped('price_total')) - sum(lm_total_line.mapped('price_total')))
                total_gr_lysm += round(sum(total_line.mapped('price_total')) - sum(lysm_total_line.mapped('price_total')))
                
        worksheet.write(new_row1, 0, 'Total', head)
        worksheet.write(new_row1, 8, round(total_qty), right_format_head)
        worksheet.write(new_row1, 9, round(total_value), right_format_head)

        worksheet.write(new_row1, 10, round(total_wd), right_format_head)
        worksheet.write(new_row1, 11, round(total_ss), right_format_head)
        worksheet.write(new_row1, 12, round(total_horeca), right_format_head)
        
        worksheet.write(new_row1, 13, round(total_lm), right_format_head)
        worksheet.write(new_row1, 14, round(total_lysm), right_format_head)
        worksheet.write(new_row1, 15, round(total_gr_lm), right_format_head)
        worksheet.write(new_row1, 16, round(total_gr_lysm), right_format_head)

        # Close the workbook to finalize it
        workbook.close()

        # Get the value of the BytesIO buffer
        output.seek(0)
        report_data = output.read()

        # Encode to base64 so it can be stored in the Binary field
        report_base64 = base64.b64encode(report_data)

        # Save the file to the wizard's binary field
        self.write({
            'report_file': report_base64,
            'report_name': 'Employe Primary Sales Report.xlsx'
        })

        # Return action to download the file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=report_file&filename={self.report_name}&download=true',
            'target': 'self',
        }


