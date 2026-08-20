// Keeps one correlation ID in each API request, response, and log entry.
package com.toodle.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/** Propagates a request correlation ID through response headers and structured logs. */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 1)
public class CorrelationIdFilter extends OncePerRequestFilter {
    private static final Logger LOGGER = LoggerFactory.getLogger(CorrelationIdFilter.class);
    private static final String HEADER = "X-Correlation-Id";
    private static final String SAFE_ID_PATTERN = "[A-Za-z0-9][A-Za-z0-9._:-]{0,127}";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String correlationId = request.getHeader(HEADER);
        if (correlationId == null || !correlationId.matches(SAFE_ID_PATTERN)) correlationId = UUID.randomUUID().toString();
        // MDC exposes the ID to every log entry emitted while this request is processed.
        MDC.put("correlationId", correlationId);
        response.setHeader(HEADER, correlationId);
        try {
            filterChain.doFilter(request, response);
            LOGGER.info("method={} path={} status={}", request.getMethod(), request.getRequestURI(), response.getStatus());
        } finally {
            MDC.remove("correlationId");
        }
    }
}
