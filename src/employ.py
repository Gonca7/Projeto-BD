import flask
from flask import Flask
from functools import wraps
import jwt
from datetime import datetime, timedelta
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

@app.route('/login', methods=['POST'])
def login():
    data = flask.request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("tag")  # ex: 'staff', 'student', 'instructor'

    con = connect_db()
    cursor = con.cursor()
    cursor.execute("SELECT tag FROM auth WHERE username=%s AND pw=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    con.close()

    if user is None:
        return flask.jsonify({"error": "Invalid username or password"}), 401

    try:
        token = generate_token(username, role)
        if token is None:
            raise Exception("Token generation failed")

        return flask.jsonify({"token": token})
    except Exception as e:
        return flask.jsonify({"error": "Login failed due to server error"}), 500


@app.route("/students/top3", methods=["GET"])
def top3_students():
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("""
            SELECT s.auth_tag, s.name, ar.course_name, ar.grade
            FROM student s
            JOIN enrolment e ON s.auth_tag = e.student_auth_tag
            JOIN academic_record ar ON ar.enrolment_id = e.id
            ORDER BY ar.grade DESC
            LIMIT 3;
        """)
        results = cursor.fetchall()
        con.close()
        return flask.jsonify([
            {
                "auth_tag": row[0],
                "name": row[1],
                "course_name": row[2],
                "grade": row[3]
            }
            for row in results
        ])
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

@app.route("/dbproj/top_by_district/", methods=["GET"])
@token_required(role='staff')
def top_by_district():
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("""
            SELECT s.auth_tag AS student_id,
                   s.district,
                   AVG(ar.grade) AS average_grade
            FROM student s
            JOIN enrolment e ON s.auth_tag = e.student_auth_tag
            JOIN academic_record ar ON ar.enrolment_id = e.id
            GROUP BY s.auth_tag, s.district
            HAVING AVG(ar.grade) = (
                SELECT MAX(avg_g) FROM (
                    SELECT AVG(ar2.grade) AS avg_g
                    FROM student s2
                    JOIN enrolment e2 ON s2.auth_tag = e2.student_auth_tag
                    JOIN academic_record ar2 ON ar2.enrolment_id = e2.id
                    WHERE s2.district = s.district
                    GROUP BY s2.auth_tag
                ) sub
            )
            ORDER BY s.district;
        """)
        results = cursor.fetchall()
        con.close()
        return flask.jsonify({
            "status": 200,
            "errors": None,
            "results": [
                {
                    "student_id": row[0],
                    "district": row[1],
                    "average_grade": float(row[2])
                } for row in results
            ]
        })
    except Exception as e:
        return flask.jsonify({"status": 500, "errors": str(e), "results": []})


@app.route("/dbproj/report", methods=["GET"])
@token_required(role='staff')
def monthly_report():
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("""
            SELECT DISTINCT ON (month)
                TO_CHAR(ar.date_evaluated, 'YYYY-MM') AS month,
                c.code AS course_edition_id,
                c.name AS course_edition_name,
                COUNT(*) FILTER (WHERE ar.grade >= 10) AS approved,
                COUNT(*) AS evaluated
            FROM academic_record ar
            JOIN enrolment e ON ar.enrolment_id = e.id
            JOIN course c ON c.name = ar.course_name
            WHERE ar.date_evaluated >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY month, c.code, c.name
            ORDER BY month, approved DESC;
        """)
        results = cursor.fetchall()
        con.close()
        return flask.jsonify({
            "status": 200,
            "errors": None,
            "results": [
                {
                    "month": row[0],
                    "course_edition_id": row[1],
                    "course_edition_name": row[2],
                    "approved": row[3],
                    "evaluated": row[4]
                } for row in results
            ]
        })
    except Exception as e:
        return flask.jsonify({"status": 500, "errors": str(e), "results": []})


@app.route("/dbproj/delete_details/<int:student_id>", methods=["DELETE"])
@token_required(role='staff')
def delete_student(student_id):
    try:
        con = connect_db()
        cursor = con.cursor()
        cursor.execute("SELECT id FROM enrolment WHERE student_auth_tag = %s", (student_id,))
        enrolments = cursor.fetchall()
        for enrol_id in enrolments:
            cursor.execute("DELETE FROM academic_record WHERE enrolment_id = %s", (enrol_id[0],))
        cursor.execute("DELETE FROM enrolment WHERE student_auth_tag = %s", (student_id,))
        cursor.execute("DELETE FROM financial_record WHERE student_auth_tag = %s", (student_id,))
        cursor.execute("DELETE FROM student_extra_curricular WHERE student_auth_tag = %s", (student_id,))
        cursor.execute("DELETE FROM student WHERE auth_tag = %s", (student_id,))
        cursor.execute("DELETE FROM auth WHERE tag = %s", (student_id,))
        con.commit()
        con.close()
        return flask.jsonify({"status": 200, "errors": None})
    except Exception as e:
        return flask.jsonify({"status": 500, "errors": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
