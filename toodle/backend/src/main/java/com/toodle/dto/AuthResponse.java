// Defines the login and registration response sent to clients.
package com.toodle.dto;

import com.toodle.model.AppUser;

public record AuthResponse(String token, String name, String email) {
    public static AuthResponse from(AppUser user, String token) {
        return new AuthResponse(token, user.getName(), user.getEmail());
    }
}
