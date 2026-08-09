# Transaction Categorization — Product Guide

## What are we building?

This app helps people organize and understand their spending.

A user adds transactions such as:

> July 10 — Starbucks — $8.50

The app recognizes the merchant and suggests a category such as **Food & Dining**. The user can review transactions, correct categories, and see how much they spent each month.

The project currently provides a tested backend. It can save and manage transactions, manage categories and merchant rules, search transaction history, and calculate monthly totals. A website, file imports, user accounts, and machine learning are planned for later.

## Why is it useful?

Bank transaction descriptions can be hard to read, and sorting every purchase by hand takes time. This app aims to automate the repetitive work while allowing users to fix mistakes.

For example:

1. A user adds a purchase from Starbucks.
2. The app suggests **Food & Dining**.
3. If the suggestion is wrong, the user changes it.
4. The monthly dashboard updates with the corrected total.
5. In the future, these corrections can help the app make better suggestions.

## How does it work?

The project will have three main parts:

- **Backend:** Saves transactions, checks information, assigns categories, and calculates totals.
- **Frontend:** The screens and forms a user sees and interacts with.
- **Machine learning:** A future feature that learns from past examples and suggests categories for unfamiliar transactions.

The information moves through the app like this:

`User enters a transaction → app checks it → category is suggested → transaction is saved → reports are updated`

## Real-world user stories

A user story describes what someone wants to do and why. The checks below tell us when the feature is complete.

### 1. Add a transaction

As a user, I want to add a purchase so that I can track my spending.

Complete when:

- The user enters an amount, merchant, and date.
- Missing or incorrect information shows a helpful message.
- The saved transaction has a category and unique ID.

### 2. Automatically suggest a category

As a user, I want the app to recognize familiar merchants so that I do less manual work.

Complete when:

- Known merchants receive the expected category.
- Capital letters do not affect the result.
- Unknown merchants are marked **Uncategorized**.

### 3. Review and find transactions

As a user, I want to browse my transactions so that I can find a purchase easily.

Complete when:

- Transactions appear in a consistent order.
- The user can filter by date and category.
- Large lists are shown in manageable pages.

### 4. Correct or remove a transaction

As a user, I want to fix mistakes so that my records and reports remain accurate.

Complete when:

- The user can edit transaction details or change its category.
- The user can remove a duplicate or incorrect transaction.
- Monthly totals update after a change.

### 5. View monthly spending

As a user, I want a monthly summary so that I can understand where my money went.

Complete when:

- The user can choose a month.
- The app shows the total spent and number of transactions.
- Spending is grouped by category.
- A month with no transactions displays a clear empty result.

### 6. Import a bank file

As a user, I want to upload a CSV file from my bank so that I do not enter every transaction by hand.

Complete when:

- The user can preview transactions before saving them.
- Incorrect rows are clearly explained.
- Possible duplicates are identified.
- The app reports how many rows were imported or skipped.

### 7. Use a simple dashboard

As a user, I want an easy-to-read website so that I can manage spending without using the API directly.

Complete when:

- The dashboard shows monthly totals and category spending.
- The user can add, search, edit, and delete transactions.
- Loading, errors, and empty results are easy to understand.
- The website works with a keyboard and on smaller screens.

### 8. Improve suggestions over time

As a user, I want the app to learn from corrections so that future category suggestions become more useful.

Complete when:

- The app safely records category corrections.
- Suggestions show how confident the app is.
- Uncertain suggestions are sent to the user for review.
- Rules for known merchants still work if the learning system is unavailable.

## How will we test it?

Testing means checking that the app behaves correctly before users depend on it.

- **Small feature tests:** Check one action, such as categorizing Starbucks correctly.
- **API tests:** Add, list, edit, and summarize sample transactions as a real client would.
- **Frontend tests:** Check that forms, buttons, filters, and error messages work.
- **Full journey tests:** Follow a complete example from adding a purchase to viewing the updated report.
- **Machine-learning tests:** Measure how often suggestions are correct, including results for each category.

Financial totals must be exact. Tests should also cover empty lists, invalid dates, duplicate imports, unknown merchants, and months without transactions.

## Build plan

We will improve the project in small, working steps:

1. Make the current backend easy to install and run.
2. Add tests for the existing features.
3. Improve input checks and money calculations.
4. Add editing, deleting, searching, and categories.
5. Build the dashboard and transaction screens.
6. Add CSV imports.
7. Save user corrections and create a basic learning model.
8. Add confidence-based suggestions and review them with real examples.

Each step should be tested and documented before moving to the next one.
