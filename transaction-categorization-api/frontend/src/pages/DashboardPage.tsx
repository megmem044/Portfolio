import { useEffect, useState } from 'react'
import {
  getMonthlySummary,
  type MonthlySummary,
  type Transaction,
} from '../api/transactions'
import TransactionForm from '../components/TransactionForm'
import '../App.css'

const navigationItems = ['Overview', 'Transactions', 'Categories', 'Rules']

type DashboardPageProps = {
  email: string
  token: string
  isLoggingOut: boolean
  onLogout: () => Promise<void>
  onShowTransactions: () => void
}

function currentMonthKey() {
  const today = new Date()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  return `${today.getFullYear()}-${month}`
}

function topCategory(summary: MonthlySummary | null): string {
  if (!summary) return '—'

  const categories = Object.entries(summary.totals_by_category)
  if (categories.length === 0) return '—'

  return categories.reduce((largest, current) =>
    Number(current[1]) > Number(largest[1]) ? current : largest,
  )[0]
}

function DashboardPage({
  email,
  token,
  isLoggingOut,
  onLogout,
  onShowTransactions,
}: DashboardPageProps) {
  const initial = email.charAt(0).toUpperCase()
  const month = currentMonthKey()
  const monthLabel = new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric',
  }).format(new Date())
  const [summary, setSummary] = useState<MonthlySummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [retryCount, setRetryCount] = useState(0)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [notice, setNotice] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    async function loadSummary() {
      setIsLoading(true)
      setError('')

      try {
        const result = await getMonthlySummary(token, month, controller.signal)
        setSummary(result)
      } catch (requestError) {
        if (requestError instanceof Error && requestError.name === 'AbortError') return
        setError('We could not load your monthly summary. Please try again.')
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    void loadSummary()
    return () => controller.abort()
  }, [month, retryCount, token])

  const amount = isLoading ? 'Loading…' : `$${summary?.overall_total ?? '0.00'}`
  const transactionCount = isLoading ? '—' : String(summary?.transaction_count ?? 0)
  const categorizedLabel = summary?.transaction_count === 1
    ? '1 transaction categorized'
    : `${summary?.transaction_count ?? 0} transactions categorized`

  function handleTransactionCreated(transaction: Transaction) {
    setIsFormOpen(false)
    setNotice(`${transaction.merchant} was categorized as ${transaction.category}.`)
    setRetryCount((count) => count + 1)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Personal finance</p>
          <h1>ClearSpend</h1>
        </div>
        <nav aria-label="Main navigation">
          {navigationItems.map((item, index) => (
            <button
              className={index === 0 ? 'nav-item active' : 'nav-item'}
              type="button"
              key={item}
              aria-current={index === 0 ? 'page' : undefined}
              onClick={item === 'Transactions' ? onShowTransactions : undefined}
            >
              {item}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="avatar" aria-hidden="true">{initial}</div>
          <div>
            <strong>{email}</strong>
            <span>Signed in</span>
          </div>
          <button
            className="logout-button"
            type="button"
            onClick={onLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? 'Signing out…' : 'Sign out'}
          </button>
        </div>
      </aside>

      <main className="page-content">
        <header className="page-header">
          <div>
            <p className="eyebrow">{monthLabel}</p>
            <h2>Spending overview</h2>
            <p className="subtitle">
              Your dashboard will summarize transactions and categories here.
            </p>
          </div>
          <button
            className="primary-button"
            type="button"
            onClick={() => setIsFormOpen(true)}
          >
            Add transaction
          </button>
        </header>

        {notice && <p className="dashboard-notice" role="status">{notice}</p>}

        <section className="summary-grid" aria-label="Monthly summary">
          <article className="summary-card featured">
            <span>Total spending</span>
            <strong>{amount}</strong>
            <small>For the current calendar month</small>
          </article>
          <article className="summary-card">
            <span>Transactions</span>
            <strong>{transactionCount}</strong>
            <small>Recorded this month</small>
          </article>
          <article className="summary-card">
            <span>Top category</span>
            <strong>{topCategory(summary)}</strong>
            <small>Based on category totals</small>
          </article>
        </section>

        {error ? (
          <section className="empty-panel" role="alert">
            <div className="empty-icon" aria-hidden="true">!</div>
            <h3>Summary unavailable</h3>
            <p>{error}</p>
            <button
              className="secondary-button"
              type="button"
              onClick={() => setRetryCount((count) => count + 1)}
            >
              Try again
            </button>
          </section>
        ) : (
          <section className="empty-panel">
            <div className="empty-icon" aria-hidden="true">↗</div>
            <h3>
              {summary?.transaction_count
                ? categorizedLabel
                : 'No transactions yet'}
            </h3>
            <p>
              {summary?.transaction_count
                ? 'Your current-month totals are loaded from FastAPI.'
                : 'Add your first transaction to begin building the monthly summary.'}
            </p>
            <button
              className="secondary-button"
              type="button"
              onClick={() => setIsFormOpen(true)}
            >
              {summary?.transaction_count
                ? 'Add another transaction'
                : 'Add your first transaction'}
            </button>
          </section>
        )}

        {isFormOpen && (
          <TransactionForm
            token={token}
            onCancel={() => setIsFormOpen(false)}
            onSaved={handleTransactionCreated}
          />
        )}
      </main>
    </div>
  )
}

export default DashboardPage
