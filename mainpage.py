import mysql.connector
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# MySQL 데이터베이스 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'teamteam'
}

# MySQL 연결 객체 생성
db_connection = mysql.connector.connect(**db_config)

# 커서 생성
db_cursor = db_connection.cursor()

@app.route('/mainpage')
def get_projects():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        user_name = "A"
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

@app.route('/addProject', methods=['POST'])
def add_project():
    data = request.json

    project_name = data.get('projectName')
    members = data.get('projectMembers')
    tags = data.get('projectTags')

    if not project_name or not members or not tags:
        return jsonify(message='모든 필드를 입력해야 합니다.'), 400

    try:
        # MySQL 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 프로젝트 정보 삽입
        insert_project_query = "INSERT INTO team (project_name) VALUES (%s)"
        cursor.execute(insert_project_query, (project_name,))
        project_id = cursor.lastrowid

        # 팀원 정보 삽입
        for member in members.split(","):
            member_name = member.strip()  # 공백 제거
            insert_member_query = "INSERT INTO team_members (project_id, member_name) VALUES (%s, %s)"
            cursor.execute(insert_member_query, (project_id, member_name))

        # 태그 정보 삽입
        for tag in tags.split(","):
            tag_name = tag.strip()
            insert_tag_query = "INSERT INTO project_tags (project_id, tag_name) VALUES (%s, %s)"
            cursor.execute(insert_tag_query, (project_id, tag_name))

        # 변경 사항 커밋
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(message='프로젝트가 성공적으로 추가되었습니다.'), 201

    except Exception as e:
        return jsonify(message=f'프로젝트 추가에 실패했습니다: {str(e)}'), 500


# 여기에 수정된 코드를 넣어주세요
@app.route('/updateProject', methods=['POST'])
def update_project():
    data = request.json

    updated_project_name = data.get('newName')
    updated_members = data.get('newMembers')
    updated_tags = data.get('newTags')
    project_id = data.get('projectId')  # 프로젝트 ID를 요청에서 받아옴

    if not project_id or not updated_project_name or not updated_members or not updated_tags:
        return jsonify(message='모든 필드를 입력해야 합니다.'), 400

    try:
        # MySQL 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 프로젝트 정보 업데이트
        update_project_query = "UPDATE team SET project_name = %s WHERE project_id = %s"
        cursor.execute(update_project_query, (updated_project_name, project_id))

        # 기존 팀원 정보 삭제
        delete_members_query = "DELETE FROM team_members WHERE project_id = %s"
        cursor.execute(delete_members_query, (project_id,))

        # 수정된 팀원 정보 삽입
        for member in updated_members.split(","):
            member_name = member.strip()  # 공백 제거
            insert_member_query = "INSERT INTO team_members (project_id, member_name) VALUES (%s, %s)"
            cursor.execute(insert_member_query, (project_id, member_name))

        # 기존 태그 정보 삭제
        delete_tags_query = "DELETE FROM project_tags WHERE project_id = %s"
        cursor.execute(delete_tags_query, (project_id,))

        # 수정된 태그 정보 삽입
        for tag in updated_tags.split(","):
            tag_name = tag.strip()
            insert_tag_query = "INSERT INTO project_tags (project_id, tag_name) VALUES (%s, %s)"
            cursor.execute(insert_tag_query, (project_id, tag_name))

        # 변경 사항 커밋
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
        # MySQL 데이터베이스 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 프로젝트 삭제
        delete_project_query = "DELETE FROM team WHERE project_id = %s"
        cursor.execute(delete_project_query, (project_id,))

        # 변경 사항 커밋
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(message='프로젝트가 성공적으로 삭제되었습니다.'), 200

    except Exception as e:
        app.logger.error(f'프로젝트 삭제 중 오류 발생: {str(e)}')
        return jsonify(message=f'프로젝트 삭제에 실패했습니다: {str(e)}'), 500


if __name__ == '__main__':
    app.run(debug=True)
