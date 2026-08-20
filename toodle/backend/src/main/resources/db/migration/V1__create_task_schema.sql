-- Creates the original task and category tables.
CREATE TABLE category (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(1) NOT NULL
);

CREATE TABLE task (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    start_date DATE,
    start_time TIME,
    due_date DATE,
    due_time TIME,
    priority VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    category_id UUID REFERENCES category(id) ON DELETE SET NULL
);

CREATE INDEX idx_task_category_id ON task(category_id);
CREATE INDEX idx_task_due_date ON task(due_date);
