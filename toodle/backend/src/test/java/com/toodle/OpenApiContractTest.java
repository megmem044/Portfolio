// Verifies and exports the Spring OpenAPI contract used by the BFF.
package com.toodle;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

/** Guards the main routes, schemas, and JWT requirement published in OpenAPI. */
@SpringBootTest
@AutoConfigureMockMvc
class OpenApiContractTest {
    @Autowired
    private MockMvc mockMvc;

    @Test
    void publishesTheApiContractWithoutAuthentication() throws Exception {
        String contract = mockMvc.perform(get("/v3/api-docs"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.info.title").value("Toodle API"))
            .andExpect(jsonPath("$.info.version").value("v1"))
            .andExpect(jsonPath("$.paths['/api/auth/login'].post").exists())
            .andExpect(jsonPath("$.paths['/api/auth/register'].post").exists())
            .andExpect(jsonPath("$.paths['/api/tasks'].get.security[0].bearerAuth").isArray())
            .andExpect(jsonPath("$.paths['/api/categories'].get.security[0].bearerAuth").isArray())
            .andExpect(jsonPath("$.components.securitySchemes.bearerAuth.scheme").value("bearer"))
            .andExpect(jsonPath("$.components.schemas.TaskRequest").exists())
            .andExpect(jsonPath("$.components.schemas.TaskResponse").exists())
            .andExpect(jsonPath("$.components.schemas.CategoryRequest").exists())
            .andExpect(jsonPath("$.components.schemas.CategoryResponse").exists())
            .andReturn()
            .getResponse()
            .getContentAsString();

        Files.createDirectories(Path.of("target"));
        Files.writeString(Path.of("target", "openapi.json"), contract);
    }
}
