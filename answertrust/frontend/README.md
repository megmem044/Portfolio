# AnswerTrust frontend

The primary AnswerTrust interface is built with React, TypeScript, and Vite.

## Local development

```powershell
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1
```

The frontend expects the API at `http://127.0.0.1:8000/api/v1`. Set
`VITE_API_URL` to use a different API address.

## Verification

```powershell
npm.cmd run build
npm.cmd run lint
npm.cmd run test:e2e
```
