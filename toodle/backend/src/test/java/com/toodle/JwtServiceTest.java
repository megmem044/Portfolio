package com.toodle;

import static org.junit.jupiter.api.Assertions.assertThrows;

import com.toodle.security.JwtService;
import io.jsonwebtoken.JwtException;
import org.junit.jupiter.api.Test;

/** Focused token-expiry coverage independent of the web integration tests. */
class JwtServiceTest {
    private static final String SECRET = "test-jwt-signing-secret-that-is-long-enough-for-hmac-sha-256";

    @Test
    void rejectsAnExpiredToken() {
        JwtService jwtService = new JwtService(SECRET, -1);
        String token = jwtService.createToken("expired@example.com");
        assertThrows(JwtException.class, () -> jwtService.getEmail(token));
    }
}
