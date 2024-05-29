import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})  # CORS 설정

bcrypt = Bcrypt()

# MySQL 데이터베이스 연결 설정
# 이 설정은 데이터베이스 호스트, 사용자 이름, 비밀번호, 데이터베이스 이름을 포함합니다.
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="teamteam"
)
cursor = db.cursor()

# 회원가입 처리를 위한 POST 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    email = data['email']

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if user:
        return jsonify({'message': 'Username already exists'}), 409

    cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
    db.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# 로그인 처리를 위한 POST 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'Username does not exist'}), 401

    hashed_password = user[2]  # 저장된 해시된 비밀번호를 가져옵니다.
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({'message': 'Password is incorrect'}), 401

    return jsonify({'message': 'Login successful'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
