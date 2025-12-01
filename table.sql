CREATE TABLE authorized_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    endat INT,
    admin BOOLEAN DEFAULT FALSE
);
