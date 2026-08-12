package com.toodle.service;

import com.toodle.dto.CategoryRequest;
import com.toodle.exception.ResourceNotFoundException;
import com.toodle.model.Category;
import com.toodle.model.Task;
import com.toodle.model.AppUser;
import com.toodle.repository.CategoryRepository;
import com.toodle.repository.TaskRepository;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class CategoryService {
    private final CategoryRepository categoryRepository;
    private final TaskRepository taskRepository;
    private final CurrentUserService currentUserService;

    public CategoryService(CategoryRepository categoryRepository, TaskRepository taskRepository, CurrentUserService currentUserService) {
        this.categoryRepository = categoryRepository;
        this.taskRepository = taskRepository;
        this.currentUserService = currentUserService;
    }

    public List<Category> findAll() { return categoryRepository.findAllByOwner(currentUserService.get()); }
    public Category create(CategoryRequest request) {
        AppUser owner = currentUserService.get();
        String name = normalizeName(request.name());
        if (categoryRepository.existsByNameIgnoreCaseAndOwner(name, owner)) conflict(name);
        return categoryRepository.save(new Category(name, request.color(), owner));
    }
    public Category update(UUID id, CategoryRequest request) {
        AppUser owner = currentUserService.get();
        Category category = categoryRepository.findByIdAndOwner(id, owner).orElseThrow(() -> new ResourceNotFoundException("Category", id));
        String name = normalizeName(request.name());
        if (categoryRepository.existsByNameIgnoreCaseAndOwnerAndIdNot(name, owner, id)) conflict(name);
        category.update(name, request.color());
        return categoryRepository.save(category);
    }
    public void delete(UUID id) {
        AppUser owner = currentUserService.get();
        Category category = categoryRepository.findByIdAndOwner(id, owner).orElseThrow(() -> new ResourceNotFoundException("Category", id));
        List<Task> tasks = taskRepository.findAllByCategoryIdAndOwner(id, owner);
        tasks.forEach(task -> task.clearCategory());
        taskRepository.saveAll(tasks);
        categoryRepository.delete(category);
    }

    private String normalizeName(String name) {
        String normalized = name.trim();
        if (normalized.isEmpty()) throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Category name cannot be blank");
        return normalized;
    }

    private void conflict(String name) {
        throw new ResponseStatusException(HttpStatus.CONFLICT, "Category already exists: " + name);
    }
}
