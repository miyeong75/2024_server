from flask import Flask, request, jsonify, make_response, render_template, url_for, redirect
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import mysql.connector
from datetime import datetime


app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}}, supports_credentials=True)
bcrypt = Bcrypt(app)

# 데이터베이스 연결 설정
db_config = {
    'user': 'root',
    'password': '2802',
    'host': 'localhost',
    'database': 'teamteam'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# 프로젝트 이름 조회 함수 추가
def get_project_name(project_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT project_name FROM team WHERE project_id = %s", (project_id,))
    project_name = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return project_name

# 루트 경로 - 할 일 목록 페이지 렌더링
@app.route('/projects/<int:project_id>/todos')
def index_todos(project_id):
    project_name = get_project_name(project_id)
    return render_template('todos.html', project_id=project_id, project_name=project_name)

# 캘린더 페이지 라우트 추가
@app.route('/projects/<int:project_id>/calendar')
def calendar(project_id):
    project_name = get_project_name(project_id)
    return render_template('calendar.html', project_id=project_id, project_name=project_name)

# mypage 라우트 추가
@app.route('/mypage')
def mypage(project_id=1):
    project_name = get_project_name(project_id)
    return render_template('mypage.html', project_id=project_id, project_name=project_name)

# 할 일 목록 가져오기
@app.route('/api/projects/<int:project_id>/todos', methods=['GET'])
def get_todos(project_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, description, deadline, completed FROM todos WHERE project_id = %s", (project_id,))
        todos = cursor.fetchall()
        return jsonify(todos)
    finally:
        cursor.close()
        connection.close()

# 할 일 추가
@app.route('/api/projects/<int:project_id>/todos', methods=['POST'])
def add_todo(project_id):
    data = request.json
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO todos (description, deadline, completed, project_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (data['description'], data['deadline'], data.get('completed', False), project_id))
        connection.commit()
        return jsonify({'id': cursor.lastrowid}), 201
    finally:
        cursor.close()
        connection.close()

# 할 일 수정
@app.route('/api/projects/<int:project_id>/todos/<int:todo_id>', methods=['PUT'])
def update_todo(project_id, todo_id):
    data = request.json
    description = data.get('description')
    deadline = data.get('deadline')
    completed = data.get('completed', None)

    if completed is None:
        return jsonify({'error': 'completed field is required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        sql = "UPDATE todos SET description=%s, deadline=%s, completed=%s WHERE id=%s AND project_id=%s"
        cursor.execute(sql, (description, deadline, completed, todo_id, project_id))
        connection.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# 할 일 삭제
@app.route('/api/projects/<int:project_id>/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(project_id, todo_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        sql = "DELETE FROM todos WHERE id=%s AND project_id=%s"
        cursor.execute(sql, (todo_id, project_id))
        connection.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Minutes 관련 라우트 추가
@app.route('/projects/<int:project_id>/minutes')
def index(project_id):
    project_name = get_project_name(project_id)
    return render_template('minutesindex.html', project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/minutespage1')
def page1(project_id):
    project_name = get_project_name(project_id)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT m.MinutesID, m.Title, m.Content, m.CreateDate, m.Author, GROUP_CONCAT(t.name SEPARATOR ',') AS Tags
        FROM Minutes m
        LEFT JOIN minute_tags mt ON m.MinutesID = mt.Minutes_id
        LEFT JOIN minutestagslist t ON mt.tag_id = t.id
        WHERE m.project_id = %s
        GROUP BY m.MinutesID, m.Title, m.Content, m.CreateDate, m.Author
    """, (project_id,))
    minutes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for minute in minutes:
        if minute['Tags']:
            minute['tags'] = minute['Tags'].split(',')
        else:
            minute['tags'] = []

    return render_template('minutespage1.html', minutes=minutes, project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/minutespage2')
def page2(project_id):
    project_name = get_project_name(project_id)
    return render_template('minutespage2.html', project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/minutessubmit', methods=['POST'])
def submit(project_id):
    data = request.json
    title = data['title']
    content = data['content']
    tags = data['tags']
    
    author = 'naboyeong'
    create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO Minutes (Title, Content, Author, CreateDate, project_id) VALUES (%s, %s, %s, %s, %s)",
            (title, content, author, create_date, project_id)
        )
        post_id = cursor.lastrowid

        for tag in tags:
            tag = tag.strip().lower()
            cursor.execute("SELECT id FROM minutestagslist WHERE name = %s", (tag,))
            tag_data = cursor.fetchone()

            if not tag_data:
                cursor.execute("INSERT INTO minutestagslist (name) VALUES (%s)", (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_data[0]

            cursor.execute("INSERT INTO minute_tags (Minutes_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

    return jsonify({"success": True, "message": "Note saved.", "minutes_id": post_id})

@app.route('/projects/<int:project_id>/minutespage4/<int:minutes_id>')
def show_minutes(project_id, minutes_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Minutes WHERE MinutesID = %s AND project_id = %s", (minutes_id, project_id))
    minute = cursor.fetchone()
    
    cursor.execute("""
        SELECT t.name FROM minutestagslist t
        JOIN minute_tags mt ON t.id = mt.tag_id
        WHERE mt.Minutes_id = %s
    """, (minutes_id,))
    tags = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    tag_list = [tag['name'] for tag in tags]
    project_name = get_project_name(project_id)
    return render_template('minutespage4.html', minute=minute, tags=tag_list, project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/delete/<int:minutes_id>', methods=['POST'])
def delete_minutes(project_id, minutes_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM minute_tags WHERE Minutes_id = %s", (minutes_id,))
    cursor.execute("DELETE FROM Minutes WHERE MinutesID = %s AND project_id = %s", (minutes_id, project_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('page1', project_id=project_id))

@app.route('/projects/<int:project_id>/minutes/update/<int:minutes_id>', methods=['POST'])
def update_minute(project_id, minutes_id):
    title = request.form['title']
    content = request.form['content']
    tags_str = request.form.get('tags', '')
    
    new_tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Minutes SET Title = %s, Content = %s WHERE MinutesID = %s AND project_id = %s", (title, content, minutes_id, project_id))

    cursor.execute("SELECT t.id, t.name FROM minutestagslist t JOIN minute_tags mt ON t.id = mt.tag_id WHERE mt.Minutes_id = %s", (minutes_id,))
    existing_tags = cursor.fetchall()
    existing_tag_names = [tag[1] for tag in existing_tags]
    existing_tag_ids = {tag[1]: tag[0] for tag in existing_tags}

    for tag in new_tags:
        if tag not in existing_tag_names:
            cursor.execute("SELECT id FROM minutestagslist WHERE name = %s", (tag,))
            tag_data = cursor.fetchone()
            if not tag_data:
                cursor.execute("INSERT INTO minutestagslist (name) VALUES (%s)", (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_data[0]

            cursor.execute("INSERT INTO minute_tags (Minutes_id, tag_id) VALUES (%s, %s)", (minutes_id, tag_id))

    for existing_tag_name in existing_tag_names:
        if existing_tag_name not in new_tags:
            cursor.execute("DELETE FROM minute_tags WHERE Minutes_id = %s AND tag_id = %s", (minutes_id, existing_tag_ids[existing_tag_name]))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f'/projects/{project_id}/minutespage4/' + str(minutes_id))

@app.route('/projects/<int:project_id>/minutes/edit/<int:minutes_id>')
def edit_minutes(project_id, minutes_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Minutes WHERE MinutesID = %s AND project_id = %s", (minutes_id, project_id))
    minute = cursor.fetchone()
    
    cursor.execute("""
        SELECT t.name FROM minutestagslist t
        JOIN minute_tags mt ON t.id = mt.tag_id
        WHERE mt.Minutes_id = %s
    """, (minutes_id,))
    tags = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    tag_list = [tag['name'] for tag in tags]
    
    return render_template('minutespage5.html', minute=minute, tags=tag_list, project_id=project_id)

@app.route('/mainpage')
def get_projects():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 쿠키에서 사용자 이름 가져오기
        user_name = request.cookies.get('username')
        if not user_name:
            return jsonify({'message': 'User not logged in'}), 401

        print(f"Fetched username from cookie: {user_name}")  # 디버깅을 위한 출력
        
        select_query = """
        SELECT t.* 
        FROM team t 
        JOIN team_members tm ON tm.project_id = t.project_id 
        WHERE tm.member_name = %s
    """
        cursor.execute(select_query, (user_name,))
        projects = []

        for (project_id, project_name) in cursor.fetchall():
            project_info = {
                'project_id': project_id,
                'project_name': project_name,
                'members': [],
                'tags': []
            }

            select_members_query = "SELECT member_name FROM team_members WHERE project_id = %s"
            cursor.execute(select_members_query, (project_id,))
            members_result = cursor.fetchall()

            for (member_name,) in members_result:
                project_info['members'].append(member_name)

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

@app.route('/addProject', methods=['POST'])
def add_project():
    data = request.json

    project_name = data.get('projectName')
    members = data.get('projectMembers')
    tags = data.get('projectTags')

    if not project_name or not members or not tags:
        return jsonify(message='모든 필드를 입력해야 합니다.'), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_project_query = "INSERT INTO team (project_name) VALUES (%s)"
        cursor.execute(insert_project_query, (project_name,))
        project_id = cursor.lastrowid

        for member in members.split(","):
            member_name = member.strip()
            insert_member_query = "INSERT INTO team_members (project_id, member_name) VALUES (%s, %s)"
            cursor.execute(insert_member_query, (project_id, member_name))

        for tag in tags.split(","):
            tag_name = tag.strip()
            insert_tag_query = "INSERT INTO project_tags (project_id, tag_name) VALUES (%s, %s)"
            cursor.execute(insert_tag_query, (project_id, tag_name))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(message='프로젝트가 성공적으로 추가되었습니다.'), 201

    except Exception as e:
        return jsonify(message=f'프로젝트 추가에 실패했습니다: {str(e)}'), 500

@app.route('/updateProject', methods=['POST'])
def update_project():
    data = request.json

    updated_project_name = data.get('newName')
    updated_members = data.get('newMembers')
    updated_tags = data.get('newTags')
    project_id = data.get('projectId')

    if not project_id or not updated_project_name or not updated_members or not updated_tags:
        return jsonify(message='모든 필드를 입력해야 합니다.'), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        update_project_query = "UPDATE team SET project_name = %s WHERE project_id = %s"
        cursor.execute(update_project_query, (updated_project_name, project_id))

        delete_members_query = "DELETE FROM team_members WHERE project_id = %s"
        cursor.execute(delete_members_query, (project_id,))

        for member in updated_members.split(","):
            member_name = member.strip()
            insert_member_query = "INSERT INTO team_members (project_id, member_name) VALUES (%s, %s)"
            cursor.execute(insert_member_query, (project_id, member_name))

        delete_tags_query = "DELETE FROM project_tags WHERE project_id = %s"
        cursor.execute(delete_tags_query, (project_id,))

        for tag in updated_tags.split(","):
            tag_name = tag.strip()
            insert_tag_query = "INSERT INTO project_tags (project_id, tag_name) VALUES (%s, %s)"
            cursor.execute(insert_tag_query, (project_id, tag_name))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(message='프로젝트가 성공적으로 수정되었습니다.'), 200

    except Exception as e:
        app.logger.error(f'프로젝트 수정 중 오류 발생: {str(e)}')
        return jsonify(message=f'프로젝트 수정에 실패했습니다: {str(e)}'), 500

@app.route('/deleteProject/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        delete_project_query = "DELETE FROM team WHERE project_id = %s"
        cursor.execute(delete_project_query, (project_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(message='프로젝트가 성공적으로 삭제되었습니다.'), 200

    except Exception as e:
        app.logger.error(f'프로젝트 삭제 중 오류 발생: {str(e)}')
        return jsonify(message=f'프로젝트 삭제에 실패했습니다: {str(e)}'), 500

@app.route('/api/users', methods=['GET'])
def get_usernames():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        select_query = "SELECT username FROM users"
        cursor.execute(select_query)
        usernames = [row[0] for row in cursor.fetchall()]
        print("username : ", usernames)

        cursor.close()
        conn.close()

        return jsonify(usernames)
    except Exception as e:
        app.logger.error(f'사용자 조회 중 오류 발생: {str(e)}')
        return jsonify(message=f'사용자 조회에 실패했습니다: {str(e)}'), 500

# 게시판 코드
@app.route('/projects/<int:project_id>/boardpage1')
def boardpage1(project_id):
    project_name = get_project_name(project_id)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT m.boardsID, m.Title, m.Content, m.CreateDate, m.Author, GROUP_CONCAT(t.name SEPARATOR ',') AS Tags
        FROM boards m
        LEFT JOIN board_tags mt ON m.boardsID = mt.boards_id
        LEFT JOIN boardstagslist t ON mt.tag_id = t.id
        WHERE m.project_id = %s
        GROUP BY m.boardsID, m.Title, m.Content, m.CreateDate, m.Author
    """, (project_id,))
    boards = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for board in boards:
        if board['Tags']:
            board['tags'] = board['Tags'].split(',')
        else:
            board['tags'] = []

    return render_template('boardpage1.html', boards=boards, project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/boardpage2')
def boardpage2(project_id):
    project_name = get_project_name(project_id)
    return render_template('boardpage2.html', project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/boardsubmit', methods=['POST'])
def boardsubmit(project_id):
    data = request.json
    title = data['title']
    content = data['content']
    tags = data['tags']
    
    author = 'naboyeong'
    create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO boards (Title, Content, Author, CreateDate, project_id) VALUES (%s, %s, %s, %s, %s)",
            (title, content, author, create_date, project_id)
        )
        post_id = cursor.lastrowid

        for tag in tags:
            tag = tag.strip().lower()
            cursor.execute("SELECT id FROM boardstagslist WHERE name = %s", (tag,))
            tag_data = cursor.fetchone()

            if not tag_data:
                cursor.execute("INSERT INTO boardstagslist (name) VALUES (%s)", (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_data[0]

            cursor.execute("INSERT INTO board_tags (boards_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

    return jsonify({"success": True, "message": "Note saved.", "boards_id": post_id})

@app.route('/projects/<int:project_id>/boardpage4/<int:boards_id>')
def show_boards(project_id, boards_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM boards WHERE boardsID = %s AND project_id = %s", (boards_id, project_id))
    board = cursor.fetchone()
    
    cursor.execute("""
        SELECT t.name FROM boardstagslist t
        JOIN board_tags mt ON t.id = mt.tag_id
        WHERE mt.boards_id = %s
    """, (boards_id,))
    tags = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    tag_list = [tag['name'] for tag in tags]
    project_name = get_project_name(project_id)
    return render_template('boardpage4.html', board=board, tags=tag_list, project_id=project_id, project_name=project_name)

@app.route('/projects/<int:project_id>/boards/delete/<int:boards_id>', methods=['POST'])
def delete_boards(project_id, boards_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM board_tags WHERE boards_id = %s", (boards_id,))
    cursor.execute("DELETE FROM boards WHERE boardsID = %s AND project_id = %s", (boards_id, project_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('boardpage1', project_id=project_id))

@app.route('/projects/<int:project_id>/boards/update/<int:boards_id>', methods=['POST'])
def update_board(project_id, boards_id):
    title = request.form['title']
    content = request.form['content']
    tags_str = request.form.get('tags', '')
    
    new_tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE boards SET Title = %s, Content = %s WHERE boardsID = %s AND project_id = %s", (title, content, boards_id, project_id))

    cursor.execute("SELECT t.id, t.name FROM boardstagslist t JOIN board_tags mt ON t.id = mt.tag_id WHERE mt.boards_id = %s", (boards_id,))
    existing_tags = cursor.fetchall()
    existing_tag_names = [tag[1] for tag in existing_tags]
    existing_tag_ids = {tag[1]: tag[0] for tag in existing_tags}

    for tag in new_tags:
        if tag not in existing_tag_names:
            cursor.execute("SELECT id FROM boardstagslist WHERE name = %s", (tag,))
            tag_data = cursor.fetchone()
            if not tag_data:
                cursor.execute("INSERT INTO boardstagslist (name) VALUES (%s)", (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_data[0]

            cursor.execute("INSERT INTO board_tags (boards_id, tag_id) VALUES (%s, %s)", (boards_id, tag_id))

    for existing_tag_name in existing_tag_names:
        if existing_tag_name not in new_tags:
            cursor.execute("DELETE FROM board_tags WHERE boards_id = %s AND tag_id = %s", (boards_id, existing_tag_ids[existing_tag_name]))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(f'/projects/{project_id}/boardpage4/' + str(boards_id))

@app.route('/projects/<int:project_id>/boards/edit/<int:boards_id>')
def edit_boards(project_id, boards_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM boards WHERE boardsID = %s AND project_id = %s", (boards_id, project_id))
    board = cursor.fetchone()
    
    cursor.execute("""
        SELECT t.name FROM boardstagslist t
        JOIN board_tags mt ON t.id = mt.tag_id
        WHERE mt.boards_id = %s
    """, (boards_id,))
    tags = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    tag_list = [tag['name'] for tag in tags]
    
    return render_template('boardpage5.html', board=board, tags=tag_list, project_id=project_id)

# 회원가입 처리를 위한 POST 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    email = data['email']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if user:
        return jsonify({'message': 'Username already exists'}), 409

    cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

# 로그인 처리를 위한 POST 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'Username does not exist'}), 401

    hashed_password = user[2]
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({'message': 'Password is incorrect'}), 401

    cursor.close()
    conn.close()

    # 로그인 성공 시 쿠키에 사용자 이름 저장
    resp = make_response(jsonify({'message': 'Login successful'}), 200)
    resp.set_cookie('username', username)  # 사용자 이름을 쿠키에 저장
    return resp


@app.route('/loginmain')
def loginmain():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)