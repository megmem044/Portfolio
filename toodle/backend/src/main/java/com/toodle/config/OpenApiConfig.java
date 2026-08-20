package com.toodle.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Defines the public API identity and JWT authentication contract. */
@Configuration
public class OpenApiConfig {
    @Bean
    OpenAPI toodleOpenApi() {
        return new OpenAPI()
            .info(new Info()
                .title("Toodle API")
                .version("v1")
                .description("Authentication, task, and category API used by the Toodle BFF."))
            .components(new Components().addSecuritySchemes("bearerAuth", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")));
    }
}
