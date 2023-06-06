# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _compute_base_logo(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        self.logo_url = base_url + "/logo.png"

    coop_email_contact = fields.Char(string="Contact email address for the cooperator")
    subscription_maximum_amount = fields.Float(
        string="Maximum authorised subscription amount"
    )
    default_capital_release_request_payment_term = fields.Many2one(
        comodel_name="account.payment.term",
        string="Default Payment Term",
        help="Default payment term to use for capital release requests",
    )
    default_country_id = fields.Many2one(
        "res.country",
        string="Default country",
        default=lambda self: self.country_id,
    )
    default_lang_id = fields.Many2one("res.lang", string="Default lang")
    allow_id_card_upload = fields.Boolean(string="Allow ID Card upload")
    create_user = fields.Boolean(string="Create user for cooperator", default=False)
    board_representative = fields.Char(string="Board representative name")
    signature_scan = fields.Binary(string="Board representative signature")
    property_cooperator_account = fields.Many2one(
        comodel_name="account.account",
        string="Cooperator Account",
        domain=[
            ("internal_type", "=", "receivable"),
            ("deprecated", "=", False),
        ],
        help="This account will be"
        " the default one as the"
        " receivable account for the"
        " cooperators",
    )
    unmix_share_type = fields.Boolean(
        string="Unmix share type",
        default=True,
        help="If checked, A cooperator will be"
        " authorised to have only one type"
        " of share",
    )
    display_logo1 = fields.Boolean(string="Display logo 1")
    display_logo2 = fields.Boolean(string="Display logo 2")
    bottom_logo1 = fields.Binary(string="Bottom logo 1")
    bottom_logo2 = fields.Binary(string="Bottom logo 2")
    logo_url = fields.Char(string="logo url", compute="_compute_base_logo")
    display_data_policy_approval = fields.Boolean(
        help="Choose to display a data policy checkbox on the cooperator"
        " website form."
    )
    data_policy_approval_required = fields.Boolean(
        string="Is data policy approval required?"
    )
    data_policy_approval_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to approve data policy.",
    )
    display_internal_rules_approval = fields.Boolean(
        help="Choose to display an internal rules checkbox on the"
        " cooperator website form."
    )
    internal_rules_approval_required = fields.Boolean(
        string="Is internal rules approval required?"
    )
    internal_rules_approval_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to approve internal rules.",
    )
    display_financial_risk_approval = fields.Boolean(
        help="Choose to display a financial risk checkbox on the"
        " cooperator website form."
    )
    financial_risk_approval_required = fields.Boolean(
        string="Is financial risk approval required?"
    )
    financial_risk_approval_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to approve financial risk.",
    )
    display_generic_rules_approval = fields.Boolean(
        help="Choose to display generic rules checkbox on the"
        " cooperator website form."
    )
    generic_rules_approval_required = fields.Boolean(
        string="Is generic rules approval required?"
    )
    generic_rules_approval_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to approve the generic rules.",
    )
    send_certificate_email = fields.Boolean(
        string="Send certificate email", default=True
    )
    cooperator_confirmation_mail_template = fields.Many2one(
        comodel_name="mail.template",
        string="Share confirmation email template",
        domain="[('model', '=', 'subscription.request')]",
    )
    send_confirmation_email = fields.Boolean(
        string="Send confirmation email", default=True
    )
    cooperator_capital_release_mail_template = fields.Many2one(
        comodel_name="mail.template",
        string="Capital release email template",
        domain="[('model', '=', 'account.move')]",
    )
    send_capital_release_email = fields.Boolean(
        string="Send Capital Release email", default=True
    )
    cooperator_waiting_list_mail_template = fields.Many2one(
        comodel_name="mail.template",
        string="Waiting list email template",
        domain="[('model', '=', 'subscription.request')]",
    )
    send_waiting_list_email = fields.Boolean(
        string="Send Waiting List email", default=True
    )
    send_share_transfer_email = fields.Boolean(
        string="Send Share Transfer Email", default=True
    )
    send_share_update_email = fields.Boolean(
        string="Send Share Update Email", default=True
    )

    @api.onchange("data_policy_approval_required")
    def onchange_data_policy_approval_required(self):
        if self.data_policy_approval_required:
            self.display_data_policy_approval = True

    @api.onchange("internal_rules_approval_required")
    def onchange_internal_rules_approval_required(self):
        if self.internal_rules_approval_required:
            self.display_internal_rules_approval = True

    @api.onchange("financial_risk_approval_required")
    def onchange_financial_risk_approval_required(self):
        if self.financial_risk_approval_required:
            self.display_financial_risk_approval = True

    @api.onchange("generic_rules_approval_required")
    def onchange_generic_rules_approval_required(self):
        if self.generic_rules_approval_required:
            self.display_generic_rules_approval = True

    @api.model
    def create(self, vals):
        result = super().create(vals)
        # The ignore_list is populated such that, if the user defines a template
        # they want to use during company creation, that choice doesn't get
        # overridden. The boolean check exists because, when creating a company
        # from the UI, all empty fields are defined with no value.
        result._setup_default_cooperator_mail_templates(
            ignore_list=[key for key, val in vals.items() if val]
        )
        return result

    @api.model
    def _get_cooperator_mail_template_fields(self):
        return {
            "cooperator_confirmation_mail_template": "cooperator.email_template_confirmation",
            "cooperator_capital_release_mail_template": (
                "cooperator.email_template_release_capital"
            ),
            "cooperator_waiting_list_mail_template": "cooperator.email_template_waiting_list",
        }

    def _get_default_cooperator_mail_template(self, xmlid, copy=True):
        """Get the mail template from its xmlid and either return it or return
        a copy of it.
        """
        self.ensure_one()
        try:
            template = self.env.ref(xmlid)
        except ValueError:
            return False
        if copy:
            result = template.copy()
            # Set name to 'Company - Template' instead of 'Template (copy)'.
            result.name = "{} - {}".format(self.name, template.name)
            return result
        else:
            return template

    def _assign_default_cooperator_mail_template(
        self, field, xmlid, copy=True, override=False
    ):
        for company in self:
            if override or not getattr(company, field):
                company.write(
                    {
                        field: company._get_default_cooperator_mail_template(
                            xmlid, copy=copy
                        ).id
                    }
                )

    def _setup_default_cooperator_mail_templates(
        self, copy=True, override=False, ignore_list=None
    ):
        if ignore_list is None:
            ignore_list = []
        for field, xmlid in self._get_cooperator_mail_template_fields().items():
            if field in ignore_list:
                continue
            self._assign_default_cooperator_mail_template(
                field, xmlid, copy=copy, override=override
            )
