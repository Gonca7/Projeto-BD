import flask
from flask import Flask
from functools import wraps
import jwt
from datetime import datetime, timedelta
import logging
import psycopg2

app = Flask(__name__)
pkey = "ultra-secured-key"
enc = "HS256"
logger = logging.getLogger()
status_codes = {
    'internal server error': 500,
    'bad request': 400,
    'unauthorized': 401,
    'success': 200
} 

def get_option():
    option =- 1

    while (option not in [0, 1, 2, 3, 4, 5, 6]):
        print('1 - List Departments')
        print('2 - List Employees')
        print('3 - Get Employee')
        print('4 - Add Employee')
        print('5 - Remove Employee')
        print('6 - Move Employee to Department')
        print('0 - Exit')

        try:
            option = int(input('Option: '))
            
        except:
            option =- 1

    return option

def connect_db():
    return psycopg2.connect(
        user="usr",
        password="password",
        host="localhost",
        port="5432",
        database="empdb"
    )

def checkAuth():
    
    auth_head = flask.request.headers.get('Authorization')

    if not auth_head:
            return flask.jsonify({'error':'Missing authorization header'}), 401

    try:
        token = auth_head
        payload = jwt.decode(token, pkey, algorithms=[enc])
        return payload, 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return flask.jsonify({'error':'Invalid tokens'}), 401

@app.route('/login', methods=['POST'])
def login():
    
    data = flask.request.get_json()
    username = data.get("username")
    password = data.get("password")

    '''
    print("\n--- Login Required ---")
    username = input("Username: ")
    password = input("Password: ")
    '''

    con = connect_db()
    cursor = con.cursor()
    cursor.execute("select tag from auth where username=%s and pw=%s", (username, password))

    user = cursor.fetchone()
    print(user)

    if user is None:
        print("No user assigned to this credentials\n")
        return flask.jsonify({"error":"No user assigned to this credentials"}), 401

    payload = {
        "username":username,
        "role": user[0],
        "exp": datetime.now() + timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, pkey, algorithm=enc)

    return flask.jsonify({"token": token})

@app.route('/enroll_course_edition/<course_edition_id>', methods=['POST'])
def enroll_couse_edition(course_edition_id):

    a = checkAuth()
    if (a[1] != 200):
        return a
    
    #Body
    connection = connect_db()
    cursor = connection.cursor()
    data = flask.request.get_json()

    cursor.execute("select ")
    
    return flask.jsonify("")

@app.route('/submit_grades/<course_edition_id>', methods=['GET'])
def submit_grades(course_edition_id):
    return flask.jsonify()

@app.route('/student_details/<student_id>', methods=['GET'])
def list_student_details(student_id):

    a = checkAuth()
    if (a[1] != 200):
        return a
    
    #Body
    connection = connect_db()
    cursor = connection.cursor()
    
    cursor.execute(
        '''
            SELECT
            course.course_edition_id AS course_edition_id,
            couse.course_name AS course_name,
            course.course_edition AS course_edition,
            academic_rate.grade AS grade
            FROM
            student
            JOIN enrolment ON student.auth_tag = enrolment.student_auth_tag
            JOIN academic_record ON academic_rate.enrolment_id = enrolment.id
            JOIN course ON academic_rate.course_name = course.name
            WHERE
                student.auth_tag = :student_id
            ORDER BY
                course_edition_year DESC;
        ''')
    
    # Fetch results
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    results = [dict(row) for row in rows]

    # Close connection
    cursor.close()
    connection.close()

    return flask.jsonify(results)

@app.route('/degree_details/<degree_id>', methods=['GET'])
def list_degree_details(student_id):

    a = checkAuth()
    if (a[1] != 200):
        return a
    
    #Body
    connection = connect_db()
    cursor = connection.cursor()
    
    cursor.execute(
        '''
            SELECT
            course.code AS course_id,
            course.name AS couse_name,
            course.edition AS course_edition,
            course.capacity AS couse_capacity,
            COUNT(DISTINCT enrolled_count.student_auth_tag) AS enrolled_count,
            COUNT(DISTINCT CASE WHEN academic_rate.grade >= 10 THEN academic_rate.enrolment_id END) AS approved_count,
            course.instructor_auth_tag AS coordinator_id,
            ARRAY_AGG(DISTINCT course_instructor.instructor_auth_tag) AS instructors
            FROM
                course
            JOIN degree_course ON degree_course.course_code = course.code
            LEFT JOIN course_instructor ON course_instructor.course_code = course.code
            LEFT JOIN class_time ON class_time.course_code = course.code
            LEFT JOIN enrolment ON enrollment.degree_id = degree_course.degree_id
            LEFT JOIN academic_record ON academic_record.enrolment_id = enrollment.id AND academic_record.course_name = course.name
            WHERE
                degree_couse.degree_id = :degree_id
            GROUP BY
                course.code, course.name, course.edition, course.capacity, course.instructor_auth_tag
            ORDER BY
                course_edition_year DESC;
        ''')
    
    # Fetch results
    rows = cursor.fetchall()

    # Convert to list of dictionaries
    results = [dict(row) for row in rows] 

    # Close connection
    cursor.close()
    connection.close()

    return flask.jsonify(results)

if __name__ == '__main__':

    app.run(debug=True)
    #login()

    '''
    function_list = (list_departments, list_employees, get_employee, add_employee, remove_employee, move_emp_department)
    option = -1

    while (option!=0):
        option = get_option()
        if (option != 0):
            function_list[option-1]()
    '''
