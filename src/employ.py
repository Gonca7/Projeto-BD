import flask
from flask import Flask
from functools import wraps
import flask
from flask import Flask
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import logging
import psycopg2

app = Flask(__name__)
JWT_SECRET_KEY = "ultra-secured-key"
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
    conn.set_client_encoding('UTF8')
    return conn

def generate_token(username, role):
    try:
        if role not in ['student', 'instructor', 'staff']:
            raise ValueError('Invalid role specified.')

        payload = {
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'username': username,
            'role': role
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        return token if isinstance(token, str) else token.decode('utf-8')
    except Exception as e:
        logger.error(f'Error generating token: {str(e)}')
        return None

def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = flask.request.headers.get('Authorization')
            token = None

            if auth_header:
                token_parts = auth_header.split(" ")
                token = token_parts[1] if len(token_parts) > 1 else token_parts[0]

            if not token:
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': 'Token is missing. Add Authorization: Bearer <token>',
                    'results': None
                })

            try:
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
                data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])

                current_user = {
                    'username': data['username'],
                    'role': data['role']
                }

                if role and current_user['role'] != role:
                    return flask.jsonify({
                        'status': status_codes['unauthorized'],
                        'errors': f"Access denied for role '{current_user['role']}'",
                        'results': None
                    })

                flask.g.current_user = current_user
                return f(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': 'Token has expired',
                    'results': None
                })
            except jwt.InvalidTokenError as e:
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': f'Invalid token: {str(e)}',
                    'results': None
                })
        return decorated
    return decorator
logger = logging.getLogger()
status_codes = {
    'internal server error': 500,
    'bad request': 400,
    'unauthorized': 401,
    'success': 200
} 

def connect_db():
    return psycopg2.connect(
        user="usr",
        password="password",
        host="localhost",
        port="5432",
        database="empdb"
    )

def generate_token(username, role):
    """Generate a JWT token with role-based permissions (student or instructor)"""
    try:
        if role not in ['student', 'instructor']:
            raise ValueError('Invalid role specified. Must be student or instructor.')

        payload = {
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'username': username,
            'role': role
        }

        token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm='HS256'
        )

        return token if isinstance(token, str) else token.decode('utf-8')
    except Exception as e:
        logger.error(f'Error generating token: {str(e)}')
        return None

def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            auth_header = flask.request.headers.get('Authorization')

            logger.info(f'Received Authorization header: {auth_header}')

            if auth_header:
                try:
                    token_parts = auth_header.split(" ")
                    token = token_parts[1] if len(token_parts) > 1 else token_parts[0]
                    logger.info(f'Extracted token: {token}')
                except IndexError:
                    logger.error('Invalid Authorization header format')
                    return flask.jsonify({
                        'status': status_codes['unauthorized'],
                        'errors': 'Invalid token format. Use: Bearer <token>',
                        'results': None
                    })

            if not token:
                logger.error('No token provided')
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': 'Token is missing. Add Authorization: Bearer <token> header',
                    'results': None
                })

            try:
                logger.info('Attempting to decode token')
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
                data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                logger.info(f'Token decoded successfully: {data}')

                current_user = {
                    'user_id': int(data['sub']),
                    'username': data['username'],
                    'role': data['role']
                }

                if role and current_user['role'] != role:
                    logger.warning(f"Access denied. User role '{current_user['role']}' does not match required role '{role}'")
                    return flask.jsonify({
                        'status': status_codes['unauthorized'],
                        'errors': f"Access denied for role '{current_user['role']}'",
                        'results': None
                    })

                flask.g.current_user = current_user
                return f(*args, **kwargs)

            except jwt.ExpiredSignatureError:
                logger.error('Token has expired')
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': 'Token has expired',
                    'results': None
                })
            except jwt.InvalidTokenError as e:
                logger.error(f'Invalid token error: {str(e)}')
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': f'Invalid token: {str(e)}',
                    'results': None
                })
            except Exception as e:
                logger.error(f'Unexpected error during token verification: {str(e)}')
                return flask.jsonify({
                    'status': status_codes['unauthorized'],
                    'errors': f'Token verification failed: {str(e)}',
                    'results': None
                })
        return decorated
    return decorator

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
        logger.warning("Login failed: invalid credentials")
        return flask.jsonify({"error": "Invalid username or password"}), 401

    role = tag

    try:
        token = generate_token(username, role)
        if token is None:
            raise Exception("Token generation failed")

        return flask.jsonify({"token": token})
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return flask.jsonify({"error": "Login failed due to server error"}), 500




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
