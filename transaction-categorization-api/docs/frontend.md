# Frontend Guide

The frontend uses React, TypeScript, and Vite. React builds the visible screens, TypeScript checks the kinds of data being used, and Vite runs or builds the website.

## Current user journey

```text
Register → Sign in → Confirm user → Dashboard → Sign out
```

1. The registration form checks the email and matching passwords in the browser.
2. `src/api/auth.ts` sends the email and password to FastAPI.
3. Login returns a temporary access token.
4. The token is sent to `/auth/me` to retrieve the signed-in user.
5. `App.tsx` keeps the token and user in React state and shows the dashboard.
6. Logout asks FastAPI to revoke the token, then clears the React state.

The token currently exists only in memory. Refreshing or closing the page returns the user to login. This is intentional for the first version.

## Main files

- `src/App.tsx` owns the current authentication state and chooses a screen.
- `src/api/auth.ts` contains authentication requests and translates API errors.
- `src/pages/RegisterPage.tsx` contains registration fields and browser checks.
- `src/pages/LoginPage.tsx` signs in and loads the current user.
- `src/pages/DashboardPage.tsx` contains the authenticated layout.

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

## Next step

The dashboard will request the signed-in user's monthly summary and display loading, success, empty, and error states.
