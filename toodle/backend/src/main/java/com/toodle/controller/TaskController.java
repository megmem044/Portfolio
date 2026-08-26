// Exposes task operations for the signed-in user.
package com.toodle.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.toodle.dto.TaskRequest;
import com.toodle.dto.TaskResponse;
import com.toodle.service.TaskService;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.CacheControl;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.context.request.WebRequest;

@RestController
@RequestMapping("/api/tasks")
@CrossOrigin(origins = "http://127.0.0.1:5173")
@Tag(name = "Tasks", description = "Manage tasks owned by the signed-in user")
@SecurityRequirement(name = "bearerAuth")
public class TaskController {
    private final TaskService taskService;
    private final ObjectMapper objectMapper;

    public TaskController(TaskService taskService, ObjectMapper objectMapper) {
        this.taskService = taskService;
        this.objectMapper = objectMapper;
    }

    @GetMapping
    public ResponseEntity<List<TaskResponse>> getTasks(WebRequest request) {
        List<TaskResponse> tasks = taskService.findAll().stream().map(TaskResponse::from).toList();
        String etag = etagFor(tasks);
        CacheControl cachePolicy = CacheControl.noCache().cachePrivate().mustRevalidate();
        if (request.checkNotModified(etag)) {
            return ResponseEntity.status(HttpStatus.NOT_MODIFIED).cacheControl(cachePolicy).eTag(etag).header("Vary", "Authorization").build();
        }
        return ResponseEntity.ok().cacheControl(cachePolicy).eTag(etag).header("Vary", "Authorization").body(tasks);
    }

    @GetMapping("/{id}")
    public TaskResponse getTask(@PathVariable UUID id) {
        return TaskResponse.from(taskService.findById(id));
    }

    @PostMapping
    @org.springframework.web.bind.annotation.ResponseStatus(HttpStatus.CREATED)
    public TaskResponse createTask(@Valid @RequestBody TaskRequest request) {
        return TaskResponse.from(taskService.create(request));
    }

    @PutMapping("/{id}")
    public TaskResponse updateTask(@PathVariable UUID id, @Valid @RequestBody TaskRequest request) {
        return TaskResponse.from(taskService.update(id, request));
    }

    @DeleteMapping("/{id}")
    @org.springframework.web.bind.annotation.ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteTask(@PathVariable UUID id) {
        taskService.delete(id);
    }

    private String etagFor(List<TaskResponse> tasks) {
        try {
            byte[] representation = objectMapper.writeValueAsBytes(tasks);
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(representation);
            return "\"" + HexFormat.of().formatHex(digest) + "\"";
        } catch (JsonProcessingException | NoSuchAlgorithmException exception) {
            throw new IllegalStateException("Unable to calculate the task-list ETag", exception);
        }
    }
}
