CREATE DATABASE IF NOT EXISTS quiz_app;
USE quiz_app;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    question_text VARCHAR(255) NOT NULL,
    correct_option INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS options (
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_number INT NOT NULL,
    option_text VARCHAR(100) NOT NULL,
    UNIQUE(question_id, option_number),
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
        ON DELETE CASCADE
);

INSERT IGNORE INTO categories VALUES
(1, 'Countries and their capitals'),
(2, 'Countries and their currencies'),
(3, 'Indian States and their capitals');

-- Import the question rows from the original database.txt after creating
-- the schema, or use project.py with SQLite as the default local database.
