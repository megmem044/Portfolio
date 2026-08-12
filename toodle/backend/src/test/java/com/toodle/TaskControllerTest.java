package com.toodle;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import com.jayway.jsonpath.JsonPath;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class TaskControllerTest {
    @Autowired
    private MockMvc mockMvc;
    private String authorization;

    @BeforeEach
    void registerUser() throws Exception {
        String email = "user" + System.nanoTime() + "@example.com";
        String response = mockMvc.perform(post("/api/auth/register").contentType("application/json").content("{\"name\":\"Test User\",\"email\":\"" + email + "\",\"password\":\"password123\"}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.token").isNotEmpty())
            .andReturn().getResponse().getContentAsString();
        authorization = "Bearer " + JsonPath.read(response, "$.token");
    }

    @Test
    void returnsAnEmptyTaskList() throws Exception {
        mockMvc.perform(get("/api/tasks").header("Authorization", authorization))
            .andExpect(status().isOk())
            .andExpect(content().json("[]"));
    }

    @Test
    void rejectsAnUnauthenticatedTaskRequest() throws Exception {
        mockMvc.perform(get("/api/tasks"))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("AUTHENTICATION_REQUIRED"))
            .andExpect(jsonPath("$.correlationId").isNotEmpty());
    }

    @Test
    void rejectsAnInvalidToken() throws Exception {
        mockMvc.perform(get("/api/tasks").header("Authorization", "Bearer not-a-valid-token"))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("AUTHENTICATION_REQUIRED"));
    }

    @Test
    void rejectsDuplicateRegistrationAndInvalidRegistrationData() throws Exception {
        String email = "duplicate" + System.nanoTime() + "@example.com";
        String registration = "{\"name\":\"Test User\",\"email\":\"" + email + "\",\"password\":\"password123\"}";
        mockMvc.perform(post("/api/auth/register").contentType("application/json").content(registration)).andExpect(status().isCreated());
        mockMvc.perform(post("/api/auth/register").contentType("application/json").content(registration))
            .andExpect(status().isConflict())
            .andExpect(jsonPath("$.code").value("RESOURCE_CONFLICT"));
        mockMvc.perform(post("/api/auth/register").contentType("application/json").content("{\"name\":\"\",\"email\":\"invalid\",\"password\":\"short\"}"))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }

    @Test
    void rejectsWrongCredentialsAndMalformedJson() throws Exception {
        String email = "login" + System.nanoTime() + "@example.com";
        registerUser(email);
        mockMvc.perform(post("/api/auth/login").contentType("application/json").content("{\"email\":\"" + email + "\",\"password\":\"wrong-password\"}"))
            .andExpect(status().isUnauthorized()).andExpect(jsonPath("$.code").value("AUTHENTICATION_FAILED"));
        mockMvc.perform(post("/api/auth/login").contentType("application/json").content("{not-json}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.code").value("MALFORMED_REQUEST"));
    }

    @Test
    void rejectsInvalidTaskSchedules() throws Exception {
        mockMvc.perform(post("/api/tasks").header("Authorization", authorization).contentType("application/json")
                .content("{\"title\":\"Invalid date\",\"startDate\":\"2026-08-13\",\"dueDate\":\"2026-08-12\",\"priority\":\"LOW\"}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.message").value("Due date cannot be before start date"));
        mockMvc.perform(post("/api/tasks").header("Authorization", authorization).contentType("application/json")
                .content("{\"title\":\"Invalid time\",\"startTime\":\"09:00\",\"priority\":\"LOW\"}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.message").value("Start time requires a start date"));
    }

    @Test
    void preventsCrossUserTaskAndCategoryAccess() throws Exception {
        String ownerAuthorization = registerUser("owner" + System.nanoTime() + "@example.com");
        String otherAuthorization = registerUser("other" + System.nanoTime() + "@example.com");

        String category = mockMvc.perform(post("/api/categories").header("Authorization", ownerAuthorization).contentType("application/json").content("{\"name\":\"Private\",\"color\":\"3\"}"))
            .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        String categoryId = JsonPath.read(category, "$.id");
        String task = mockMvc.perform(post("/api/tasks").header("Authorization", ownerAuthorization).contentType("application/json").content("{\"title\":\"Owner task\",\"priority\":\"LOW\",\"categoryId\":\"" + categoryId + "\"}"))
            .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        String taskId = JsonPath.read(task, "$.id");

        mockMvc.perform(get("/api/tasks/{id}", taskId).header("Authorization", otherAuthorization)).andExpect(status().isNotFound());
        mockMvc.perform(put("/api/tasks/{id}", taskId).header("Authorization", otherAuthorization).contentType("application/json").content("{\"title\":\"Stolen\",\"priority\":\"HIGH\"}")).andExpect(status().isNotFound());
        mockMvc.perform(delete("/api/tasks/{id}", taskId).header("Authorization", otherAuthorization)).andExpect(status().isNotFound());
        mockMvc.perform(put("/api/categories/{id}", categoryId).header("Authorization", otherAuthorization).contentType("application/json").content("{\"name\":\"Stolen\",\"color\":\"4\"}")).andExpect(status().isNotFound());
        mockMvc.perform(delete("/api/categories/{id}", categoryId).header("Authorization", otherAuthorization)).andExpect(status().isNotFound());
        mockMvc.perform(post("/api/tasks").header("Authorization", otherAuthorization).contentType("application/json").content("{\"title\":\"Cross category\",\"priority\":\"LOW\",\"categoryId\":\"" + categoryId + "\"}"))
            .andExpect(status().isNotFound());

        mockMvc.perform(get("/api/tasks/{id}", taskId).header("Authorization", ownerAuthorization)).andExpect(status().isOk());
    }

    @Test
    void preventsDuplicateCategoryNamesAndClearsCategoryOnDelete() throws Exception {
        String created = mockMvc.perform(post("/api/categories").header("Authorization", authorization).contentType("application/json").content("{\"name\":\"  Work  \",\"color\":\"3\"}"))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.name").value("Work")).andReturn().getResponse().getContentAsString();
        String categoryId = JsonPath.read(created, "$.id");
        mockMvc.perform(post("/api/categories").header("Authorization", authorization).contentType("application/json").content("{\"name\":\"work\",\"color\":\"4\"}"))
            .andExpect(status().isConflict()).andExpect(jsonPath("$.code").value("RESOURCE_CONFLICT"));
        String task = mockMvc.perform(post("/api/tasks").header("Authorization", authorization).contentType("application/json").content("{\"title\":\"Categorized\",\"priority\":\"LOW\",\"categoryId\":\"" + categoryId + "\"}"))
            .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        String taskId = JsonPath.read(task, "$.id");
        mockMvc.perform(delete("/api/categories/{id}", categoryId).header("Authorization", authorization)).andExpect(status().isNoContent());
        mockMvc.perform(get("/api/tasks/{id}", taskId).header("Authorization", authorization)).andExpect(status().isOk()).andExpect(jsonPath("$.categoryId").doesNotExist());
    }

    @Test
    void createsAndListsATask() throws Exception {
        String request = """
            {"title":"Backend task","description":"Created through REST","startDate":"2026-08-12","startTime":"09:00","dueDate":"2026-08-12","dueTime":"10:00","priority":"MEDIUM"}
            """;

        mockMvc.perform(post("/api/tasks").header("Authorization", authorization).contentType("application/json").content(request))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.title").value("Backend task"))
            .andExpect(jsonPath("$.priority").value("medium"));

        mockMvc.perform(get("/api/tasks").header("Authorization", authorization))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].title").value("Backend task"));
    }

    @Test
    void retrievesUpdatesAndDeletesATask() throws Exception {
        String created = mockMvc.perform(post("/api/tasks").header("Authorization", authorization).contentType("application/json").content("{\"title\":\"Original\",\"priority\":\"LOW\"}"))
            .andExpect(status().isCreated())
            .andReturn().getResponse().getContentAsString();
        String taskId = JsonPath.read(created, "$.id");

        mockMvc.perform(get("/api/tasks/{id}", taskId).header("Authorization", authorization)).andExpect(status().isOk()).andExpect(jsonPath("$.title").value("Original"));
        mockMvc.perform(put("/api/tasks/{id}", taskId).header("Authorization", authorization).contentType("application/json").content("{\"title\":\"Updated\",\"priority\":\"HIGH\",\"completed\":true}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.title").value("Updated"))
            .andExpect(jsonPath("$.isCompleted").value(true));
        mockMvc.perform(delete("/api/tasks/{id}", taskId).header("Authorization", authorization)).andExpect(status().isNoContent());
        mockMvc.perform(get("/api/tasks/{id}", taskId).header("Authorization", authorization)).andExpect(status().isNotFound());
    }

    @Test
    void createsUpdatesAndDeletesACategory() throws Exception {
        String created = mockMvc.perform(post("/api/categories").header("Authorization", authorization).contentType("application/json").content("{\"name\":\"Work\",\"color\":\"3\"}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("Work"))
            .andReturn().getResponse().getContentAsString();
        String categoryId = JsonPath.read(created, "$.id");

        mockMvc.perform(put("/api/categories/{id}", categoryId).header("Authorization", authorization).contentType("application/json").content("{\"name\":\"Projects\",\"color\":\"4\"}"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Projects"));
        mockMvc.perform(delete("/api/categories/{id}", categoryId).header("Authorization", authorization)).andExpect(status().isNoContent());
    }

    private String registerUser(String email) throws Exception {
        String response = mockMvc.perform(post("/api/auth/register").contentType("application/json").content("{\"name\":\"Isolation User\",\"email\":\"" + email + "\",\"password\":\"password123\"}"))
            .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        return "Bearer " + JsonPath.read(response, "$.token");
    }
}
