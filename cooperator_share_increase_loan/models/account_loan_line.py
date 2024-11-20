from odoo import models, Command, _


class AccountLoanLine(models.Model):
    _inherit = "account.loan.line"

    def view_process_values_custom(self):
        """Computes the annuity and returns the result with custom context"""
        self.ensure_one()
        if self.loan_id.loan_type == "interest" and self.loan_id.from_subscription:
            self = self.with_context(use_custom_move_line_vals=True)
        if self.is_leasing:
            self._generate_invoice()
        else:
            self._generate_move()
        return self.view_account_values()

    def _move_line_vals(self, account=False):
        self.ensure_one()
        vals = []

        if self.env.context.get('use_custom_move_line_vals'):
            if self.loan_id.loan_type == "interest" and self.loan_id.from_subscription:
                interest_account = self.loan_id.interest_expenses_account_id
                taxes = interest_account.tax_ids
                if taxes:
                    tax_results = taxes.compute_all(
                        self.interests_amount,
                        currency=self.loan_id.currency_id,
                        quantity=1.0,
                        product=None,
                        partner=self.loan_id.partner_id,
                    )

                    tax_values = {
                        "name": "Loan interest",
                        "amount_currency": self.interests_amount,
                        "currency_id": self.loan_id.company_id.currency_id.id,
                        "tax_ids": [Command.set(taxes.ids)],
                        "account_id": interest_account.id,
                        "debit": tax_results["total_included"],
                        "credit": 0.0,
                    }
                    vals.append(tax_values)

                    partner = self.loan_id.partner_id.with_company(self.loan_id.company_id)
                    balance_line = {
                        "name": "Interest payment",
                        "amount_currency": -tax_results["total_included"],
                        "currency_id": self.loan_id.company_id.currency_id.id,
                        "partner_id": self.loan_id.partner_id.id,
                        "account_id": partner.property_account_payable_id.id,
                        "debit": 0.0,
                        "credit": tax_results["total_included"],
                    }
                    vals.append(balance_line)
                    return vals
        else:
            return super()._move_line_vals(account=account)
