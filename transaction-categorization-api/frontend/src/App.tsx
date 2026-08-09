import './App.css'

const navigationItems = ['Overview', 'Transactions', 'Categories', 'Rules']

function App() {
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
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="avatar" aria-hidden="true">G</div>
          <div>
            <strong>Guest user</strong>
            <span>Not signed in</span>
          </div>
        </div>
      </aside>

      <main className="page-content">
        <header className="page-header">
          <div>
            <p className="eyebrow">August 2026</p>
            <h2>Spending overview</h2>
            <p className="subtitle">
              Your dashboard will summarize transactions and categories here.
            </p>
          </div>
          <button className="primary-button" type="button">
            Add transaction
          </button>
        </header>

        <section className="summary-grid" aria-label="Monthly summary">
          <article className="summary-card featured">
            <span>Total spending</span>
            <strong>$0.00</strong>
            <small>No transactions this month</small>
          </article>
          <article className="summary-card">
            <span>Transactions</span>
            <strong>0</strong>
            <small>Ready for your first entry</small>
          </article>
          <article className="summary-card">
            <span>Top category</span>
            <strong>—</strong>
            <small>Categories appear after spending</small>
          </article>
        </section>

        <section className="empty-panel">
          <div className="empty-icon" aria-hidden="true">↗</div>
          <h3>No transactions yet</h3>
          <p>
            Once the frontend connects to FastAPI, your recent transactions will
            appear here.
          </p>
          <button className="secondary-button" type="button">
            Add your first transaction
          </button>
        </section>
      </main>
    </div>
  )
}

export default App
