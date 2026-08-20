// Signals that an owner-scoped resource could not be found.
package com.toodle.exception;

import java.util.UUID;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String resource, UUID id) {
        super(resource + " with id " + id + " was not found");
    }
}
