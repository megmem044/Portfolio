-- Adds accounts and connects existing data to an owner.
CREATE TABLE app_user (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

ALTER TABLE category ADD COLUMN owner_id UUID REFERENCES app_user(id) ON DELETE CASCADE;
ALTER TABLE task ADD COLUMN owner_id UUID REFERENCES app_user(id) ON DELETE CASCADE;

CREATE INDEX idx_category_owner_id ON category(owner_id);
CREATE INDEX idx_task_owner_id ON task(owner_id);
