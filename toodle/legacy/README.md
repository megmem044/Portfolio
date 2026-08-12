# Legacy prototypes

These files preserve the product history that the active full-stack application is modernizing.

- `web/` is the original browser-only PWA. It uses vanilla JavaScript and browser storage. Its stylesheet and icon were promoted into `frontend/` because the React migration intentionally keeps the established design.
- `ios/` is an earlier SwiftUI/MVVM prototype and is not part of the current build.

The prototypes are reference material only. New implementation work belongs in `frontend/`, `bff/`, or `backend/`.
