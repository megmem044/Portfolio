# How the Project Is Organized

This guide explains where the code belongs and how a transaction moves through the app.

## The main flow

When someone adds a transaction, the app follows these steps:

1. A route receives the amount, merchant, and date.
2. A schema checks that the information is valid.
3. The categorizer chooses a category from the merchant name.
4. A model describes how the transaction is saved.
5. The database session saves it and returns the result.

In short:

`Request → validation → category rule → database → response`

## Folder guide

```text
app/
├── api/
│   ├── dependencies.py       Shared helpers used by routes
│   └── routes/               Available API actions
├── core/
│   └── config.py             App settings
├── db/
│   ├── base.py               Shared database model base
│   └── session.py            Database connection setup
├── models/
│   └── transaction.py        Stored transaction fields
├── schemas/
│   └── transaction.py        Accepted and returned information
├── services/
│   └── categorizer.py        Merchant category rules
└── main.py                   Creates and starts the app

tests/
├── conftest.py               Safe temporary test database
├── test_categorizer.py       Category-rule checks
└── test_transactions.py      API behavior checks

docs/
├── architecture.md           This file
├── phase-plan.md             Build phases and progress
└── product-requirements.md   User needs and feature checks
```

## Where new code should go

- Put web addresses and request handling in `app/api/routes`.
- Put shared route helpers in `app/api/dependencies.py`.
- Put business decisions in `app/services`.
- Put stored database fields in `app/models`.
- Put input and output checks in `app/schemas`.
- Put database connection code in `app/db`.
- Add a test whenever behavior is added or changed.

Keeping these jobs separate makes the project easier to understand, test, and extend.
