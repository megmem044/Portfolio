# Frontend Guide

The frontend uses React, TypeScript, and Vite. React builds the visible screens, TypeScript checks the kinds of data being used, and Vite runs or builds the website.

## Current user journey

```text
Register → Sign in → Dashboard → Add transaction → Review or edit → Sign out
```

1. The registration form checks the email and matching passwords in the browser.
2. `src/api/auth.ts` sends the email and password to FastAPI.
3. Login returns a temporary access token.
4. The token is sent to `/auth/me` to retrieve the signed-in user.
5. `App.tsx` keeps the token and user in React state and shows the dashboard.
6. Logout asks FastAPI to revoke the token, then clears the React state.
7. The dashboard loads the current monthly summary using the token.
8. The transaction page loads one database page at a time and supports filters and sorting.
9. Create, edit, and delete actions refresh the affected data.

The token currently exists only in memory. Refreshing or closing the page returns the user to login. This is intentional for the first version.

## Main files

- `src/App.tsx` owns the current authentication state and chooses a screen.
- `src/api/auth.ts` contains authentication requests and translates API errors.
- `src/pages/RegisterPage.tsx` contains registration fields and browser checks.
- `src/pages/LoginPage.tsx` signs in and loads the current user.
- `src/pages/DashboardPage.tsx` contains the authenticated layout.
- `src/pages/TransactionsPage.tsx` contains the table, filters, sorting, and pagination.
- `src/components/TransactionForm.tsx` is reused for transaction creation and editing.
- `src/api/transactions.ts` contains authenticated transaction and summary requests.

Keeping API requests outside page components makes the screens easier to read and allows the request code to be reused.

## React ideas used so far

**State** stores information that can change:

```tsx
const [email, setEmail] = useState('')
```

**Props** pass information or actions from a parent component to a child:

```tsx
<DashboardPage email={user.email} onLogout={handleLogout} />
```

**Conditional rendering** chooses the visible page:

```text
Authenticated → dashboard
Not authenticated → login or registration
```

## Run and check the frontend

From the repository root:

```powershell
npm --prefix frontend run dev
npm --prefix frontend run lint
npm --prefix frontend run build
```

- `dev` starts the local website.
- `lint` checks for suspicious code patterns.
- `build` checks TypeScript and creates optimized production files.

## Transaction data flow

```text
React form → FastAPI validation → category rule → database → refreshed UI
```

The table sends filters and sorting choices to FastAPI. The database applies them before pagination, so results remain correct across pages.

Deletion requires a second confirmation action and identifies the exact merchant and amount before removing data.

## Next step

Build category management screens, followed by merchant-rule management and richer monthly reporting.
