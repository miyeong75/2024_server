document.addEventListener('DOMContentLoaded', function () {
    var signupForm = document.getElementById('signupForm');

    signupForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var username = document.getElementById('signup-user').value;
        var password = document.getElementById('signup-pass').value;
        var repeatPassword = document.getElementById('signup-repeat-pass').value;
        var email = document.getElementById('signup-email').value;

        if (password !== repeatPassword) {
            alert('비밀번호가 일치하지 않습니다. 다시 확인해 주세요.');
            return;
        }

        console.log('Username:', username, 'Password:', password, 'Repeat Password:', repeatPassword, 'Email:', email);

        fetch('http://localhost:3000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: email
            })
        })
        .then(response => {
            if (response.status === 409) { // 이미 사용자 이름이 존재하는 경우
                throw new Error('Username already exists');
            } else if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            alert('회원가입이 성공적으로 완료되었습니다.');
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
            alert(error.message); // 수정된 부분: 에러 메시지를 보다 구체적으로 표시
        });
    });
});