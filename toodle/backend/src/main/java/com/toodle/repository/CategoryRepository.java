package com.toodle.repository;

import com.toodle.model.Category;
import com.toodle.model.AppUser;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CategoryRepository extends JpaRepository<Category, UUID> {
	List<Category> findAllByOwner(AppUser owner);
	Optional<Category> findByIdAndOwner(UUID id, AppUser owner);
}