-- Data for users
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (2, 'Dr. Sharma', 'sharma@college.edu', '$2b$12$QDmOTvNiHjN3EguYAJy7ueqBgOWHgeauczLj9MHskrZOfTZXf4okC', 'teacher', 'CSE', 'TCH-1234', 1, '2026-03-14 05:16:02.926314', NULL);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (3, 'Prof. Iyer', 'iyer@college.edu', '$2b$12$XMAM9o4AawiRLRICNnpb6uVjcftsef9ulzllIMPHM0tLQ9x2fNGx2', 'hod', 'CSE', 'HOD-1234', 1, '2026-03-14 05:16:03.305106', NULL);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (4, 'System Admin', 'admin@classsync.app', '$2b$12$tiHjQT/m0e7c04RUBYav/.E52fpplyGQyxOnnAg.oq3U5EabiQaZS', 'admin', 'Admin', 'ADM-1234', 1, '2026-03-14 05:16:03.305109', NULL);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (6, 'Pravin Shinde', 'shinde.pravin1912@gmail.com', '$2b$12$3dJdVhZac6oGMaDHENp/peGl9lE6LhrmqA4xcZ9HQwGzu/tBAWZYG', 'student', 'CSE', 'STU-1222', 1, '2026-03-14 10:57:32.372783', 0);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (7, 'Vignesh', 'vignesh.mudaliar2005@gmail.com', '$2b$12$wQPox9M/TCSH/co.fZdvieNu.HDJb0U2Jdn733DAp.SDgBA390RDy', 'student', 'CSE', 'STU-1255', 1, '2026-03-14 16:54:29.155117', 1);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (8, 'Sapna Malpani', '1912vmudaliar@gmail.com', '$2b$12$64AijgERs6UQzHxTM5p3vOOMkUbbYXL9QQMljWke5uv20UJcfh9Ba', 'teacher', 'CSE', 'TCH-1221', 1, '2026-03-14 17:01:27.350466', 1);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (9, 'Mahadeo Pisal', 'vigneshmudaliar2024@gmail.com', '$2b$12$dlh/zLkNKzzL4vseVXOAMufTImrx.NOJag8.ycCJBINlBSU8k8/Vi', 'hod', 'CSE', 'HOD-2000', 1, '2026-03-14 18:37:52.787397', 1);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (10, 'Amaan Shaikh', '666thedarkshop@gmail.com', '$2b$12$xcpqFm7rgnDCNsrQpMVXLuT5oei2na81hmeQ.E86NoqLyOOIP8OxW', 'admin', NULL, 'ADM-7777', 1, '2026-03-15 18:27:25.227449', 1);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (11, 'Swaraj Deshmukh', 'swarajdeshmukh850@gmail.com', '$2b$12$11Kl1kvcDnqbNeZv9N97EeWl6A88utoCClHCjSgRF46emFECD3Ct6', 'admin', NULL, 'ADM-0007', 1, '2026-03-16 06:48:38.676028', 1);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (12, 'Swaruuu Sir', 'sewyswaraj107@gmail.com', 'scrypt:32768:8:1$WPdEOY57pZGM0xbz$6f7b4baa7644f9e63dd1373c19a51cffa827853ecc3c593295420d99b839a1acc9c63741ac2e9abd4147dd7bd667c7269a9e306c60de6fcc9254a6d292e901fb', 'teacher', 'CSE', 'TCH-1223', 1, '2026-03-16 06:51:59.548805', 0);
INSERT INTO users (id, name, email, password_hash, role, department, college_user_id, is_active, created_at, is_verified) VALUES (13, 'Swaruuu Sir', 'sewyswaraj710@gmail.com', '$2b$12$5ZOiBPXtcdOexTWpD/4n6.bJ1dAsCn1esiaM.VWjQg/udGHxU5tie', 'teacher', 'IT', 'STU-1251', 1, '2026-03-16 06:54:23.216526', 1);
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));

-- Data for subjects
INSERT INTO subjects (id, subject_code, subject_name, credits, semester, department) VALUES (1, 'CS101', 'Introduction to Computer Science', 3, 1, 'CSE');
INSERT INTO subjects (id, subject_code, subject_name, credits, semester, department) VALUES (2, 'CS102', 'Data Structures', 4, 2, 'CSE');
SELECT setval('subjects_id_seq', (SELECT COALESCE(MAX(id), 1) FROM subjects));

-- Data for students
INSERT INTO students (id, user_id, class_section, semester, roll_number, batch) VALUES (3, 6, 'Semester 4 - CSE Alpha', NULL, NULL, NULL);
INSERT INTO students (id, user_id, class_section, semester, roll_number, batch) VALUES (4, 7, 'Semester 4 - CSE Alpha', NULL, NULL, NULL);
SELECT setval('students_id_seq', (SELECT COALESCE(MAX(id), 1) FROM students));

-- Data for teachers
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (1, 2, 'Assistant Professor', 'A-201');
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (2, 8, NULL, NULL);
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (3, 3, 'Head of Department', NULL);
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (4, 9, 'Head of Department', NULL);
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (5, 12, NULL, NULL);
INSERT INTO teachers (id, user_id, designation, cabin_no) VALUES (6, 13, NULL, NULL);
SELECT setval('teachers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM teachers));

-- Data for timetable
INSERT INTO timetable (id, teacher_id, subject_id, day_of_week, start_time, end_time, room_number, class_section, is_active, created_at) VALUES (1, 1, 1, 'Tuesday', '10:30:00.000000', '11:30:00.000000', '101-C', 'Semester 4-TyBsc', 0, '2026-03-14 05:25:06.467354');
INSERT INTO timetable (id, teacher_id, subject_id, day_of_week, start_time, end_time, room_number, class_section, is_active, created_at) VALUES (2, 1, 1, 'Monday', '11:00:00.000000', '11:45:00.000000', '102-A', 'Semester 4-TyBsc', 0, '2026-03-14 06:33:57.400154');
INSERT INTO timetable (id, teacher_id, subject_id, day_of_week, start_time, end_time, room_number, class_section, is_active, created_at) VALUES (3, 1, 1, 'Tuesday', '10:30:00.000000', '11:30:00.000000', '101-C', 'Semester 4 - CSE Alpha', 1, '2026-03-14 06:40:08.106006');
INSERT INTO timetable (id, teacher_id, subject_id, day_of_week, start_time, end_time, room_number, class_section, is_active, created_at) VALUES (4, 2, 2, 'Monday', '09:45:00.000000', '10:30:00.000000', '102-A', 'Semester 4 - CSE Alpha', 1, '2026-03-14 17:02:36.587503');
SELECT setval('timetable_id_seq', (SELECT COALESCE(MAX(id), 1) FROM timetable));

-- Data for attendance_sessions
INSERT INTO attendance_sessions (id, teacher_id, subject_id, session_date, start_time, end_time_limit, classroom_name, latitude, longitude, radius_meters, status, total_present, created_at) VALUES (1, 1, 1, '2026-03-14', '2026-03-14 05:57:53.970951', '2026-03-14 06:07:53.963594', '101-C', 18.44886762808756, 73.84655800399281, 50.0, 'expired', 1, '2026-03-14 05:57:53.970956');
INSERT INTO attendance_sessions (id, teacher_id, subject_id, session_date, start_time, end_time_limit, classroom_name, latitude, longitude, radius_meters, status, total_present, created_at) VALUES (2, 1, 1, '2026-03-14', '2026-03-14 06:06:01.818420', '2026-03-14 06:16:01.814561', '101-C', 18.448985522689725, 73.8465875948989, 50.0, 'expired', 0, '2026-03-14 06:06:01.818427');
INSERT INTO attendance_sessions (id, teacher_id, subject_id, session_date, start_time, end_time_limit, classroom_name, latitude, longitude, radius_meters, status, total_present, created_at) VALUES (3, 2, 2, '2026-03-14', '2026-03-14 17:24:10.589929', '2026-03-14 17:34:10.587613', '102-A', 18.448922601984762, 73.84659842645922, 50.0, 'expired', 1, '2026-03-14 17:24:10.589933');
SELECT setval('attendance_sessions_id_seq', (SELECT COALESCE(MAX(id), 1) FROM attendance_sessions));

-- Data for attendance
INSERT INTO attendance (id, session_id, student_id, marked_at, student_latitude, student_longitude, distance_from_class, status, is_valid, ip_address) VALUES (1, 1, 1, '2026-03-14 06:06:27.725374', 18.448951815026806, 73.84663003272503, 12.056323156457584, 'present', 1, '127.0.0.1');
INSERT INTO attendance (id, session_id, student_id, marked_at, student_latitude, student_longitude, distance_from_class, status, is_valid, ip_address) VALUES (2, 3, 4, '2026-03-14 17:24:45.680347', 18.448916299428827, 73.84649485024758, 10.947692900459936, 'present', 1, '127.0.0.1');
SELECT setval('attendance_id_seq', (SELECT COALESCE(MAX(id), 1) FROM attendance));

-- Data for session_activity_log
INSERT INTO session_activity_log (id, session_id, student_id, action, reason, latitude, longitude, ip_address, logged_at) VALUES (1, 1, 1, 'marked', NULL, 18.448951815026806, 73.84663003272503, '127.0.0.1', '2026-03-14 06:06:27.735927');
INSERT INTO session_activity_log (id, session_id, student_id, action, reason, latitude, longitude, ip_address, logged_at) VALUES (2, 3, 4, 'marked', NULL, 18.448916299428827, 73.84649485024758, '127.0.0.1', '2026-03-14 17:24:45.683470');
SELECT setval('session_activity_log_id_seq', (SELECT COALESCE(MAX(id), 1) FROM session_activity_log));

-- Data for notification_prefs
INSERT INTO notification_prefs (id, user_id, email_enabled, remind_3days, remind_2days, remind_1day, remind_deadline) VALUES (1, 8, 1, 1, 1, 1, 1);
INSERT INTO notification_prefs (id, user_id, email_enabled, remind_3days, remind_2days, remind_1day, remind_deadline) VALUES (2, 7, 1, 0, 1, 1, 1);
SELECT setval('notification_prefs_id_seq', (SELECT COALESCE(MAX(id), 1) FROM notification_prefs));

-- Data for assignments
INSERT INTO assignments (id, teacher_id, subject_id, title, description, deadline, classroom_link, resource_path, created_at) VALUES (1, 2, 2, 'Unit 1 Assignment', 'complete it as soon as possible!!', '2026-03-16 23:30:00.000000', NULL, 'Pytest_Report__018.pdf', '2026-03-14 17:51:35.934198');
INSERT INTO assignments (id, teacher_id, subject_id, title, description, deadline, classroom_link, resource_path, created_at) VALUES (2, 2, 1, 'U2 Assignment', 'do fast', '2026-03-15 21:30:00.000000', 'https://classroom.google.com/c/Nzg4Nzc5NTUzMDM0', '5dab4e11_Pytest_Report__018.pdf', '2026-03-14 18:05:31.308520');
INSERT INTO assignments (id, teacher_id, subject_id, title, description, deadline, classroom_link, resource_path, created_at) VALUES (3, 2, 1, 'assignment 4', 'trials', '2026-03-26 14:30:00.000000', NULL, '6de07bac_Pytest_Report__018.pdf', '2026-03-16 06:33:14.063404');
SELECT setval('assignments_id_seq', (SELECT COALESCE(MAX(id), 1) FROM assignments));

-- Data for submissions
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (1, 1, 1, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (2, 1, 2, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (3, 1, 3, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (4, 1, 4, 1, '2026-03-14 18:01:38.367285', 'submitted');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (5, 2, 1, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (6, 2, 2, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (7, 2, 3, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (8, 2, 4, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (9, 3, 3, 0, NULL, 'pending');
INSERT INTO submissions (id, assignment_id, student_id, self_reported, submitted_at, status) VALUES (10, 3, 4, 0, NULL, 'pending');
SELECT setval('submissions_id_seq', (SELECT COALESCE(MAX(id), 1) FROM submissions));

-- Data for announcements
INSERT INTO announcements (id, posted_by, title, content, priority, target_audience, target_class, target_department, created_at) VALUES (1, 9, 'urgent announcement', 'successful testing of urgent announcement', 'urgent', 'student', 'Alpha', 'CSE', '2026-03-14 18:40:30.742407');
INSERT INTO announcements (id, posted_by, title, content, priority, target_audience, target_class, target_department, created_at) VALUES (2, 9, 'imp announcement', 'bbb', 'important', 'all', 'Delta', 'CSE', '2026-03-14 18:41:13.509367');
INSERT INTO announcements (id, posted_by, title, content, priority, target_audience, target_class, target_department, created_at) VALUES (3, 9, 'normal announcemnt', 'checkingggg', 'normal', 'teacher', 'Delta', 'CSE', '2026-03-14 18:41:57.308497');
INSERT INTO announcements (id, posted_by, title, content, priority, target_audience, target_class, target_department, created_at) VALUES (4, 9, 'u1', 'vvv', 'urgent', 'student', 'Alpha', 'CSE', '2026-03-14 18:50:31.315752');
SELECT setval('announcements_id_seq', (SELECT COALESCE(MAX(id), 1) FROM announcements));

-- Data for announcement_reads
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (1, 1, 9, '2026-03-14 18:42:22.028181');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (2, 2, 9, '2026-03-14 18:42:24.685903');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (3, 3, 9, '2026-03-14 18:42:26.181713');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (4, 1, 7, '2026-03-14 18:49:25.407733');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (5, 2, 7, '2026-03-14 18:49:26.307463');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (6, 3, 7, '2026-03-14 18:49:26.741919');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (7, 4, 8, '2026-03-15 17:24:30.287391');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (8, 1, 8, '2026-03-15 17:24:30.857685');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (9, 2, 8, '2026-03-15 17:24:31.446531');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (10, 3, 8, '2026-03-15 17:24:32.020150');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (11, 4, 7, '2026-03-15 17:39:34.078006');
INSERT INTO announcement_reads (id, announcement_id, user_id, read_at) VALUES (12, 4, 9, '2026-03-15 18:14:02.114222');
SELECT setval('announcement_reads_id_seq', (SELECT COALESCE(MAX(id), 1) FROM announcement_reads));

