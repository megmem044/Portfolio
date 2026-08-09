/** Load transaction data for the authenticated dashboard. */

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export type MonthlySummary = {
  month: string
  transaction_count: number
  overall_total: string
  totals_by_category: Record<string, string>
}

export type Transaction = {
  id: number
  amount: string
  merchant: string
  category: string
  date: string
}

export type TransactionPage = {
  items: Transaction[]
  total: number
  page: number
  page_size: number
}

export type TransactionFilters = {
  search: string
  category: string
  start: string
  end: string
  sortBy: 'date' | 'amount' | 'merchant' | 'category'
  sortDirection: 'asc' | 'desc'
}

type FastApiError = {
  detail?: string | Array<{ msg: string }>
}

function errorMessage(error: FastApiError): string {
  if (typeof error.detail === 'string') return error.detail
  if (Array.isArray(error.detail) && error.detail.length > 0) {
    return error.detail[0].msg
  }
  return 'The transaction could not be saved.'
}

export async function getMonthlySummary(
  token: string,
  month: string,
  signal?: AbortSignal,
): Promise<MonthlySummary> {
  const query = new URLSearchParams({ month })
  const response = await fetch(`${API_URL}/transactions/summary?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
    signal,
  })

  if (!response.ok) {
    throw new Error('The monthly summary could not be loaded.')
  }

  return (await response.json()) as MonthlySummary
}

export async function createTransaction(
  token: string,
  amount: string,
  merchant: string,
  date: string,
): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ amount, merchant, date }),
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }

  return (await response.json()) as Transaction
}

export async function updateTransaction(
  token: string,
  transactionId: number,
  changes: { amount: string; merchant: string; date: string },
): Promise<Transaction> {
  const response = await fetch(`${API_URL}/transactions/${transactionId}`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(changes),
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }

  return (await response.json()) as Transaction
}

export async function deleteTransaction(
  token: string,
  transactionId: number,
): Promise<void> {
  const response = await fetch(`${API_URL}/transactions/${transactionId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })

  if (!response.ok) {
    const error = (await response.json()) as FastApiError
    throw new Error(errorMessage(error))
  }
}

export async function getTransactions(
  token: string,
  page: number,
  filters: TransactionFilters,
  signal?: AbortSignal,
): Promise<TransactionPage> {
  const query = new URLSearchParams({
    page: String(page),
    page_size: '10',
    sort_by: filters.sortBy,
    sort_direction: filters.sortDirection,
  })
  if (filters.search) query.set('search', filters.search)
  if (filters.category) query.set('category', filters.category)
  if (filters.start) query.set('start', filters.start)
  if (filters.end) query.set('end', filters.end)
  const response = await fetch(`${API_URL}/transactions/?${query}`, {
    headers: { Authorization: `Bearer ${token}` },
    signal,
  })

  if (!response.ok) {
    throw new Error('Transactions could not be loaded.')
  }

  return (await response.json()) as TransactionPage
}
