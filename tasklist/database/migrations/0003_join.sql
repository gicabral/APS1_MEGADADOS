ALTER TABLE
    tasks ADD user_uuid BINARY(16);
ALTER TABLE
    tasks ADD FOREIGN KEY (user_uuid) 
    REFERENCES users(uuid) 
    ON DELETE CASCADE;
