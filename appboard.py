from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
import mysql.connector

app = Flask(__name__)

db_config = {
    'user': 'root',
    'password': '2802',
    'host': 'localhost',
    'database': 'serverproject'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page1():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # 쿼리 실행: Minutes와 관련된 태그를 모두 가져옵니다.
    cursor.execute("""
        SELECT m.MinutesID, m.Title, m.Content, m.CreateDate, m.Author, GROUP_CONCAT(t.name SEPARATOR ',') AS Tags
        FROM Minutes m
        LEFT JOIN minute_tags mt ON m.MinutesID = mt.Minutes_id
        LEFT JOIN minutestagslist t ON mt.tag_id = t.id
        GROUP BY m.MinutesID, m.Title, m.Content, m.CreateDate, m.Author
    """)
    minutes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # 각 minute의 'Tags' 값을 리스트로 변환
    for minute in minutes:
        if minute['Tags']:
            minute['tags'] = minute['Tags'].split(',')
        else:
            minute['tags'] = []

    return render_template('page1.html', minutes=minutes)


@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/page3')
def page3_data():
    return render_template('page3.html')

@app.route('/api/notes')
def notes_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Minutes")  # 데이터를 가져올 테이블 이름
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # notes 변수에 저장된 데이터를 JSON 형태로 반환합니다.
    return jsonify(notes)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    title = data['title']
    content = data['content']
    tags = data['tags']
    
    author = 'naboyeong'
    create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 데이터베이스 연결 및 커서 생성
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        # Minutes 테이블에 데이터 삽입
        cursor.execute(
            "INSERT INTO Minutes (Title, Content, Author, CreateDate) VALUES (%s, %s, %s, %s)",
            (title, content, author, create_date)
        )
        post_id = cursor.lastrowid

        # 각 태그 처리
        for tag in tags:
            tag = tag.strip().lower()
            cursor.execute("SELECT id FROM minutestagslist WHERE name = %s", (tag,))
            tag_data = cursor.fetchone()

            if not tag_data:
                # 새로운 태그인 경우 삽입
                cursor.execute("INSERT INTO minutestagslist (name) VALUES (%s)", (tag,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag_data[0]

            # 연결 테이블에 추가
            cursor.execute("INSERT INTO minute_tags (Minutes_id, tag_id) VALUES (%s, %s)", (post_id, tag_id))

        # 커밋
        conn.commit()
    except Exception as e:
        # 에러 발생 시 롤백
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        # 리소스 해제
        cursor.close()
        conn.close()

    return jsonify({"success": True, "message": "Note saved."})



@app.route('/page4/<int:minutes_id>')
def show_minutes(minutes_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Minutes WHERE MinutesID = %s", (minutes_id,))
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
    return render_template('page4.html', minute=minute, tags=tag_list)


@app.route('/delete/<int:minutes_id>', methods=['POST'])
def delete_minutes(minutes_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Minutes WHERE MinutesID = %s", (minutes_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('page1'))  # 삭제 후 리다이렉트할 페이지

@app.route('/minutes/update/<int:minutes_id>', methods=['POST'])
def update_minute(minutes_id):
    title = request.form['title']
    content = request.form['content']
    tags_str = request.form.get('tags', '')
    
    # 쉼표로 구분된 태그 문자열을 리스트로 변환
    new_tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

    # 데이터베이스 연결 및 업데이트
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE Minutes SET Title = %s, Content = %s WHERE MinutesID = %s", (title, content, minutes_id))

    # 기존 태그를 가져오고 그 이름 목록과 ID 매핑 테이블을 만듭니다.
    cursor.execute("SELECT t.id, t.name FROM minutestagslist t JOIN minute_tags mt ON t.id = mt.tag_id WHERE mt.Minutes_id = %s", (minutes_id,))
    existing_tags = cursor.fetchall()
    existing_tag_names = [tag[1] for tag in existing_tags]
    existing_tag_ids = {tag[1]: tag[0] for tag in existing_tags}

    # 새 태그 추가 로직
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

    # 기존 태그 중 새 태그 리스트에 없는 태그를 제거
    for existing_tag_name in existing_tag_names:
        if existing_tag_name not in new_tags:
            cursor.execute("DELETE FROM minute_tags WHERE Minutes_id = %s AND tag_id = %s", (minutes_id, existing_tag_ids[existing_tag_name]))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/page4/' + str(minutes_id))




@app.route('/minutes/edit/<int:minutes_id>')
def edit_minutes(minutes_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Minutes WHERE MinutesID = %s", (minutes_id,))
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
    
    return render_template('page5.html', minute=minute, tags=tag_list)

@app.route('/test')
def test222():
    return render_template('test.html')




if __name__ == '__main__':
    app.run(debug=True)

