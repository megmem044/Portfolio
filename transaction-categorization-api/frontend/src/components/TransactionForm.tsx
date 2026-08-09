/** Collect and save one transaction without mixing form logic into the dashboard. */

import { useState, type FormEvent } from 'react'
import {
  createTransaction,
  type Transaction,
  updateTransaction,
} from '../api/transactions'

type TransactionFormProps = {
  token: string
  transaction?: Transaction
  onCancel: () => void
  onSaved: (transaction: Transaction) => void
}

function localDate() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function TransactionForm({
  token,
  transaction,
  onCancel,
  onSaved,
}: TransactionFormProps) {
  const [amount, setAmount] = useState(transaction?.amount ?? '')
  const [merchant, setMerchant] = useState(transaction?.merchant ?? '')
  const [date, setDate] = useState(transaction?.date ?? localDate())
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const savedTransaction = transaction
        ? await updateTransaction(token, transaction.id, {
            amount,
            merchant: merchant.trim(),
            date,
          })
        : await createTransaction(token, amount, merchant.trim(), date)
      onSaved(savedTransaction)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'The transaction could not be saved.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section
        className="transaction-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="transaction-form-title"
      >
        <div className="modal-heading">
          <div>
            <p className="eyebrow">
              {transaction ? 'Edit transaction' : 'New transaction'}
            </p>
            <h3 id="transaction-form-title">
              {transaction ? 'Update spending' : 'Add spending'}
            </h3>
          </div>
          <button type="button" className="close-button" onClick={onCancel}>
            Close
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <label htmlFor="transaction-amount">Amount</label>
          <input
            id="transaction-amount"
            type="number"
            inputMode="decimal"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            placeholder="8.50"
            required
            autoFocus
          />

          <label htmlFor="transaction-merchant">Merchant</label>
          <input
            id="transaction-merchant"
            type="text"
            maxLength={200}
            value={merchant}
            onChange={(event) => setMerchant(event.target.value)}
            placeholder="Starbucks"
            required
          />

          <label htmlFor="transaction-date">Date</label>
          <input
            id="transaction-date"
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            required
          />

          {error && <p className="modal-error" role="alert">{error}</p>}

          <div className="modal-actions">
            <button className="secondary-button" type="button" onClick={onCancel}>
              Cancel
            </button>
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? 'Saving…'
                : transaction
                  ? 'Update transaction'
                  : 'Save transaction'}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default TransactionForm
