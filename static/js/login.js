document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 폼의 기본 제출 동작 방지

        // 사용자 이름과 비밀번호 가져오기
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            // 서버로 로그인 요청 보내기
            const response = await fetch('http://localhost:3000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            // 로그인 응답 처리
            if (!response.ok) {
                const errorResponse = await response.json(); // 서버 응답 본문을 JSON으로 파싱
                console.error('Login Error:', errorResponse.message); // 콘솔에 오류 메시지 출력
                alert(`Login Error: ${errorResponse.message}`); // 사용자에게 오류 메시지를 알림
                return; // 함수 실행 종료
            }

            // 로그인 성공 처리
            const data = await response.json(); // 성공 응답을 JSON으로 파싱
            console.log('Login Success:', data.message);
            alert('Login Success!'); // 성공 메시지를 사용자에게 알림

            // 로그인 성공 후 처리, 예: 메인 페이지로 리다이렉션
            window.location.href = 'http://127.0.0.1:5500/main.html'; // 성공 시 리다이렉션할 경로로 변경하세요

        } catch (error) {
            console.error('Login Error:', error);
            alert('Login Error: An error occurred while processing your request.'); // 네트워크 오류 등의 경우 사용자에게 알림
        }
    });
})
