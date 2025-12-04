from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fa_api_url = fields.Char(string="User Name")
    fa_api_token = fields.Char(string="Password")

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('fa.api.url', self.fa_api_url)
        self.env['ir.config_parameter'].sudo().set_param('fa.api.token', self.fa_api_token)

    def get_values(self):
        res = super().get_values()
        res.update(
            fa_api_url=self.env['ir.config_parameter'].sudo().get_param('fa.api.url', ''),
            fa_api_token=self.env['ir.config_parameter'].sudo().get_param('fa.api.token', ''),
        )
        return res
