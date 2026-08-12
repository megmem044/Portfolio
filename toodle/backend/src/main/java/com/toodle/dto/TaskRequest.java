package com.toodle.dto;

import com.toodle.model.Priority;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

public record TaskRequest(
    @NotBlank String title,
    String description,
    LocalDate startDate,
    LocalTime startTime,
    LocalDate dueDate,
    LocalTime dueTime,
    @NotNull Priority priority,
    UUID categoryId,
    boolean completed
) {
}