/** Display one page of the signed-in user's transaction history. */

import { useEffect, useState, type FormEvent } from 'react'
import { getCategories, type Category } from '../api/categories'
import {
  deleteTransaction,
  getTransactions,
  type Transaction,
  type TransactionFilters,
  type TransactionPage as TransactionPageData,
} from '../api/transactions'
import TransactionForm from '../components/TransactionForm'
import './TransactionsPage.css'

type TransactionsPageProps = {
  token: string
  email: string
  onBack: () => void
}

const emptyFilters: TransactionFilters = {
  search: '',
  category: '',
  start: '',
  end: '',
  sortBy: 'date',
  sortDirection: 'desc',
}

function TransactionsPage({ token, email, onBack }: TransactionsPageProps) {
  const [page, setPage] = useState(1)
  const [data, setData] = useState<TransactionPageData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [categories, setCategories] = useState<Category[]>([])
  const [draftFilters, setDraftFilters] = useState<TransactionFilters>(emptyFilters)
  const [appliedFilters, setAppliedFilters] = useState<TransactionFilters>(emptyFilters)
  const [selectedTransaction, setSelectedTransaction] =
    useState<Transaction | null>(null)
  const [reloadCount, setReloadCount] = useState(0)
  const [notice, setNotice] = useState('')
  const [transactionToDelete, setTransactionToDelete] =
    useState<Transaction | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    getCategories(token, controller.signal)
      .then(setCategories)
      .catch((requestError: unknown) => {
        if (requestError instanceof Error && requestError.name === 'AbortError') return
        setError('Categories could not be loaded.')
      })
    return () => controller.abort()
  }, [token])

  useEffect(() => {
    const controller = new AbortController()

    async function loadTransactions() {
      setIsLoading(true)
      setError('')
      try {
        setData(
          await getTransactions(token, page, appliedFilters, controller.signal),
        )
      } catch (requestError) {
        if (requestError instanceof Error && requestError.name === 'AbortError') return
        setError('We could not load your transactions.')
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    void loadTransactions()
    return () => controller.abort()
  }, [appliedFilters, page, reloadCount, token])

  const hasNextPage = data ? data.page * data.page_size < data.total : false

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPage(1)
    setAppliedFilters({
      ...draftFilters,
      search: draftFilters.search.trim(),
    })
  }

  function clearFilters() {
    setDraftFilters(emptyFilters)
    setAppliedFilters(emptyFilters)
    setPage(1)
  }

  function handleTransactionSaved(transaction: Transaction) {
    setSelectedTransaction(null)
    setNotice(`${transaction.merchant} was updated successfully.`)
    setReloadCount((count) => count + 1)
  }

  async function confirmDelete() {
    if (!transactionToDelete) return

    setIsDeleting(true)
    setDeleteError('')
    try {
      await deleteTransaction(token, transactionToDelete.id)
      setNotice(`${transactionToDelete.merchant} was deleted.`)
      setTransactionToDelete(null)

      if (data?.items.length === 1 && page > 1) {
        setPage((current) => current - 1)
      } else {
        setReloadCount((count) => count + 1)
      }
    } catch (requestError) {
      setDeleteError(
        requestError instanceof Error
          ? requestError.message
          : 'The transaction could not be deleted.',
      )
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <main className="transactions-page">
      <header className="transactions-header">
        <div>
          <button className="back-button" type="button" onClick={onBack}>
            ← Back to overview
          </button>
          <p className="eyebrow">{email}</p>
          <h1>Transactions</h1>
          <p>Review your most recent spending records.</p>
        </div>
        <span className="result-count">{data?.total ?? 0} total</span>
      </header>

      <form className="transaction-filters" onSubmit={applyFilters}>
        <div className="filter-field merchant-filter">
          <label htmlFor="merchant-search">Merchant</label>
          <input
            id="merchant-search"
            type="search"
            value={draftFilters.search}
            onChange={(event) =>
              setDraftFilters({ ...draftFilters, search: event.target.value })
            }
            placeholder="Search merchant"
          />
        </div>

        <div className="filter-field">
          <label htmlFor="category-filter">Category</label>
          <select
            id="category-filter"
            value={draftFilters.category}
            onChange={(event) =>
              setDraftFilters({ ...draftFilters, category: event.target.value })
            }
          >
            <option value="">All categories</option>
            {categories.map((category) => (
              <option value={category.name} key={category.id}>{category.name}</option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="start-date">From</label>
          <input
            id="start-date"
            type="date"
            value={draftFilters.start}
            onChange={(event) =>
              setDraftFilters({ ...draftFilters, start: event.target.value })
            }
          />
        </div>

        <div className="filter-field">
          <label htmlFor="end-date">To</label>
          <input
            id="end-date"
            type="date"
            value={draftFilters.end}
            onChange={(event) =>
              setDraftFilters({ ...draftFilters, end: event.target.value })
            }
          />
        </div>

        <div className="filter-field">
          <label htmlFor="sort-field">Sort by</label>
          <select
            id="sort-field"
            value={draftFilters.sortBy}
            onChange={(event) =>
              setDraftFilters({
                ...draftFilters,
                sortBy: event.target.value as TransactionFilters['sortBy'],
              })
            }
          >
            <option value="date">Date</option>
            <option value="amount">Amount</option>
            <option value="merchant">Merchant</option>
            <option value="category">Category</option>
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="sort-direction">Order</label>
          <select
            id="sort-direction"
            value={draftFilters.sortDirection}
            onChange={(event) =>
              setDraftFilters({
                ...draftFilters,
                sortDirection: event.target.value as TransactionFilters['sortDirection'],
              })
            }
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>

        <div className="filter-actions">
          <button type="button" onClick={clearFilters}>Clear</button>
          <button type="submit">Apply filters</button>
        </div>
      </form>

      {notice && <p className="list-notice" role="status">{notice}</p>}

      {error && <p className="list-message error" role="alert">{error}</p>}
      {isLoading && <p className="list-message" role="status">Loading transactions…</p>}

      {!isLoading && !error && data?.items.length === 0 && (
        <section className="transaction-empty">
          <h2>No transactions found</h2>
          <p>Add a transaction from the overview to see it here.</p>
        </section>
      )}

      {!isLoading && !error && data && data.items.length > 0 && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant</th>
                <th>Category</th>
                <th className="amount-column">Amount</th>
                <th className="action-column">Action</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((transaction) => (
                <tr key={transaction.id}>
                  <td>{transaction.date}</td>
                  <td><strong>{transaction.merchant}</strong></td>
                  <td><span className="category-pill">{transaction.category}</span></td>
                  <td className="amount-column">${transaction.amount}</td>
                  <td className="action-column">
                    <button
                      type="button"
                      onClick={() => setSelectedTransaction(transaction)}
                    >
                      Edit
                    </button>
                    <button
                      className="delete-button"
                      type="button"
                      onClick={() => {
                        setDeleteError('')
                        setTransactionToDelete(transaction)
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <nav className="pagination" aria-label="Transaction pages">
        <button
          type="button"
          onClick={() => setPage((current) => current - 1)}
          disabled={page === 1 || isLoading}
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button
          type="button"
          onClick={() => setPage((current) => current + 1)}
          disabled={!hasNextPage || isLoading}
        >
          Next
        </button>
      </nav>

      {selectedTransaction && (
        <TransactionForm
          token={token}
          transaction={selectedTransaction}
          onCancel={() => setSelectedTransaction(null)}
          onSaved={handleTransactionSaved}
        />
      )}

      {transactionToDelete && (
        <div className="modal-backdrop" role="presentation">
          <section
            className="delete-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-title"
          >
            <p className="eyebrow">Confirm deletion</p>
            <h2 id="delete-title">Delete {transactionToDelete.merchant}?</h2>
            <p>
              This will permanently remove the ${transactionToDelete.amount}
              transaction and update its monthly summary.
            </p>

            {deleteError && <p className="modal-error" role="alert">{deleteError}</p>}

            <div className="modal-actions">
              <button
                className="secondary-button"
                type="button"
                onClick={() => setTransactionToDelete(null)}
                disabled={isDeleting}
              >
                Keep transaction
              </button>
              <button
                className="danger-button"
                type="button"
                onClick={confirmDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting…' : 'Delete permanently'}
              </button>
            </div>
          </section>
        </div>
      )}
    </main>
  )
}

export default TransactionsPage
