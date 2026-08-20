// Defines category data returned by the API.
package com.toodle.dto;

import com.toodle.model.Category;
import java.util.UUID;

public record CategoryResponse(UUID id, String name, String color) {
    public static CategoryResponse from(Category category) {
        return new CategoryResponse(category.getId(), category.getName(), category.getColor());
    }
}
