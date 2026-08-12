package com.toodle.repository;

import com.toodle.model.Task;
import com.toodle.model.AppUser;
import java.util.UUID;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface TaskRepository extends JpaRepository<Task, UUID> {
	List<Task> findAllByCategoryIdAndOwner(UUID categoryId, AppUser owner);
	List<Task> findAllByOwner(AppUser owner);
	Optional<Task> findByIdAndOwner(UUID id, AppUser owner);
}