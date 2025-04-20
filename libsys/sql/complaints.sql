-- Insert Complaints
INSERT INTO complaints (student_id, title, content, status, created_at, resolved_at, reply) VALUES
(3, 'Book Damaged', 'The book I borrowed is damaged.', 'open', '2025-4-05 13:00:00', NULL, NULL),  -- student 1 has an open complaint
(5, 'No book', 'I couldn''t borrow the book I wanted.', 'resolved', '2025-4-06 12:00:00', '2025-4-06 14:00:00', 'Sorry'),  -- student 3 has a resolved complaint
(4, 'Delay', 'There was a delay in the book delivery.', 'open', '2025-4-07 09:00:00', NULL, NULL),  -- student 2 has an open complaint
(4, 'System Failure', 'The library system is not functioning properly.', 'resolved', '2025-4-08 11:00:00', '2025-4-09 13:00:00', 'Sorry');  -- student 2 has a resolved complaint
