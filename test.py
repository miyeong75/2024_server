import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response

app = Flask(__name__)

# MySQL 데이터베이스 연결 설정
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="2802",
        database="teamteam"
    )
    return connection

# 로그인 페이지 라우트
@app.route('/loginmain')
def login2():
    return render_template('login.html')

# 로그인 처리 라우트
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and user[0] == password:
        response = make_response(jsonify(success=True))
        response.set_cookie('username', username)
        return response
    else:
        return jsonify(success=False, message="잘못된 사용자 이름 또는 비밀번호입니다.")

# 회원가입 처리 라우트
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 사용자 이름 중복 확인
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        cursor.close()
        conn.close()
        return jsonify(success=False, message="이미 존재하는 사용자 이름입니다.")
    
    # 새로운 사용자 추가
    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                   (username, password, email))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(success=True)

# 메인 페이지 라우트
@app.route('/mainpage')
def get_projects():
    try:
        user_name = request.cookies.get('username')
        if not user_name:
            return redirect(url_for('login2'))

        conn = get_db_connection()
        cursor = conn.cursor()

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



