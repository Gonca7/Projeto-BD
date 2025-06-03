import flask
from flask import Flask
from functools import wraps
import flask
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

def connect_db():
    conn = psycopg2.connect(
        user="usr",
        password="password",
        host="localhost",
        port="5432",
        database="empdb"
    )
    conn.set_client_encoding('UTF-8')
    return conn

@app.route('/login', methods=['POST'])
def login():
    data = flask.request.get_json()
    username = data.get("username")
    password = data.get("password")
    tag = data.get("tag")

    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT tag FROM auth WHERE username=%s AND pw=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    con.close()

    if user is None:
        print("No user assigned to this credentials\n")
        return flask.jsonify({"error":"No user assigned to this credentials"}), 401

    payload = {
        "username":username,
        "role": user[0],
        "exp": datetime.now() + timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, pkey, algorithm=enc)

    print(token);

    return flask.jsonify({"token": token})

def get_option():
    
    option=-1

    while (option not in [0,1,2,3,4,5,6]):
        print('1 - List Departments')
        print('2 - List Employees')
        print('3 - Get Employee')
        print('4 - Add Employee')
        print('5 - Remove Employee')
        print('6 - Move Employee to Department')
        print('0 - Exit')

        try:
            option=int(input('Option: '))
        except:
            option=-1

    return option

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

@app.route('/lst_courses', methods=['GET'])
def list_courses():

    a = checkAuth()
    if(a[1] != 200 ):
        return a

    #Body
    print('--- List of Departments ---')

    connection=connect_db()
    cursor = connection.cursor()
    cursor.execute('select * from course')

    courses = cursor.fetchall()

    result = []
    for row in courses:
        result.append({
            "name":row[0],
            "code":row[1],
            "prerequisites":row[2],
            "edition":row[3],
            "capacity":row[4],
            "Instructor_auth_tag":row[5]
        })

    '''
    string = ["Cadeira", "Código", "PreRequesitos", "Edição", "Capacidade", "ID Instrutor"]
    print("{:<25} {:<5} {:<20} {:<7} {:<7} {:<11}".format(*string))

    for row in cursor:

        temp = [row[0],row[1],row[2], row[3],row[4],row[5]]
        print("{:<25} {:<5} {:>20} {:<7} {:<7} {:<11}".format(*temp))

    print('---------------------------\n')'''

    return flask.jsonify(result)

def list_employees():
    print('\n--- List of Employees ---')

    ## To Be Completed

    print('-------------------------\n')

def get_employee():
    print('\n--- Get Employee ---')

    name=''
    while (len(name)==0):
        name=input('Name: ')

    connection=connect_db()
    cursor = connection.cursor()
    cursor.execute("select emp_no, employees.name, job, date_contract, salary, commissions, departments.name \
    from employees,departments \
    where departments_dep_no = dep_no \
    and employees.name='"+name+"'")

    
    # and employees.name='' or 1=1 --'

    # cursor.execute("select emp_no, employees.name, job, date_contract, salary, commissions, departments.name \
    # from employees,departments \
    # where departments_dep_no = dep_no \
    # and employees.name=%s",(name,))

    if (cursor.rowcount==0):
        print('Employee does not exist!')

    for row in cursor:
        print('No:',row[0])
        print('Name:',row[1])
        print('Job:',row[2])
        print('Date Contract:',row[3])
        print('Salary:',row[4])
        print('Commissions:',row[5])
        print('Department:',row[6])

    print('--------------------\n')

@app.route('/register/<usr_type>', methods=['POST'])
def add_employee(usr_type):
    
    a = checkAuth()
    if(a[1] != 200 ):
        return a

    #Body
    connection=connect_db()
    cursor = connection.cursor()
    data = flask.request.get_json()

    if(usr_type == 'student'):
        name = data.get("name")
        age= data.get("age")
        reg_year = data.get("reg_year")
        
        cursor.execute(
            '''
            INSERT INTO student(name, age, registration_year, auth_tag)
            VALUES(%s, %s, %s, %s);
            ''', (name, age, reg_year, a[0]["role"]))
        
        connection.commit()
        return flask.jsonify({'Success':'Student added '}), 200
    
    elif(usr_type == 'instructor'):
        name = data.get("name")
        
        cursor.execute(
            '''
            INSERT INTO instructor(name, auth_tag)
            VALUES(%s, %s);
            ''', (name, a[0]["role"]))
        
        connection.commit()
        return flask.jsonify({'Success':'Instructor added '}), 200        

    return flask.jsonify({'error':'Bad Request'}), 400


@app.route('/enroll_deg/<deg_id>', methods=['POST'])
def enrollDeg(deg_id):
    
    a = checkAuth()
    if(a[1] != 200 ):
        return a
    
    #Body
    connection=connect_db()
    cursor = connection.cursor()
    data = flask.request.get_json()


    cursor.execute('''select * from instructor where auth_tag = %s''', (a[0]["role"],))
    isStaff = cursor.fetchall()
    if(len(isStaff) <= 0):
        return flask.jsonify({'error':'Operation Denied'}), 500


    tag = data.get('tag')
    cursor.execute(
    '''
    insert into enrolment(is_finished, degree_id, student_auth_tag)
    values(false, %s, %s);
    ''', (deg_id, tag))

    connection.commit()
    return flask.jsonify({'Success':'Student enrolled'}), 200       

@app.route('/enroll_act/<act_id>', methods=['POST'])
def enrollAct(act_id):
    
    a = checkAuth()
    if(a[1] != 200 ):
        return a
    
    #Body
    connection=connect_db()
    cursor = connection.cursor()
    data = flask.request.get_json()


    cursor.execute('''select * from student where auth_tag = %s''', (a[0]["role"],))
    isStud = cursor.fetchall()
    if(len(isStud) <= 0):
        return flask.jsonify({'error':'Operation Denied'}), 500


    cursor.execute(
    '''
    insert into student_extra_curricular(student_auth_tag, extra_curricular_id)
    values(%s, %s);
    ''', (a[0]["role"], act_id))

    connection.commit()
    return flask.jsonify({'Success':'You enrolled into an activity'}), 200

def remove_employee():
    print('\n--- Remove Employee ---')

    name=''
    while (len(name)==0):
        name=input('Name: ')

    connection=connect_db()
    cursor = connection.cursor()
    cursor.execute("delete from employees \
    where name=%s",(name,))

    if (cursor.rowcount==0):
        print('Employee does not exist!')
    else:
        print(cursor.rowcount, 'employee(s) deleted!')
        connection.commit()

    print('-----------------------\n')

def move_emp_department():
    print('\n--- Move Employee to Department ---')

    ## To Be Completed

    print('-----------------------------------\n')

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
