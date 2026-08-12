package com.toodle.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record CategoryRequest(@NotBlank String name, @NotBlank @Pattern(regexp = "[0-9]") String color) {
}