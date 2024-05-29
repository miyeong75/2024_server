document.addEventListener("DOMContentLoaded", function () {
  // 모달 요소 및 버튼 요소
  const forgotPasswordLink = document.getElementById("forgot-password-link");
  const modal = document.getElementById("forgot-password-modal");
  const closeModalButton = modal.querySelector(".close");
  const forgotPasswordForm = document.getElementById("forgot-password-form");
  const verifyCodeForm = document.getElementById("verify-code-form");

  // "Forgot Password?" 링크 클릭 시 모달 열기
  forgotPasswordLink.addEventListener("click", function (event) {
    event.preventDefault();
    modal.style.display = "block";
  });

  // 모달 닫기 버튼 클릭 시 모달 닫기
  closeModalButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // 모달 외부 클릭 시 모달 닫기
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  // "Send Verification Code" 버튼 클릭 시
  forgotPasswordForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const username = document.getElementById("forgot-username").value;
    const email = document.getElementById("forgot-email").value;

    fetch('/send_verification_code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        forgotPasswordForm.style.display = "none";
        verifyCodeForm.style.display = "block";
      } else {
        alert(data.message);
      }
    });
  });

  // "Verify and Show Password" 버튼 클릭 시
  verifyCodeForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const verificationCode = document.getElementById("verification-code").value;

    fetch('/verify_code_and_get_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ verification_code: verificationCode })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert(`Your password is: ${data.password}`);
        modal.style.display = "none";
        forgotPasswordForm.reset();
        verifyCodeForm.reset();
        forgotPasswordForm.style.display = "block";
        verifyCodeForm.style.display = "none";
      } else {
        alert(data.message);
      }
    });
  });
});
