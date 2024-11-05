# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    type = fields.Selection(
        selection_add=[
            ("increase_remunerated", "Increase number of share and remunerated"),
        ],
    )
    loan_id = fields.Many2one("account.loan", string="Associated Loan", copy=False)
    loan_interest_rate = fields.Float(
        string="Loan Interest Rate",
        digits=(6, 2),
        help="Interest rate for the associated loan",
    )
    loan_min_periods = fields.Integer(
        string="Loan Periods", help="Minimum number of periods for the loan"
    )
    method_period = fields.Integer(
        string="Period Length",
        default=1,
        help="State here the time between 2 depreciations, in months",
        required=True,
    )
    loan_journal_id = fields.Many2one(
        "account.journal",
        string="Loan Journal",
        help="Journal where the loan will be created",
    )
    interest_expenses_account_id = fields.Many2one(
        "account.account",
        string="Interest Expenses Account",
        help="Account where the interests will be assigned to",
    )
    customize_loan = fields.Boolean(
        string="Customize Loan", help="Check to customize loan details"
    )

    @api.onchange("type", "share_product_id")
    def _onchange_type(self):
        if self.type == "increase_remunerated" and self.share_product_id:
            product = self.share_product_id
            self.loan_interest_rate = product.loan_interest_rate
            self.loan_journal_id = product.loan_journal_id
            self.loan_min_periods = product.loan_min_periods
            self.method_period = product.method_period
            self.interest_expenses_account_id = product.interest_expenses_account_id
        else:
            self.loan_interest_rate = False
            self.loan_journal_id = False
            self.loan_min_periods = False
            self.method_period = False
            self.interest_expenses_account_id = False

    def create_permanent_loan(self):
        self.ensure_one()
        if self.type == "increase_remunerated" and not self.loan_id:
            product = self.share_product_id
            invoice = self.env["account.move"].search(
                [
                    ("subscription_request", "=", self.id),
                    ("state", "=", "posted"),
                ],
                limit=1,
            )

            if not invoice:
                raise UserError(_("No posted invoice found for this subscription"))

            # Get the same account used in invoice
            account = (
                product.property_account_income_increase_id
                or product.categ_id.property_account_income_increase_categ_id
            )

            if not account:
                raise UserError(
                    _(
                        "Please define income account for this product:"
                        ' "{name}" (id: {id}) - or for its category: "{category}".'
                    ).format(
                        name=product.name, id=product.id, category=product.categ_id.name
                    )
                )

            loan_vals = {
                "name": "/",
                "partner_id": self.partner_id.id or product.partner_id.id,
                "company_id": self.company_id.id or product.company_id.id,
                "journal_id": self.loan_journal_id.id or product.loan_journal_id.id,
                "loan_type": "interest",
                "loan_amount": self.subscription_amount,
                "rate": self.loan_interest_rate or product.loan_interest_rate,
                "periods": self.loan_min_periods or product.loan_min_periods,
                "min_periods": self.loan_min_periods or product.loan_min_periods,
                "method_period": self.method_period or product.method_period,
                "is_permanent": True,
                "short_term_loan_account_id": account.id,
                "interest_expenses_account_id": self.interest_expenses_account_id.id
                or product.interest_expenses_account_id.id,
                "from_subscription": True,
                "state": "posted",
            }
            loan = self.env["account.loan"].create(loan_vals)
            self.loan_id = loan.id
            loan.start_date = fields.Date.today()
            loan._compute_draft_lines()

            # Relate invoice with loan
            invoice.write({"loan_id": loan.id})

            return loan

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") == "paid":
            for subscription in self:
                if (
                    subscription.type == "increase_remunerated"
                    and not subscription.loan_id
                ):
                    _logger.info(
                        "Creating loan after subscription paid: %s", subscription.id
                    )
                    subscription.create_permanent_loan()
                    if subscription.loan_id:
                        subscription.loan_id.compute_lines()
                        _logger.info(
                            "Loan created and computed: %s", subscription.loan_id.id
                        )
        return res

    @api.model
    def _adapt_create_vals_and_membership_from_partner(self, vals, partner):
        res = super()._adapt_create_vals_and_membership_from_partner(vals, partner)

        if vals.get("type") == "increase_remunerated":
            vals["type"] = "increase"

        return res
