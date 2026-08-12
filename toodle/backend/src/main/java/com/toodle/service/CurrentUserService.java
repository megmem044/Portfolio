package com.toodle.service;

import com.toodle.model.AppUser;
import com.toodle.repository.UserRepository;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
public class CurrentUserService {
    private final UserRepository userRepository;
    public CurrentUserService(UserRepository userRepository) { this.userRepository = userRepository; }

    public AppUser get() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        return userRepository.findByEmailIgnoreCase(email).orElseThrow();
    }
}