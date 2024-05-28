from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import mysql.connector

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'teamteam'
}

# 데이터베이스 연결 설정
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 루트 경로 - 할 일 목록 페이지 렌더링
@app.route('/projects/<int:project_id>/todos')
def index_todos(project_id):
    return render_template('todos.html', project_id=project_id)

# 캘린더 페이지 라우트 추가
@app.route('/projects/<int:project_id>/calendar')
def calendar(project_id):
    return render_template('calendar.html', project_id=project_id)

# mypage 라우트 추가
@app.route('/projects/<int:project_id>/mypage')
def mypage(project_id):
    return render_template('mypage.html', project_id=project_id)

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
    return render_template('minutesindex.html', project_id=project_id)

@app.route('/projects/<int:project_id>/minutespage1')
def page1(project_id):
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

    return render_template('minutespage1.html', minutes=minutes, project_id=project_id)

@app.route('/projects/<int:project_id>/minutespage2')
def page2(project_id):
    return render_template('minutespage2.html', project_id=project_id)

@app.route('/projects/<int:project_id>/minutespage3')
def page3_data(project_id):
    return render_template('minutespage3.html', project_id=project_id)

@app.route('/api/projects/<int:project_id>/notes')
def notes_data(project_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Minutes WHERE project_id = %s", (project_id,))
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(notes)

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

    return jsonify({"success": True, "message": "Note saved."})

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
    return render_template('minutespage4.html', minute=minute, tags=tag_list, project_id=project_id)

@app.route('/projects/<int:project_id>/delete/<int:minutes_id>', methods=['POST'])
def delete_minutes(project_id, minutes_id):
    conn = get_db_connection()
    cursor = conn.cursor()
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
    existing_tag_names = [tag['name'] for tag in existing_tags]
    existing_tag_ids = {tag['name']: tag['id'] for tag in existing_tags}

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

@app.route('/projects/<int:project_id>/minutestest')
def test222(project_id):
    return render_template('minutestest.html', project_id=project_id)

if __name__ == '__main__':
    app.run(debug=True)
