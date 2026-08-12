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
            .andExpect(status().isForbidden());
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
}