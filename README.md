# Finance Treasury — Odoo 19

**Universal Treasury Management: Cash, Bank, Card, Wallet & Financial Operations**

A comprehensive treasury management module for Odoo 19 that handles all financial operations through a single unified transaction engine with full Odoo Accounting integration.

---

## Features

### Multi-Account Management
- Manage **Cash**, **Bank**, **Card**, and **Wallet** accounts from a single dashboard
- Each account links to a Chart of Accounts entry and an Accounting Journal
- Real-time balance computed from posted journal items
- Per-account negative balance protection (overdraft toggle)
- Auto-generated account codes (ACC/0001, ACC/0002, ...)

### Universal Transactions
- Single model for both income and expenses
- State workflow: **Draft** → **Confirmed** → **Cancelled**
- On confirmation: automatically creates and posts a journal entry
- On cancellation: cleanly reverses the journal entry
- On deletion: removes linked journal entries
- Balance validation prevents overdraft (when enabled)

### Account-to-Account Transfers
- Transfer money between treasury accounts
- Same-currency validation (use Exchange for different currencies)
- Creates paired outgoing + incoming transactions
- Full balance validation on the source account
- Auto-generated references (TRF/2026/00001)

### Multi-Currency Exchange
- Exchange between accounts with different currencies
- Auto-calculates exchange rate from Odoo's currency rate engine
- Manual rate override supported
- Exchange fee support (charged from source account)
- Auto-generated references (EXC/2026/00001)

### Reports & Analytics
- **Cash Flow Report** — Pivot table and bar chart by date, account, and type
- **Income vs. Expense Report** — Pivot table and pie chart by category and type

### Kanban Dashboard
- Visual overview of all accounts grouped by type
- Shows account name, code, type badge, live balance, and transaction count

### Security
- **Treasury User** — Create and view transactions (no delete)
- **Treasury Manager** — Full access including cancel, delete, and configuration
- Multi-company record rules

---

## Accounting Integration

Every treasury operation is backed by real journal entries in Odoo Accounting. No manual bookkeeping required.

| Operation | Debit | Credit |
|-----------|-------|--------|
| **Income** | Account's CoA (asset +) | Category's CoA (income recognized) |
| **Expense** | Category's CoA (expense recognized) | Account's CoA (asset −) |
| **Transfer** | Paired: outgoing expense + incoming income via transfer category |
| **Exchange** | Paired: outgoing in source currency + incoming in target currency |

- Balances are computed live: `SUM(debit) − SUM(credit)` from `account.move.line` where `parent_state = 'posted'`
- Currency on treasury accounts is enforced to match the linked Chart of Accounts entry

---

## Data Models

| Model | Description |
|-------|-------------|
| `finance.account` | Cash, Bank, Card, Wallet accounts with CoA & Journal links |
| `finance.transaction` | Universal income/expense model with journal entry lifecycle |
| `finance.transfer` | Same-currency account-to-account transfers |
| `finance.exchange` | Multi-currency exchanges with auto-rate & fee support |
| `finance.category` | Income / Expense / Transfer / Exchange categories linked to CoA |

---

## Menu Structure

```
Treasury
├── Operations
│   ├── Transactions
│   ├── Transfers
│   └── Currency Exchanges
├── Accounts
├── Reporting
│   ├── Cash Flow Report
│   └── Income vs. Expense
└── Configuration
    └── Categories (Manager only)
```

---

## Installation

1. Copy the `finance-treasury` folder into your Odoo addons directory
2. Update the apps list: **Settings** → **Apps** → **Update Apps List**
3. Search for **Finance Treasury** and click **Install**

### Dependencies

| Module | Purpose |
|--------|---------|
| `base` | Core Odoo framework |
| `mail` | Chatter, tracking, and activities |
| `account` | Accounting integration (Chart of Accounts, Journals, Journal Entries) |

---

## Configuration

### 1. Create Categories
Go to **Treasury** → **Configuration** → **Categories** and create:
- **Income** categories (e.g., Sales Revenue, Interest) — link to income CoA accounts
- **Expense** categories (e.g., Rent, Utilities, Salaries) — link to expense CoA accounts
- **Transfer** category — link to a clearing/transit CoA account
- **Exchange** category — link to an exchange clearing CoA account

### 2. Create Treasury Accounts
Go to **Treasury** → **Accounts** and create your accounts:
- Select account type: Cash, Bank, Card, or Wallet
- Link to a **Chart of Account** entry (currency must match)
- Link to an **Accounting Journal**
- Toggle **Allow Negative Balance** if overdraft should be permitted

### 3. Start Recording Operations
- **Transactions**: Record daily income and expenses
- **Transfers**: Move money between same-currency accounts
- **Exchanges**: Convert between currencies

---

## Technical Details

| Property | Value |
|----------|-------|
| **Version** | 19.0.1.0.0 |
| **License** | LGPL-3 |
| **Category** | Accounting/Finance |
| **Author** | Jonibek Yorqulov |

---

## License

This module is licensed under the **GNU Lesser General Public License v3.0 (LGPL-3)**.
See [LICENSE](https://www.gnu.org/licenses/lgpl-3.0.html) for details.
