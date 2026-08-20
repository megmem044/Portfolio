// Applies task rules, ownership checks, and safe update handling.
package com.toodle.service;

import com.toodle.dto.TaskRequest;
import com.toodle.exception.ResourceNotFoundException;
import com.toodle.model.Category;
import com.toodle.model.AppUser;
import com.toodle.model.Task;
import com.toodle.repository.CategoryRepository;
import com.toodle.repository.TaskRepository;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

/** Applies task operations while enforcing the authenticated owner boundary. */
@Service
public class TaskService {
    private final TaskRepository taskRepository;
    private final CategoryRepository categoryRepository;
    private final CurrentUserService currentUserService;

    public TaskService(TaskRepository taskRepository, CategoryRepository categoryRepository, CurrentUserService currentUserService) {
        this.taskRepository = taskRepository;
        this.categoryRepository = categoryRepository;
        this.currentUserService = currentUserService;
    }

    public List<Task> findAll() {
        return taskRepository.findAllByOwner(currentUserService.get());
    }

    public Task findById(UUID id) {
        return taskRepository.findByIdAndOwner(id, currentUserService.get()).orElseThrow(() -> new ResourceNotFoundException("Task", id));
    }

    public Task create(TaskRequest request) {
        validateSchedule(request);
        AppUser owner = currentUserService.get();
        return taskRepository.save(new Task(request.title().trim(), normalize(request.description()), request.startDate(), request.startTime(), request.dueDate(), request.dueTime(), request.priority(), findCategory(request.categoryId(), owner), owner, request.completed()));
    }

    @Transactional
    public Task update(UUID id, TaskRequest request) {
        validateSchedule(request);
        Task task = findById(id);
        if (request.version() == null || request.version() != task.getVersion()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "This task changed since you opened it. Refresh and try again.");
        }
        task.update(request.title().trim(), normalize(request.description()), request.startDate(), request.startTime(), request.dueDate(), request.dueTime(), request.priority(), findCategory(request.categoryId(), currentUserService.get()), request.completed());
        taskRepository.flush();
        return task;
    }

    public void delete(UUID id) {
        taskRepository.delete(findById(id));
    }

    private Category findCategory(UUID categoryId, AppUser owner) {
        if (categoryId == null) return null;
        return categoryRepository.findByIdAndOwner(categoryId, owner).orElseThrow(() -> new ResourceNotFoundException("Category", categoryId));
    }

    private void validateSchedule(TaskRequest request) {
        if (request.startTime() != null && request.startDate() == null) badRequest("Start time requires a start date");
        if (request.dueTime() != null && request.dueDate() == null) badRequest("Due time requires a due date");
        if (request.startDate() != null && request.dueDate() != null) {
            if (request.dueDate().isBefore(request.startDate())) badRequest("Due date cannot be before start date");
            if (request.dueDate().isEqual(request.startDate()) && request.startTime() != null && request.dueTime() != null && request.dueTime().isBefore(request.startTime())) {
                badRequest("Due time cannot be before start time on the same date");
            }
        }
    }

    private void badRequest(String message) {
        throw new ResponseStatusException(HttpStatus.BAD_REQUEST, message);
    }

    private String normalize(String value) {
        if (value == null) return null;
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }
}
