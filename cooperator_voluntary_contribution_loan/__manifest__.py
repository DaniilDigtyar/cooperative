##############################################################################
#
# Copyright (c) 2024 Som IT Cooperatiu SCCL
# Copyright (c) 2024 Nicolás Ramos (https://somit.coop)
#
# The licence is in the file __manifest__.py
##############################################################################
{
    "name": "Cooperator Voluntary Contribution Loan",
    "version": "16.0.1.0.0",
    "author": "Som IT Cooperatiu SCCL, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/cooperative",
    "license": "AGPL-3",
    "summary": "Adds a loan to the voluntary contribution requests",
    "category": "Cooperative management",
    "depends": [
        "cooperator_voluntary_contribution",
        "account_loan_permanent",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/subscription_request_views.xml",
    ],
    "installable": True,
    "maintainers": ["nramosdev"],
    "development_status": "Alpha",
}
