from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_income_increase_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string="Income Account for Share Increase",
        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used when validating a share increase subscription request instead of the default income account"
    )
