package com.toodle.exception;

import java.time.Instant;

/** Stable error contract returned by both MVC handlers and Spring Security. */
public record ApiError(Instant timestamp, int status, String code, String message, String path, String correlationId) {
    public static ApiError of(int status, String code, String message, String path, String correlationId) {
        return new ApiError(Instant.now(), status, code, message, path, correlationId);
    }
}
