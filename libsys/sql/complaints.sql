-- Insert Complaints
INSERT INTO complaints (patron_id, title, content, status, created_at, resolved_at, reply) VALUES
(3, 'Book Damaged', 'The book I borrowed is damaged.', 'open', '2024-10-05 10:00:00', NULL, NULL),  -- Patron 3 has an open complaint
(5, 'No book', 'I couldn''t borrow the book I wanted.', 'resolved', '2024-10-06 12:00:00', '2024-10-06 14:00:00', 'Sorry'),  -- Patron 5 has a resolved complaint
(4, 'Delay', 'There was a delay in the book delivery.', 'open', '2024-10-07 09:00:00', NULL, NULL),  -- Patron 4 has an open complaint
(2, 'System Failure', 'The library system is not functioning properly.', 'resolved', '2024-10-08 11:00:00', '2024-10-09 13:00:00', 'Sorry');  -- Patron 2 has a resolved complaint
