DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management;

USE library_management;

-- Table to store book categories
CREATE TABLE book_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- Table to store user details (Librarians and students)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('librarian', 'student') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_username (username),
    INDEX idx_users_email (email)
);

-- Table to store book details
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    published_year INT CHECK (published_year <= YEAR(CURRENT_DATE)),
    isbn VARCHAR(20) NOT NULL UNIQUE,
    copies INT NOT NULL DEFAULT 1 CHECK (copies >= 0),
    category_id INT,
    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES book_categories(category_id),
    INDEX idx_books_title (title),
    INDEX idx_books_author (author),
    INDEX idx_books_isbn (isbn)
);

-- Table to store borrow transactions
CREATE TABLE borrows (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NOT NULL,
    return_date DATETIME,
    status ENUM('active', 'returned', 'overdue', 'lost') DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id),
    INDEX idx_borrows_user (user_id),
    INDEX idx_borrows_book (book_id),
    INDEX idx_borrows_status (status)
);

-- Table to store complaints by students
CREATE TABLE complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    resolved_by INT,
    reply TEXT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (resolved_by) REFERENCES USERS(user_id),
    INDEX idx_complaints_status (status),
    INDEX idx_complaints_user (user_id)
);

-- Table to store book reservations
CREATE TABLE book_reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    reservation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME NOT NULL,
    status ENUM('pending', 'fulfilled', 'cancelled', 'expired') DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (book_id) REFERENCES BOOKS(book_id),
    INDEX idx_reservations_user (user_id),
    INDEX idx_reservations_book (book_id),
    INDEX idx_reservations_status (status)
);

-- Table to store system logs
CREATE TABLE systen_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    INDEX idx_logs_user (user_id),
    INDEX idx_logs_action (action),
    INDEX idx_logs_timestamp (timestamp)
);