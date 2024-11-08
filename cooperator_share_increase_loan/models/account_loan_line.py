from odoo import models, Command


class AccountLoanLine(models.Model):
    _inherit = "account.loan.line"

    def _move_line_vals(self, account=False):
        self.ensure_one()
        vals = []

        if self.loan_id.loan_type == "interest" and self.loan_id.from_subscription:

            interest_account = self.loan_id.interest_expenses_account_id

            taxes = interest_account.tax_ids
            if taxes:
                tax_values = {
                    "amount_currency": self.interests_amount,
                    "currency_id": self.loan_id.company_id.currency_id.id,
                    "tax_ids": [Command.set(taxes.ids)],
                    "partner_id": self.loan_id.partner_id.id,
                    "account_id": interest_account.id,
                }

                tax_results = taxes.compute_all(
                    self.interests_amount,
                    currency=self.loan_id.company_id.currency_id,
                    partner=self.loan_id.partner_id,
                )

                vals.append(
                    {
                        "account_id": interest_account.id,
                        "credit": 0,
                        "debit": tax_results["total_included"],
                        "tax_ids": [],
                    }
                )

                for tax_vals in tax_results["taxes"]:
                    if tax_vals["amount"]:
                        tax = self.env["account.tax"].browse(tax_vals["id"])
                        vals.append(
                            {
                                "account_id": tax_vals["account_id"],
                                "credit": (
                                    tax_vals["amount"] if tax_vals["amount"] > 0 else 0
                                ),
                                "debit": (
                                    -tax_vals["amount"] if tax_vals["amount"] < 0 else 0
                                ),
                                "tax_line_id": tax_vals["id"],
                                "name": tax.name,
                            }
                        )
            else:
                vals.append(
                    {
                        "account_id": interest_account.id,
                        "credit": 0,
                        "debit": self.interests_amount,
                    }
                )

            vals.append(
                {
                    "account_id": self.loan_id.partner_id.property_account_payable_id.id,
                    "partner_id": self.loan_id.partner_id.id,
                    "credit": self.payment_amount,
                    "debit": 0,
                }
            )

            return vals
        else:
            return super()._move_line_vals(account=account)
