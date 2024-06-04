import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for
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
    password="2802",
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



@app.route('/loginmain')
def login2():
    return render_template('login.html')



@app.route('/mainpage')
def get_projects():
    try:
        conn = db
        cursor = conn.cursor()

        user_name = "user1"
        #user_name = request.cookies.get('username')
        select_query = """
        SELECT t.* 
        FROM team t 
        JOIN team_members tm ON tm.project_id = t.project_id 
        WHERE tm.member_name = %s
    """
        cursor.execute(select_query, (user_name, ))
        projects = []

        for (project_id, project_name) in cursor.fetchall():  # fetchall()로 결과 가져오기
            project_info = {
                'project_id': project_id,
                'project_name': project_name,
                'members': [],
                'tags': []
            }

            # 팀원 정보 조회
            select_members_query = "SELECT member_name FROM team_members WHERE project_id = %s"
            cursor.execute(select_members_query, (project_id,))
            members_result = cursor.fetchall()

            for (member_name,) in members_result:
                project_info['members'].append(member_name)

            # 태그 정보 조회
            select_tags_query = "SELECT tag_name FROM project_tags WHERE project_id = %s"
            cursor.execute(select_tags_query, (project_id,))
            tags_result = cursor.fetchall()

            for (tag_name,) in tags_result:
                project_info['tags'].append(tag_name)

            projects.append(project_info)

        cursor.close()
        conn.close()

        return render_template('mainpage.html', projects=projects)

    except Exception as e:
        app.logger.error(f'프로젝트 조회 중 오류 발생: {str(e)}')
        return jsonify(message=f'프로젝트 조회에 실패했습니다: {str(e)}'), 500



if __name__ == '__main__':
    app.run(debug=True)
