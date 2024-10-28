# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    loan_id = fields.Many2one("account.loan", string="Associated Loan")
    loan_interest_rate = fields.Float(
        string="Loan Interest Rate",
        digits=(6, 2),
        help="Interest rate for the associated loan",
    )
    loan_min_periods = fields.Integer(
        string="Loan Periods", help="Minimum number of periods for the loan"
    )
    loan_journal_id = fields.Many2one(
        "account.journal",
        string="Loan Journal",
        help="Journal where the loan will be created",
    )
    short_term_loan_account_id = fields.Many2one(
        "account.account",
        string="Short Term Loan Account",
        help="Account that will contain the pending amount on short term",
    )
    long_term_loan_account_id = fields.Many2one(
        "account.account",
        string="Long Term Loan Account",
        help="Account that will contain the pending amount on Long term",
    )
    interest_expenses_account_id = fields.Many2one(
        "account.account",
        string="Interest Expenses Account",
        help="Account where the interests will be assigned to",
    )
    type = fields.Selection(
        selection_add=[
            ("increase_remunerated", "Increase number of share and remunerated"),
        ],
    )
    customize_loan = fields.Boolean(
        string="Customize Loan", help="Check to customize loan details"
    )

    @api.constrains("type", "is_voluntary")
    def _check_increase_remunerated(self):
        for record in self:
            if record.type == "increase_remunerated" and not record.is_voluntary:
                raise ValidationError(
                    _(
                        "You can only select 'Increase number of share and remunerated' for voluntary subscriptions."
                    )
                )

    @api.onchange("is_voluntary")
    def _onchange_is_voluntary(self):
        if not self.is_voluntary and self.type == "increase_remunerated":
            self.type = "increase"

    @api.onchange("type", "share_product_id")
    def _onchange_type_remunerated(self):
        if self.type == "increase_remunerated" and self.share_product_id:
            product = self.share_product_id
            self.loan_interest_rate = product.loan_interest_rate
            self.loan_journal_id = product.loan_journal_id
            self.loan_min_periods = product.loan_min_periods
            self.short_term_loan_account_id = product.short_term_loan_account_id
            self.long_term_loan_account_id = product.long_term_loan_account_id
            self.interest_expenses_account_id = product.interest_expenses_account_id
        else:
            self.loan_interest_rate = False
            self.loan_journal_id = False
            self.loan_min_periods = False
            self.short_term_loan_account_id = False
            self.long_term_loan_account_id = False
            self.interest_expenses_account_id = False

    def create_permanent_loan(self):
        self.ensure_one()
        if self.type == "increase_remunerated" and not self.loan_id:
            product = self.share_product_id
            loan_vals = {
                "name": f"Loan for {self.partner_id.name} - {self.id}",
                "partner_id": self.partner_id.id or product.partner_id.id,
                "company_id": self.company_id.id or product.company_id.id,
                "journal_id": self.loan_journal_id.id or product.loan_journal_id.id,
                "loan_type": "interest",
                "loan_amount": self.subscription_amount,
                "rate": self.loan_interest_rate or product.loan_interest_rate,
                "periods": self.loan_min_periods or product.loan_min_periods,
                "min_periods": self.loan_min_periods or product.loan_min_periods,
                "is_permanent": True,
                "short_term_loan_account_id": self.short_term_loan_account_id.id
                or product.short_term_loan_account_id.id,
                "long_term_loan_account_id": self.long_term_loan_account_id.id
                or product.long_term_loan_account_id.id,
                "interest_expenses_account_id": self.interest_expenses_account_id.id
                or product.interest_expenses_account_id.id,
            }
            loan = self.env["account.loan"].create(loan_vals)
            self.loan_id = loan.id

    def validate_subscription_request(self):
        if self.type == "increase_remunerated":
            loan = self.create_permanent_loan()
            if loan:
                loan.compute_lines()
            self.write({"state": "done"})
            return True
        else:
            return super(SubscriptionRequest, self).validate_subscription_request()
