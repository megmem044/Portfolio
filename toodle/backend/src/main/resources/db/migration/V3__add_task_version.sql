-- Adds optimistic locking so an old task edit cannot overwrite a newer one.
ALTER TABLE task ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
