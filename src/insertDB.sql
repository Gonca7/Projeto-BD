INSERT INTO auth (username, pw, tag) 
VALUES ('user', 'pw', 123);

INSERT INTO course (name, code, prerequisites, edition, capacity, Instructor_auth_tag)
VALUES ('BD', 123765890, 'Lorem Ipsum', '24/25', 30, 123);

INSERT INTO instructor (name, auth_tag)
values ('Joao', 123);

