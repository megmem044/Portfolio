package com.toodle.model;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

@Entity
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    private String title;
    private String description;
    private LocalDate startDate;
    private LocalTime startTime;
    private LocalDate dueDate;
    private LocalTime dueTime;
    @Enumerated(EnumType.STRING)
    private Priority priority;
    private boolean completed;
    private Instant createdAt;
    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;
    @ManyToOne
    @JoinColumn(name = "owner_id")
    private AppUser owner;

    protected Task() {
    }

    public Task(String title, String description, LocalDate startDate, LocalTime startTime, LocalDate dueDate, LocalTime dueTime, Priority priority, Category category, AppUser owner, boolean completed) {
        this.title = title;
        this.description = description;
        this.startDate = startDate;
        this.startTime = startTime;
        this.dueDate = dueDate;
        this.dueTime = dueTime;
        this.priority = priority;
        this.category = category;
        this.owner = owner;
        this.completed = completed;
        this.createdAt = Instant.now();
    }

    public UUID getId() { return id; }
    public String getTitle() { return title; }
    public String getDescription() { return description; }
    public LocalDate getStartDate() { return startDate; }
    public LocalTime getStartTime() { return startTime; }
    public LocalDate getDueDate() { return dueDate; }
    public LocalTime getDueTime() { return dueTime; }
    public Priority getPriority() { return priority; }
    public boolean isCompleted() { return completed; }
    public Instant getCreatedAt() { return createdAt; }
    public Category getCategory() { return category; }

    public void update(String title, String description, LocalDate startDate, LocalTime startTime, LocalDate dueDate, LocalTime dueTime, Priority priority, Category category, boolean completed) {
        this.title = title;
        this.description = description;
        this.startDate = startDate;
        this.startTime = startTime;
        this.dueDate = dueDate;
        this.dueTime = dueTime;
        this.priority = priority;
        this.category = category;
        this.completed = completed;
    }

    public void clearCategory() {
        this.category = null;
    }
}