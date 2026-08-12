// Process entry point: starts the configured BFF HTTP server.
import { createApp } from './app.js';

const port = Number(process.env.PORT ?? 3000);
createApp().listen(port, () => console.log(`Toodle BFF listening on http://127.0.0.1:${port}`));
