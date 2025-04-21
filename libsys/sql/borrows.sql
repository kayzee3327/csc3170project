-- Insert Borrow Transactions
INSERT INTO borrows (user_id, book_id, borrow_date, due_date, return_date) VALUES
(3, 1, '2025-4-01 10:00:00', '2025-4-08 10:00:00', '2025-4-04 12:00:00'),  -- student 1 borrowed "Introduction to Programming"
(4, 2, '2025-4-02 11:00:00', '2025-4-09 11:00:00', '2025-4-08 14:00:00'),  -- student 2 borrowed "Data Structures and Algorithms"
(5, 3, '2025-4-03 12:00:00', '2025-4-10 12:00:00', '2025-4-12 15:00:00'),  -- student 3 borrowed "Database Management Systems"
(4, 4, '2025-4-04 13:00:00', '2025-4-11 13:00:00', NULL),                  -- student 2 borrowed "Artificial Intelligence Basics" (not returned yet)
(5, 5, '2025-4-05 09:00:00', '2025-4-12 09:00:00', NULL),                  -- student 3 borrowed "Machine Learning for Beginners" (not returned yet)
(3, 6, '2025-4-06 14:00:00', '2025-4-13 14:00:00', '2025-4-15 16:00:00');  -- student 1 borrowed "Python Programming"
