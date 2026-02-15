# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FinanceAccount(models.Model):
    """
    Represents any money source: cashbox, bank account, card, or wallet.
    Each account MUST be linked to a Chart of Accounts entry and a Journal.
    The currency is enforced to match the linked CoA account's currency.
    """
    _name = 'finance.account'
    _description = 'Finance Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Account Name',
        required=True,
        tracking=True,
        help='Display name of the financial account.',
    )
    code = fields.Char(
        string='Code',
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        help='Unique auto-generated code for the account.',
    )
    type = fields.Selection(
        selection=[
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('card', 'Card'),
            ('wallet', 'Wallet'),
        ],
        string='Account Type',
        required=True,
        default='cash',
        tracking=True,
        help='Type of financial account.',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True,
        help='Currency used for this account. Must match the Chart of Account currency.',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company that owns this account.',
    )
    branch_id = fields.Many2one(
        comodel_name='res.company',
        string='Branch',
        help='Optional branch for multi-branch setups.',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, this account will be hidden from lists.',
    )
    allow_negative = fields.Boolean(
        string='Allow Negative Balance',
        default=False,
        tracking=True,
        help='If checked, transactions that result in a negative balance will be allowed.',
    )

    # -------------------------------------------------------------------------
    # Accounting Integration Fields (required)
    # -------------------------------------------------------------------------
    account_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Chart of Account',
        required=True,
        tracking=True,
        help='The chart of accounts entry linked to this treasury account. '
             'This is the main side (debit for income / credit for expense) '
             'of every journal entry. The currency must match.',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Accounting Journal',
        required=True,
        tracking=True,
        help='Journal used to create accounting entries for this treasury account.',
    )

    # -------------------------------------------------------------------------
    # Balance & Transactions
    # -------------------------------------------------------------------------
    balance = fields.Monetary(
        string='Balance',
        compute='_compute_balance',
        currency_field='currency_id',
        help='Live balance from the linked Chart of Account '
             '(sum of debit − credit on all posted journal items).',
    )
    transaction_ids = fields.One2many(
        comodel_name='finance.transaction',
        inverse_name='account_id',
        string='Transactions',
    )
    transaction_count = fields.Integer(
        string='Transaction Count',
        compute='_compute_transaction_count',
    )
    notes = fields.Html(
        string='Notes',
        help='Internal notes about this account.',
    )

    # -------------------------------------------------------------------------
    # ONCHANGE
    # -------------------------------------------------------------------------

    @api.onchange('account_account_id')
    def _onchange_account_account_id(self):
        """Auto-fill currency from the linked Chart of Account."""
        if self.account_account_id and self.account_account_id.currency_id:
            self.currency_id = self.account_account_id.currency_id
        elif self.account_account_id:
            # If CoA has no specific currency, use the company currency
            self.currency_id = self.env.company.currency_id

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------

    @api.constrains('currency_id', 'account_account_id')
    def _check_currency_match(self):
        """Ensure the treasury account currency matches the Chart of Account currency."""
        for rec in self:
            if rec.account_account_id and rec.account_account_id.currency_id:
                if rec.currency_id != rec.account_account_id.currency_id:
                    raise ValidationError(
                        _('Currency mismatch: the treasury account currency (%(acc_currency)s) '
                          'must match the Chart of Account "%(coa)s" currency (%(coa_currency)s).',
                          acc_currency=rec.currency_id.name,
                          coa=rec.account_account_id.display_name,
                          coa_currency=rec.account_account_id.currency_id.name,
                          )
                    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    def _compute_balance(self):
        """
        Compute the balance directly from posted journal items
        (account.move.line) of the linked Chart of Account.

        balance = SUM(debit) − SUM(credit)
        where account_id = linked CoA  AND  parent_state = 'posted'
        """
        # Collect all CoA ids that we need balances for
        coa_ids = [acc.account_account_id.id for acc in self if acc.account_account_id]
        if coa_ids:
            self.env.cr.execute("""
                SELECT account_id,
                       COALESCE(SUM(debit), 0) - COALESCE(SUM(credit), 0) AS balance
                  FROM account_move_line
                 WHERE account_id IN %s
                   AND parent_state = 'posted'
              GROUP BY account_id
            """, (tuple(coa_ids),))
            balances = dict(self.env.cr.fetchall())
        else:
            balances = {}

        for account in self:
            if account.account_account_id:
                account.balance = balances.get(account.account_account_id.id, 0.0)
            else:
                account.balance = 0.0

    def _compute_transaction_count(self):
        """Count the number of transactions for this account."""
        for account in self:
            account.transaction_count = len(account.transaction_ids)

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign sequence code on creation."""
        for vals in vals_list:
            if vals.get('code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code('finance.account') or _('New')
        return super().create(vals_list)

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------

    def action_view_transactions(self):
        """Open the list of transactions for this account."""
        self.ensure_one()
        return {
            'name': _('Transactions'),
            'type': 'ir.actions.act_window',
            'res_model': 'finance.transaction',
            'view_mode': 'list,form',
            'domain': [('account_id', '=', self.id)],
            'context': {'default_account_id': self.id},
        }

    # -------------------------------------------------------------------------
    # SQL CONSTRAINTS
    # -------------------------------------------------------------------------

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Account code must be unique!'),
    ]
