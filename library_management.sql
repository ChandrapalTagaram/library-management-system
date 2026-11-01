-- Library Management System Database

-- Database: MySQL

CREATE DATABASE IF NOT EXISTS library_management;

USE library_management;

-- 1. Books Table
CREATE TABLE IF NOT EXISTS books (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL
);

-- 3. Issued Books Table
CREATE TABLE IF NOT EXISTS issued_books (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    student_id INT NOT NULL,
    issue_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- Display all tables
SHOW TABLES;

-- View all books
SELECT * FROM books;

-- View all students
SELECT * FROM students;

-- View all issued books
SELECT * FROM issued_books;

-- View books with their issue history
SELECT
    b.book_id,
    b.title,
    b.author,
    b.quantity,
    ib.issue_id,
    ib.return_date
FROM books b
LEFT JOIN issued_books ib
    ON b.book_id = ib.book_id
ORDER BY b.book_id;