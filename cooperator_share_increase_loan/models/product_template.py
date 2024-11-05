# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    loan_interest_rate = fields.Float(
        string="Loan Interest Rate",
        digits=(6, 2),
        help="Interest rate for the associated loan",
    )
    loan_journal_id = fields.Many2one(
        "account.journal",
        string="Loan Journal",
        help="Journal where the loan will be created",
    )
    loan_min_periods = fields.Integer(
        string="Loan Periods", help="Minimum number of periods for the loan"
    )
    method_period = fields.Integer(
        string="Period Length",
        default=1,
        help="State here the time between 2 depreciations, in months",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    interest_expenses_account_id = fields.Many2one(
        "account.account",
        string="Interests account",
        help="Account where the interests will be assigned to",
        domain="[('company_id', 'in', [current_company_id, False]), ('deprecated', '=', False)]",
    )
    method_period = fields.Integer(
        string="Period Length",
        default=1,
        help="State here the time between 2 depreciations, in months",
        required=True,
    )
