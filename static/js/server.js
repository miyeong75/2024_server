const express = require('express');
const bcrypt = require('bcrypt');
const mysql = require('mysql2');
const cors = require('cors');
const app = express();

// CORS 설정: 클라이언트에서 서버로의 요청을 허용하는 설정입니다.
// 이 예에서는 'http://127.0.0.1:5500'에서 오는 요청만 허용합니다.
app.use(cors({
    origin: 'http://127.0.0.1:5500' // 특정 출처만 허용
}));

// express.json() 미들웨어를 사용하여 JSON 형식의 요청 본문을 파싱합니다.
app.use(express.json());

// MySQL 데이터베이스 연결 설정
// 이 설정은 데이터베이스 호스트, 사용자 이름, 비밀번호, 데이터베이스 이름을 포함합니다.
const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'root', // 실제 환경에서는 비밀번호를 안전하게 관리하세요.
    database: 'teamteam'
});

// 회원가입 처리를 위한 POST 라우트
app.post('/register', async (req, res) => {
    const { username, password, email } = req.body;

    // 먼저 데이터베이스에서 사용자 이름이 존재하는지 확인
    db.query('SELECT * FROM users WHERE username = ?', [username], async (error, results) => {
        if (error) {
            console.error('Database query error:', error);
            return res.status(500).json({ message: 'Error querying the database' });
        }

        if (results.length > 0) {
            // 사용자 이름이 이미 존재하는 경우
            return res.status(409).json({ message: 'Username already exists' });
        }

        // 사용자 이름이 존재하지 않는 경우, 비밀번호 해싱 후 새 사용자 등록
        const hashedPassword = await bcrypt.hash(password, 10);
        db.query(
            'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
            [username, hashedPassword, email],
            (insertError, insertResults) => {
                if (insertError) {
                    console.error('Error inserting user data:', insertError);
                    return res.status(500).json({ message: 'Error registering new user' });
                }
                res.status(201).json({ message: 'User registered successfully' });
            }
        );
    });
});

// 로그인 처리를 위한 POST 라우트
app.post('/login', (req, res) => {
    const { username, password } = req.body; // 요청 본문에서 사용자 이름과 비밀번호 추출
  
    // 데이터베이스에서 사용자 이름으로 사용자 검색
    db.query('SELECT * FROM users WHERE username = ?', [username], async (error, results) => {
      if (error) {
        console.error('Database query error:', error);
        return res.status(500).send({ message: 'Server error' }); // JSON 형식으로 오류 메시지 전송
      }
  
      if (results.length === 0) {
        // 사용자 이름이 데이터베이스에 없는 경우
        return res.status(401).json({ message: 'Username does not exist' }); // JSON 형식으로 응답 수정
      }
  
      // 사용자가 존재하면 비밀번호 검증
      const user = results[0];
      const passwordMatch = await bcrypt.compare(password, user.password);
  
      if (!passwordMatch) {
        // 비밀번호가 일치하지 않는 경우
        return res.status(401).json({ message: 'Password is incorrect' }); // JSON 형식으로 응답 수정
      }
  
      // 로그인 성공
      res.status(200).json({ message: 'Login successful' }); // JSON 형식으로 성공 메시지 전송
    });
  });

const PORT = 3000;
// 서버를 지정된 포트에서 실행
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));