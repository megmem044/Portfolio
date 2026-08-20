// Registers accounts and checks login credentials.
package com.toodle.service;

import com.toodle.dto.AuthResponse;
import com.toodle.dto.LoginRequest;
import com.toodle.dto.RegisterRequest;
import com.toodle.model.AppUser;
import com.toodle.repository.UserRepository;
import com.toodle.security.JwtService;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/** Registers users and validates credentials before issuing JWT-backed sessions. */
@Service
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public AuthResponse register(RegisterRequest request) {
        String email = request.email().trim().toLowerCase();
        if (userRepository.existsByEmailIgnoreCase(email)) throw new ResponseStatusException(HttpStatus.CONFLICT, "An account already exists for this email");
        AppUser user = userRepository.save(new AppUser(request.name().trim(), email, passwordEncoder.encode(request.password())));
        return AuthResponse.from(user, jwtService.createToken(user.getEmail()));
    }

    public AuthResponse login(LoginRequest request) {
        AppUser user = userRepository.findByEmailIgnoreCase(request.email().trim()).orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password"));
        if (!passwordEncoder.matches(request.password(), user.getPasswordHash())) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid email or password");
        return AuthResponse.from(user, jwtService.createToken(user.getEmail()));
    }
}
