from flask import Flask, request, jsonify, render_template  # render_template 추가
import pymysql
import pymysql.cursors

app = Flask(__name__)

# 데이터베이스 연결 설정
def get_db_connection():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='root',
                                 database='teamteam',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

# 루트 경로 - 할 일 목록 페이지 렌더링
@app.route('/todos')
def index():
    return render_template('todos.html')

# 캘린더 페이지 라우트 추가
@app.route('/calendar')  # 캘린더 페이지 경로
def calendar():
    return render_template('calendar.html')

# 할 일 목록 가져오기
@app.route('/api/todos', methods=['GET'])
def get_todos():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, description, deadline, completed FROM todos")
            todos = cursor.fetchall()
            return jsonify(todos)
    finally:
        connection.close()

# 할 일 추가
@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.json
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO todos (description, deadline, completed) VALUES (%s, %s, %s)"
            cursor.execute(sql, (data['description'], data['deadline'], data.get('completed', False)))
            connection.commit()
            return jsonify({'id': cursor.lastrowid}), 201
    finally:
        connection.close()

# 할 일 수정
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.json
    description = data.get('description')
    deadline = data.get('deadline')
    completed = data.get('completed', None)
    
    if completed is None:
        return jsonify({'error': 'completed field is required'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE todos SET description=%s, deadline=%s, completed=%s WHERE id=%s"
            cursor.execute(sql, (description, deadline, completed, todo_id))
            connection.commit()
            return jsonify({'success': True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()



# 할 일 삭제
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM todos WHERE id=%s"
            cursor.execute(sql, (todo_id,))
            connection.commit()
            return jsonify({'success': True}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

# 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)