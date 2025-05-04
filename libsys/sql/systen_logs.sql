-- 用户登录日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'User Login', 'users', 1, '{"username": "admin1", "role": "librarian"}', '2025-01-05 08:30:15'),
(2, 'User Login', 'users', 2, '{"username": "admin2", "role": "librarian"}', '2025-01-05 09:15:22'),
(3, 'User Login', 'users', 3, '{"username": "student1", "role": "student"}', '2025-01-05 10:20:45'),
(4, 'User Login', 'users', 4, '{"username": "student2", "role": "student"}', '2025-01-05 11:05:32'),
(5, 'User Login', 'users', 5, '{"username": "student3", "role": "student"}', '2025-01-05 13:17:28'),
(6, 'User Login', 'users', 6, '{"username": "student4", "role": "student"}', '2025-01-05 14:30:11'),
(7, 'User Login', 'users', 7, '{"username": "student5", "role": "student"}', '2025-01-05 15:45:52'),
(1, 'User Login', 'users', 1, '{"username": "admin1", "role": "librarian"}', '2025-01-06 08:25:30'),
(2, 'User Login', 'users', 2, '{"username": "admin2", "role": "librarian"}', '2025-01-06 09:10:18'),
(3, 'User Login', 'users', 3, '{"username": "student1", "role": "student"}', '2025-01-06 10:35:21');

-- 图书管理日志（添加、更新、删除）
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'Book Added', 'books', 31, '{"title": "Cloud Native Patterns", "author": "Cornelia Davis", "isbn": "978-1617294969", "copies": 3, "category_id": 11}', '2025-01-07 09:30:45'),
(1, 'Book Added', 'books', 32, '{"title": "Practical MLOps", "author": "Noah Gift", "isbn": "978-1098103019", "copies": 2, "category_id": 12}', '2025-01-07 09:45:22'),
(2, 'Book Added', 'books', 33, '{"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "isbn": "978-1449373320", "copies": 5, "category_id": 3}', '2025-01-07 10:15:18'),
(1, 'Book Updated', 'books', 31, '{"title": "Cloud Native Patterns", "author": "Cornelia Davis", "isbn": "978-1617294969", "copies": 5, "category_id": 11}', '2025-01-08 11:20:35'),
(2, 'Book Updated', 'books', 12, '{"title": "iOS Programming with Swift", "author": "Tim Cook", "isbn": "978-2233445566", "copies": 5, "category_id": 7}', '2025-01-08 13:40:12'),
(2, 'Book Deleted', 'books', 34, '{"title": "Legacy Title", "author": "Unknown Author", "isbn": "978-0000000000"}', '2025-01-09 14:25:42');

-- 图书借阅操作日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(3, 'Book Borrowed', 'books', 1, '{"borrow_id": 100, "borrow_date": "2025-01-10 10:15:22"}', '2025-01-10 10:15:22'),
(4, 'Book Borrowed', 'books', 5, '{"borrow_id": 101, "borrow_date": "2025-01-10 11:30:45"}', '2025-01-10 11:30:45'),
(5, 'Book Borrowed', 'books', 8, '{"borrow_id": 102, "borrow_date": "2025-01-10 13:45:18"}', '2025-01-10 13:45:18'),
(6, 'Book Borrowed', 'books', 15, '{"borrow_id": 103, "borrow_date": "2025-01-10 14:20:33"}', '2025-01-10 14:20:33'),
(7, 'Book Borrowed', 'books', 22, '{"borrow_id": 104, "borrow_date": "2025-01-10 15:10:52"}', '2025-01-10 15:10:52'),
(3, 'Book Returned', 'books', 1, '{"borrow_id": 100, "return_date": "2025-01-17 09:30:15"}', '2025-01-17 09:30:15'),
(4, 'Book Returned', 'books', 5, '{"borrow_id": 101, "return_date": "2025-01-18 10:45:22"}', '2025-01-18 10:45:22'),
(5, 'Book Returned', 'books', 8, '{"borrow_id": 102, "return_date": "2025-01-17 14:15:48"}', '2025-01-17 14:15:48');

-- 图书预约操作日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(3, 'Book Reserved', 'books', 10, '{"reservation_id": 1, "expiry_date": "2025-01-19 10:30:00"}', '2025-01-12 10:30:00'),
(4, 'Book Reserved', 'books', 16, '{"reservation_id": 2, "expiry_date": "2025-01-19 11:45:00"}', '2025-01-12 11:45:00'),
(5, 'Book Reserved', 'books', 23, '{"reservation_id": 3, "expiry_date": "2025-01-19 13:20:00"}', '2025-01-12 13:20:00'),
(3, 'Reservation Cancelled', 'books', 10, '{"reservation_id": 1}', '2025-01-13 09:15:30'),
(4, 'Reservation Fulfilled', 'books', 16, '{"reservation_id": 2, "borrow_id": 105}', '2025-01-14 10:25:45');

-- 投诉处理日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(3, 'Complaint Submitted', 'complaints', 16, '{"title": "Unable to Reserve Popular Book", "content": "When I tried to reserve \'Artificial Intelligence: A Modern Approach\', the system kept giving an error."}', '2025-01-15 10:30:15'),
(4, 'Complaint Submitted', 'complaints', 17, '{"title": "Book Damage Issue", "content": "The \'Deep Learning for Computer Vision\' book I borrowed has several torn pages, affecting readability."}', '2025-01-15 11:20:45'),
(5, 'Complaint Submitted', 'complaints', 18, '{"title": "Borrowing History Error", "content": "My borrowing history shows that I have not returned \'Database Management Systems\', but I actually returned it last week."}', '2025-01-15 13:45:22'),

(1, 'Complaint Resolved', 'complaints', 16, '{"reply": "The issue in the reservation system has been fixed. You should now be able to make reservations normally. Thank you for your feedback!", "resolved_at": "2025-01-16 09:20:30", "resolved_by": 1}', '2025-01-16 09:20:30'),
(2, 'Complaint Resolved', 'complaints', 17, '{"reply": "We sincerely apologize for the inconvenience. A new copy of the book has been provided, and you may exchange it at the front desk. Additionally, we have strengthened the book damage inspection process.", "resolved_at": "2025-01-16 10:15:45", "resolved_by": 2}', '2025-01-16 10:15:45');


-- 分类管理日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'Category Added', 'categories', 16, '{"name": "DevOps and SRE", "description": "Books about DevOps practices, Site Reliability Engineering, and Continuous Integration/Deployment."}', '2025-01-17 09:30:45'),
(2, 'Category Added', 'categories', 17, '{"name": "Quantum Computing", "description": "Books related to quantum computing, quantum algorithms, and quantum information science."}', '2025-01-17 10:15:22'),
(1, 'Category Updated', 'categories', 16, '{"name": "DevOps, SRE and Platform Engineering", "description": "Books about DevOps practices, Site Reliability Engineering, Platform Engineering, and Continuous Integration/Deployment."}', '2025-01-18 11:20:35'),
(2, 'Category Updated', 'categories', 7, '{"name": "Mobile App Development", "description": "Books related to mobile app development, including iOS, Android, and cross-platform development."}', '2025-01-18 13:40:12'),
(1, 'Category Deleted with Books', 'categories', 17, '{"name": "Quantum Computing", "books_deleted": 0}', '2025-01-19 14:25:42');


-- 用户注册日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(NULL, 'User Registration', 'users', 8, '{"username": "student6", "role": "student", "full_name": "Frank Johnson", "email": "frank.johnson@cuhk.edu.cn"}', '2025-01-20 10:15:30'),
(NULL, 'User Registration', 'users', 9, '{"username": "student7", "role": "student", "full_name": "Helen Davis", "email": "helen.davis@cuhk.edu.cn"}', '2025-01-20 11:30:45'),
(NULL, 'User Registration', 'users', 10, '{"username": "student8", "role": "student", "full_name": "Ian Wilson", "email": "ian.wilson@cuhk.edu.cn"}', '2025-01-20 13:45:22');

-- 一些例行管理操作的日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'System Backup', 'system', NULL, '{"backup_file": "library_management_20250121.sql", "backup_size": "15.7MB"}', '2025-01-21 23:00:00'),
(2, 'Book Inventory Check', 'inventory', NULL, '{"total_books": 33, "books_available": 25, "books_borrowed": 8, "books_missing": 0}', '2025-01-22 16:30:45'),
(1, 'System Configuration Update', 'system', NULL, '{"updated_settings": ["borrow_period", "max_borrows_per_user"], "previous_values": {"borrow_period": 7, "max_borrows_per_user": 5}, "new_values": {"borrow_period": 14, "max_borrows_per_user": 7}}', '2025-01-23 09:15:22'),
(2, 'User Account Maintenance', 'users', NULL, '{"inactive_accounts_archived": 2, "password_resets_requested": 3}', '2025-01-24 14:45:30'),
(1, 'System Backup', 'system', NULL, '{"backup_file": "library_management_20250128.sql", "backup_size": "16.2MB"}', '2025-01-28 23:00:00');

-- 系统性能监控日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(NULL, 'System Performance Check', 'system', NULL, '{"database_size": "23.4MB", "query_response_time_avg": "45ms", "active_connections": 12, "cpu_usage": "32%", "memory_usage": "45%"}', '2025-01-25 03:00:00'),
(NULL, 'System Alert', 'system', NULL, '{"alert_type": "High Traffic", "connections": 25, "time_period": "10:30-11:30", "recommended_action": "Monitor system resources"}', '2025-01-25 11:35:22'),
(NULL, 'System Performance Check', 'system', NULL, '{"database_size": "23.5MB", "query_response_time_avg": "43ms", "active_connections": 5, "cpu_usage": "28%", "memory_usage": "42%"}', '2025-01-26 03:00:00'),
(NULL, 'System Alert', 'system', NULL, '{"alert_type": "Slow Query Detected", "query_id": "SELECT-20250127-001", "execution_time": "3.2s", "recommended_action": "Optimize query or add index"}', '2025-01-27 14:22:15'),
(NULL, 'System Performance Check', 'system', NULL, '{"database_size": "23.6MB", "query_response_time_avg": "40ms", "active_connections": 8, "cpu_usage": "30%", "memory_usage": "43%"}', '2025-01-27 03:00:00');

-- 书籍异常处理日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'Book Reported Damaged', 'books', 8, '{"reported_by": 5, "damage_description": "Water damage affecting multiple pages", "action_taken": "Replaced with a new copy."}', '2025-01-28 10:25:45'),
(2, 'Book Reported Lost', 'books', 15, '{"reported_by": 6, "compensation_fee": 125.00, "status": "Paid"}', '2025-01-28 13:40:22'),
(1, 'Book Acquisition Request', 'books', NULL, '{"requested_title": "The DevOps Handbook", "author": "Gene Kim", "isbn": "978-1942788003", "requested_by": 3, "status": "Approved"}', '2025-01-29 09:15:30'),
(2, 'Book Acquisition Request', 'books', NULL, '{"requested_title": "Clean Architecture", "author": "Robert C. Martin", "isbn": "978-0134494166", "requested_by": 4, "status": "Under Review"}', '2025-01-29 10:30:45'),
(1, 'Book Condition Update', 'books', 23, '{"previous_condition": "Good", "new_condition": "Needs Repair", "action_taken": "Temporarily removed from shelves and sent for repair."}', '2025-01-30 11:45:22');

-- 数据分析和报告生成日志
INSERT INTO systen_logs (user_id, action, entity_type, entity_id, details, timestamp) VALUES
(1, 'Report Generated', 'report', NULL, '{"report_type": "Monthly Borrowing Statistics", "period": "January 2025", "total_borrows": 87, "total_returns": 79, "popular_category": "Artificial Intelligence"}', '2025-01-31 15:30:45'),
(2, 'Report Generated', 'report', NULL, '{"report_type": "User Activity Analysis", "period": "January 2025", "most_active_user": "student3", "least_active_user": "student7", "avg_books_per_user": 3.5}', '2025-01-31 16:15:22'),
(1, 'Report Generated', 'report', NULL, '{"report_type": "Book Circulation Analysis", "period": "January 2025", "highest_circulation": "Artificial Intelligence: A Modern Approach", "lowest_circulation": "Theory of Computation", "avg_days_borrowed": 7.8}', '2025-01-31 17:00:30');
