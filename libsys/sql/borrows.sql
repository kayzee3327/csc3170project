-- Insert Borrow Transactions
INSERT INTO borrows (patron_id, book_id, borrow_date, return_date) VALUES
(3, 1, '2024-10-01 10:00:00', '2024-10-10 10:00:00'),  -- Patron 3 borrowed "Introduction to Programming"
(4, 2, '2024-10-02 11:00:00', '2024-10-08 14:00:00'),  -- Patron 4 borrowed "Data Structures and Algorithms"
(5, 3, '2024-10-03 12:00:00', '2024-10-12 15:00:00'),  -- Patron 5 borrowed "Database Management Systems"
(2, 4, '2024-10-04 13:00:00', NULL),                    -- Patron 2 borrowed "Artificial Intelligence Basics" (not returned yet)
(3, 5, '2024-10-05 09:00:00', NULL),                    -- Patron 3 borrowed "Machine Learning for Beginners" (not returned yet)
(1, 6, '2024-10-06 14:00:00', '2024-10-15 16:00:00');  -- Patron 1 borrowed "Python Programming"
