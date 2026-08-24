// OpenTelemetry startup: records safe HTTP and Express timing before application modules load.
import { NodeSDK } from '@opentelemetry/sdk-node';
import { ConsoleSpanExporter, ParentBasedSampler, TraceIdRatioBasedSampler } from '@opentelemetry/sdk-trace-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

const tracingEnabled = process.env.OTEL_SDK_DISABLED === 'false';

if (tracingEnabled) {
  const configuredRatio = Number(process.env.OTEL_TRACES_SAMPLER_ARG ?? 0.1);
  const samplingRatio = Number.isFinite(configuredRatio) && configuredRatio >= 0 && configuredRatio <= 1 ? configuredRatio : 0.1;
  const sdk = new NodeSDK({
    serviceName: process.env.OTEL_SERVICE_NAME ?? 'toodle-bff',
    sampler: new ParentBasedSampler({ root: new TraceIdRatioBasedSampler(samplingRatio) }),
    traceExporter: new ConsoleSpanExporter(),
    instrumentations: [getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false },
      '@opentelemetry/instrumentation-http': {
        headersToSpanAttributes: {
          client: { requestHeaders: [], responseHeaders: [] },
          server: { requestHeaders: [], responseHeaders: [] },
        },
      },
    })],
  });

  sdk.start();

  const stopTracing = () => {
    void sdk.shutdown().finally(() => process.exit(0));
  };
  process.once('SIGTERM', stopTracing);
  process.once('SIGINT', stopTracing);
}
