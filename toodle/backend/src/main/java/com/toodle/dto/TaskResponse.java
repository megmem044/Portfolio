package com.toodle.dto;

import com.toodle.model.Task;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

public record TaskResponse(UUID id, String title, String description, LocalDate startDate, LocalTime startTime, LocalDate dueDate, LocalTime dueTime, String priority, boolean isCompleted, UUID categoryId, String categoryColor, Instant createdAt) {
    public static TaskResponse from(Task task) {
        return new TaskResponse(
            task.getId(), task.getTitle(), task.getDescription(), task.getStartDate(), task.getStartTime(), task.getDueDate(), task.getDueTime(),
            task.getPriority().name().toLowerCase(), task.isCompleted(),
            task.getCategory() == null ? null : task.getCategory().getId(),
            task.getCategory() == null ? null : task.getCategory().getColor(), task.getCreatedAt()
        );
    }
}