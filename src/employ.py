import jwt
from flask import Flask, request, jsonify
import psycopg2
import datetime

app = Flask(__name__)
pkey = "ultra-secured-key"
enc = "HS256"

@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    '''
    print("\n--- Login Required ---")
    username = input("Username: ")
    password = input("Password: ")'''

    con = connect_db();
    cursor = con.cursor()
    cursor.execute("select tag from auth where username=%s and pw=%s", (username, password))

    user = cursor.fetchone()
    print(user)

    if user is None:
        print("No user assigned to this credentials\n")
        return jsonify({"error":"No user assigned to this credentials"}), 401

    payload = {
        "username":username,
        "role": user[0],
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, pkey, algorithm=enc)

    print(token);

    return jsonify({"token": token})


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

def connect_db():
    connection = psycopg2.connect(user = "gonca7",
        password = "postgres",   # password should not be visible - will address this later on the course
        host = "localhost",
        port = "5432",
        database = "empdb")
    # parameters should be changeable - will address this later on the course

    return connection

def checkAuth():
    
    auth_head = request.headers.get('Authorization')

    if not auth_head:
            return jsonify({'error':'Missing authorization header'}), 401

    try:
        token = auth_head
        payload = jwt.decode(token, pkey, algorithms=[enc])
        return payload, 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return jsonify({'error':'Invalid tokens'}), 401



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

    return jsonify(result)

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
    data = request.get_json()

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
        return jsonify({'200':'Student added '}), 200
    
    elif(usr_type == 'instructor'):
        name = data.get("name")
        
        cursor.execute(
            '''
            INSERT INTO instructor(name, auth_tag)
            VALUES(%s, %s);
            ''', (name, a[0]["role"]))
        
        connection.commit()
        return jsonify({'200':'Instructor added '}), 200        

    return jsonify({'error':'Bad Request'}), 400



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
            function_list[option-1]()'''
