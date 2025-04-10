-- Insert Librarians
INSERT INTO users (username, password, role, full_name, email) VALUES
('admin1', 'password123', 'librarian', 'Alice Green', 'alice.green@cuhk.edu.cn'),
('admin2', 'password123', 'librarian', 'Bob White', 'bob.white@cuhk.edu.cn');

-- Insert Patrons
INSERT INTO users (username, password, role, full_name, email) VALUES
('patron1', 'password123', 'patron', 'Charlie Brown', 'charlie.brown@cuhk.edu.cn'),
('patron2', 'password123', 'patron', 'David Smith', 'david.smith@cuhk.edu.cn'),
('patron3', 'password123', 'patron', 'Eve Black', 'eve.black@cuhk.edu.cn'),
('patron4', 'password123', 'patron', 'Grace Lee', 'grace.lee@cuhk.edu.cn'),
('patron5', 'password123', 'patron', 'Hank Miller', 'hank.miller@cuhk.edu.cn');
