# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountLoan(models.Model):
    _inherit = "account.loan"

    subscription_request_id = fields.Many2one(
        "subscription.request", string="Subscription Request"
    )
    from_subscription = fields.Boolean(
        string="Created from Subscription",
        default=False,
        help="Indicates if this loan was created from a subscription request",
    )

    def _generate_loan_entries(self, date):
        """
        Generate the moves of unfinished loans before date
        :param date:
        :return:
        """
        res = []
        for record in self.search(
            [("state", "=", "posted"), ("is_leasing", "=", False)]
        ):
            lines = record.line_ids.filtered(
                lambda r: r.date <= date and not r.move_ids
            )
            lines = lines.with_context(use_custom_move_line_vals=True)
            res += lines._generate_move()
        return res
