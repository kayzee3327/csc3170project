DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management;

USE library_management;

-- Table to store user details (Librarians and Patrons)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('librarian', 'patron') NOT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100)
);

-- Table to store book details
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    published_year INT NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    copies INT NOT NULL
);

-- Table to store borrow transactions
CREATE TABLE borrows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patron_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    return_date DATETIME,
    FOREIGN KEY (patron_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Table to store complaints by patrons
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patron_id INT NOT NULL,
    title TEXT,
    content TEXT,
    status ENUM('open', 'resolved') DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    reply TEXT,
    FOREIGN KEY (patron_id) REFERENCES users(id)
);
