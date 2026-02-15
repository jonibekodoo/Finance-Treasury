# -*- coding: utf-8 -*-
{
    'name': 'Finance Treasury',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Finance',
    'summary': 'Universal Treasury Management: Cash, Bank, Card, Wallet & Financial Operations',
    'description': """
Finance Treasury Module
=======================
A comprehensive treasury management system that handles all financial operations
through a single unified transaction engine.

Features:
---------
* Manage Cash, Bank, Card, and Wallet accounts in one place
* Universal transaction model for income and expenses
* Account-to-account transfers
* Multi-currency exchange with automatic rate calculation
* Computed real-time account balances
* Negative balance protection
* Dashboard kanban view for account overview
* Pivot and graph reports for cash flow analysis
* Role-based security (User / Manager)
* Automatic sequence generation for all documents
    """,
    'author': 'Finance Treasury',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'account',
    ],
    'data': [
        # Security
        'security/treasury_security.xml',
        'security/ir.model.access.csv',
        # Data
        'data/sequence_data.xml',
        # Views
        'views/finance_account_views.xml',
        'views/finance_category_views.xml',
        'views/finance_transaction_views.xml',
        'views/finance_transfer_views.xml',
        'views/finance_exchange_views.xml',
        # Reports (must load before menus that reference report actions)
        'report/transaction_report_views.xml',
        # Menus
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
