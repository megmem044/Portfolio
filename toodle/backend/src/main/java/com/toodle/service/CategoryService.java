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
import org.springframework.stereotype.Service;

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
    public Category create(CategoryRequest request) { return categoryRepository.save(new Category(request.name(), request.color(), currentUserService.get())); }
    public Category update(UUID id, CategoryRequest request) {
        AppUser owner = currentUserService.get();
        Category category = categoryRepository.findByIdAndOwner(id, owner).orElseThrow(() -> new ResourceNotFoundException("Category", id));
        category.update(request.name(), request.color());
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
}