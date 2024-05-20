document.addEventListener("DOMContentLoaded", function () {
    // 비밀번호 찾기 버튼을 클릭하면 모달을 열도록 설정
    const forgotPasswordButton = document.querySelector("#forgot-password-button");
    const modal = document.querySelector(".modal");
    const closeButton = document.querySelector(".close");
  
    forgotPasswordButton.addEventListener("click", function () {
      modal.style.display = "block";
    });
  
    // 모달 닫기 버튼을 클릭하면 모달이 닫히도록 설정
    closeButton.addEventListener("click", function () {
      modal.style.display = "none";
    });
  
    // 모달 외부를 클릭하면 모달이 닫히도록 설정
    window.addEventListener("click", function (event) {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
  
    // Submit 버튼 클릭 시 비밀번호 재설정 링크를 이메일로 보내는 기능 구현
    const submitButton = document.querySelector("#submit-button");
  
    submitButton.addEventListener("click", function () {
      // 입력된 이메일 가져오기
      const email = document.querySelector("#email").value;
  
      // 여기서 비밀번호 재설정 링크를 해당 이메일로 보내는 코드를 작성하면 됩니다.
  
      // 임시로 콘솔에 이메일 출력
      console.log("Email: ", email);
  
      // 모달 닫기
      modal.style.display = "none";
    });
  });