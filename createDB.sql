CREATE TABLE course (
	name		 TEXT NOT NULL,
	code		 BIGINT,
	prerequisites	 TEXT,
	edition		 CHAR(5) NOT NULL,
	capacity		 INTEGER NOT NULL,
	instructor_auth_tag BIGINT NOT NULL,
	PRIMARY KEY(code)
);

CREATE TABLE class_time (
	class_number		 INTEGER NOT NULL,
	class_time		 TIMESTAMP NOT NULL,
	is_pl			 BOOL NOT NULL DEFAULT true,
	classroom_classroom_number BIGINT,
	course_code		 BIGINT,
	PRIMARY KEY(classroom_classroom_number,course_code)
);

CREATE TABLE classroom (
	classroom_number BIGINT,
	campus		 TEXT NOT NULL,
	location	 TEXT NOT NULL,
	capacity	 INTEGER NOT NULL,
	PRIMARY KEY(classroom_number)
);

CREATE TABLE degree (
	id	 BIGINT,
	name TEXT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE student (
	name		 TEXT NOT NULL,
	age		 INTEGER NOT NULL,
	registration_year INTEGER NOT NULL,
	auth_tag		 BIGINT,
	PRIMARY KEY(auth_tag)
);

CREATE TABLE academic_record (
	id		 BIGSERIAL,
	course_name	 TEXT NOT NULL,
	grade	 INTEGER NOT NULL,
	enrolment_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE financial_record (
	description	 VARCHAR(512),
	cost		 FLOAT(8) NOT NULL,
	is_paid		 BOOL NOT NULL DEFAULT false,
	is_extra	 BOOL NOT NULL DEFAULT false,
	student_auth_tag BIGINT NOT NULL
);

CREATE TABLE instructor (
	name	 TEXT NOT NULL,
	auth_tag BIGINT,
	PRIMARY KEY(auth_tag)
);

CREATE TABLE enrolment (
	id		 BIGSERIAL,
	is_finished	 BOOL DEFAULT false,
	degree_id	 BIGINT NOT NULL,
	student_auth_tag BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE extra_curricular (
	id		 SERIAL,
	name	 VARCHAR(512) NOT NULL,
	description VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE auth (
	username CHAR(20) NOT NULL,
	pw	 VARCHAR(512) NOT NULL,
	tag	 BIGSERIAL,
	PRIMARY KEY(tag)
);

CREATE TABLE student_extra_curricular (
	student_auth_tag	 BIGINT,
	extra_curricular_id INTEGER,
	PRIMARY KEY(student_auth_tag,extra_curricular_id)
);

CREATE TABLE course_instructor (
	course_code	 BIGINT,
	instructor_auth_tag BIGINT,
	PRIMARY KEY(course_code,instructor_auth_tag)
);

CREATE TABLE degree_course (
	degree_id	 BIGINT,
	course_code BIGINT,
	PRIMARY KEY(degree_id,course_code)
);

CREATE TABLE course_course (
	course_code	 BIGINT,
	course_code1 BIGINT,
	PRIMARY KEY(course_code,course_code1)
);

ALTER TABLE course ADD CONSTRAINT course_fk1 FOREIGN KEY (instructor_auth_tag) REFERENCES instructor(auth_tag);
ALTER TABLE class_time ADD CONSTRAINT class_time_fk1 FOREIGN KEY (classroom_classroom_number) REFERENCES classroom(classroom_number);
ALTER TABLE class_time ADD CONSTRAINT class_time_fk2 FOREIGN KEY (course_code) REFERENCES course(code);
ALTER TABLE student ADD CONSTRAINT student_fk1 FOREIGN KEY (auth_tag) REFERENCES auth(tag);
ALTER TABLE academic_record ADD CONSTRAINT academic_record_fk1 FOREIGN KEY (enrolment_id) REFERENCES enrolment(id);
ALTER TABLE financial_record ADD CONSTRAINT financial_record_fk1 FOREIGN KEY (student_auth_tag) REFERENCES student(auth_tag);
ALTER TABLE instructor ADD CONSTRAINT instructor_fk1 FOREIGN KEY (auth_tag) REFERENCES auth(tag);
ALTER TABLE enrolment ADD CONSTRAINT enrolment_fk1 FOREIGN KEY (degree_id) REFERENCES degree(id);
ALTER TABLE enrolment ADD CONSTRAINT enrolment_fk2 FOREIGN KEY (student_auth_tag) REFERENCES student(auth_tag);
ALTER TABLE student_extra_curricular ADD CONSTRAINT student_extra_curricular_fk1 FOREIGN KEY (student_auth_tag) REFERENCES student(auth_tag);
ALTER TABLE student_extra_curricular ADD CONSTRAINT student_extra_curricular_fk2 FOREIGN KEY (extra_curricular_id) REFERENCES extra_curricular(id);
ALTER TABLE course_instructor ADD CONSTRAINT course_instructor_fk1 FOREIGN KEY (course_code) REFERENCES course(code);
ALTER TABLE course_instructor ADD CONSTRAINT course_instructor_fk2 FOREIGN KEY (instructor_auth_tag) REFERENCES instructor(auth_tag);
ALTER TABLE degree_course ADD CONSTRAINT degree_course_fk1 FOREIGN KEY (degree_id) REFERENCES degree(id);
ALTER TABLE degree_course ADD CONSTRAINT degree_course_fk2 FOREIGN KEY (course_code) REFERENCES course(code);
ALTER TABLE course_course ADD CONSTRAINT course_course_fk1 FOREIGN KEY (course_code) REFERENCES course(code);
ALTER TABLE course_course ADD CONSTRAINT course_course_fk2 FOREIGN KEY (course_code1) REFERENCES course(code);


