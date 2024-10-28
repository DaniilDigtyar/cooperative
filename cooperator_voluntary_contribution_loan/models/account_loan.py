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
