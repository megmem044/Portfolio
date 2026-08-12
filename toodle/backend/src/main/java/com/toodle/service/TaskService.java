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
import org.springframework.stereotype.Service;

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
        AppUser owner = currentUserService.get();
        return taskRepository.save(new Task(request.title(), request.description(), request.startDate(), request.startTime(), request.dueDate(), request.dueTime(), request.priority(), findCategory(request.categoryId(), owner), owner, request.completed()));
    }

    public Task update(UUID id, TaskRequest request) {
        Task task = findById(id);
        task.update(request.title(), request.description(), request.startDate(), request.startTime(), request.dueDate(), request.dueTime(), request.priority(), findCategory(request.categoryId(), currentUserService.get()), request.completed());
        return taskRepository.save(task);
    }

    public void delete(UUID id) {
        taskRepository.delete(findById(id));
    }

    private Category findCategory(UUID categoryId, AppUser owner) {
        if (categoryId == null) return null;
        return categoryRepository.findByIdAndOwner(categoryId, owner).orElseThrow(() -> new ResourceNotFoundException("Category", categoryId));
    }
}