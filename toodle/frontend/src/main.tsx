import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
// Browser entry point: mounts the React application and loads the shared Toodle design system.
import './styles.css';
import { App } from './app/App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
