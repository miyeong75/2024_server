let addedMembers = [];
let editedMembers = [];
let selectedProject = null; // 선택된 프로젝트를 저장할 변수

let memberList = [];

// 페이지 로딩 시 서버에서 사용자 목록을 가져옵니다.
window.onload = function() {
    fetch(`/api/users`)
        .then(response => response.json())
        .then(data => {
            memberList = data;
            console.log('Updated member list:', memberList);
        })
        .catch(error => console.error('Error fetching user list:', error));
};

function showAddProjectPopup() {
    document.getElementById("addProjectPopup").style.display = "block";
}

function closeAddProjectPopup() {
    document.getElementById("addProjectPopup").style.display = "none";
    resetAddProjectForm();
}

function resetAddProjectForm() {
    document.getElementById("newProjectName").value = "";
    document.getElementById("newProjectMembers").value = "";
    document.getElementById("newProjectTags").value = "";
    addedMembers = [];
    updateMemberList("addedMembersContainer", addedMembers);
}

function addMemberToList() {
    const memberInput = document.getElementById("newProjectMembers");
    const memberName = memberInput.value.trim();

    // 입력값이 비어 있는지 확인
    if (memberName === "") {
        alert("팀원 이름을 입력해주세요.");
        return;
    }

    // 입력값이 회원 리스트에 존재하는지 확인
    if (memberList.includes(memberName)) {
        addedMembers.push(memberName);
        updateMemberList("addedMembersContainer", addedMembers);
        memberInput.value = "";
    } else {
        alert("회원 리스트에 존재하지 않는 팀원입니다.");
    }
}


      function addNewMember(inputId, containerId) {
        const memberInput = document.getElementById(inputId);
        const memberName = memberInput.value.trim();

        if (memberName !== "" && memberList.includes(memberName)) {
          editedMembers.push(memberName);
          updateMemberList(containerId, editedMembers);
          memberInput.value = "";
        } else {
          alert("회원 리스트에 존재하지 않는 팀원입니다.");
        }
      }

function showEditPopup(button) {
      const projectElement = button.closest(".project");
      if (!projectElement) {
        console.error("프로젝트 요소를 찾을 수 없습니다.");
    return;
}

  // 선택된 프로젝트 저장
  selectedProject = projectElement;

  // 프로젝트 ID 가져오기
  const projectId = projectElement.dataset.projectId; // 수정이 필요한 부분

  // 팝업창 요소에 프로젝트명, 팀원, 태그 입력
  const projectName = projectElement.querySelector(".project-name").textContent;
  const projectMembers = projectElement.querySelector(".project-members").textContent;
  const tagElements = projectElement.querySelectorAll(".tag");
  const projectTags = Array.from(tagElements)
    .map((tag) => tag.textContent)
    .join(", ");

  // 프로젝트 ID를 hidden input에 설정
  document.getElementById("editProjectId").value = projectId; // 수정이 필요한 부분

  document.getElementById("editName").value = projectName;
  document.getElementById("editMembersContainer").innerHTML = ""; // 기존 팀원 목록 초기화

  // 기존 팀원 추가
  projectMembers
    .split(":")[1]
    .trim()
    .split(",")
    .forEach((member) => {
      editedMembers.push(member.trim());
    });
  updateMemberList("editMembersContainer", editedMembers);

  document.getElementById("editTags").value = projectTags;

  // 수정 팝업창 표시
  const editPopup = document.getElementById("editPopup");
  if (editPopup) {
    editPopup.style.display = "block";
  } else {
    console.error("수정 팝업창을 찾을 수 없습니다.");
  }
}


  function updateMemberList(containerId, members) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    members.forEach((member) => {
      const memberHTML = `
                <div>
                    ${member}
                    <span style="cursor: pointer;" onclick="removeMember('${member}', '${containerId}')"> X </span>
                </div>
            `;
      container.insertAdjacentHTML("beforeend", memberHTML);
    });
  }

  function removeMember(member, containerId) {
    const members =
      containerId === "addedMembersContainer"
        ? addedMembers
        : editedMembers;
    const updatedMembers = members.filter((m) => m !== member);
    if (containerId === "addedMembersContainer") {
      addedMembers = updatedMembers;
    } else {
      editedMembers = updatedMembers;
    }
    updateMemberList(containerId, updatedMembers);
  }

function addProject() {
  const projectName = document.getElementById("newProjectName").value.trim();
  const projectMembers = addedMembers.join(", ");
  const projectTags = document.getElementById("newProjectTags").value.trim();
  const projectPublic = 1; //공개설정

  if (projectName === "" || projectMembers === "" || projectTags === "") {
    alert("프로젝트명, 팀원, 태그를 모두 입력해주세요.");
    return;
  }

  closeAddProjectPopup();

  // Fetch API를 사용하여 서버에 POST 요청 보내기
  const requestData = {
    projectName,
    projectMembers,
    projectTags,
    projectPublic,
  };

  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
  };

  fetch(`/addProject`, requestOptions)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data.message); // 성공 메시지 출력
      // 추가 팝업창 닫기
      closeAddProjectPopup();
      location.reload();
    })
    .catch(error => {
      console.error('프로젝트 추가 실패:', error);
      // 실패 시 처리 (예: 오류 메시지 표시)
      alert('프로젝트 추가에 실패했습니다.');
    });
}


      function generateTagElements(tagsString) {
        const tags = tagsString.split(",").map((tag) => tag.trim());
        return tags.map((tag) => `<div class="tag">${tag}</div>`).join("");
      }

     function deleteProject(button) {
    // 클릭된 요소의 부모 요소인 project 클래스를 가진 요소에서 프로젝트 ID를 가져옴
    const projectId = button.closest('.project').dataset.projectId;

    // 삭제 요청 보내기
    const requestOptions = {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    fetch(`/deleteProject/${projectId}`, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message); // 성공 메시지 출력
            // 프로젝트 삭제 성공 시 추가 작업 수행
            // 예: 페이지 새로고침 또는 삭제된 프로젝트를 UI에서 제거
            location.reload();
        })
        .catch(error => {
            console.error('프로젝트 삭제 실패:', error);
            // 실패 시 처리 (예: 오류 메시지 표시)
            alert('프로젝트 삭제에 실패했습니다.');
        });
}

function deleteProjectFromServer(projectId) {
    // 서버로 프로젝트 삭제 요청 보내기
    const requestOptions = {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    };

    fetch(`/deleteProject/${projectId}`, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message); // 성공 메시지 출력
            // 프로젝트 삭제 성공 시 추가 작업 수행
            // 예: 페이지 새로고침 또는 삭제된 프로젝트를 UI에서 제거
            location.reload();
        })
        .catch(error => {
            console.error('프로젝트 삭제 실패:', error);
            // 실패 시 처리 (예: 오류 메시지 표시)
            alert('프로젝트 삭제에 실패했습니다.');
        });
}


     function addMemberToList() {
    const memberInput = document.getElementById("newProjectMembers");
    const memberName = memberInput.value.trim();

    // 입력값이 비어 있는지 확인
    if (memberName === "") {
        alert("팀원 이름을 입력해주세요.");
        return;
    }

    // 입력값이 회원 리스트에 존재하는지 확인
    if (memberList.includes(memberName)) {
        addedMembers.push(memberName);
        updateMemberList("addedMembersContainer", addedMembers);
        memberInput.value = "";
    } else {
        alert("회원 리스트에 존재하지 않는 팀원입니다.");
    }
}


      function closeEditPopup() {
        document.getElementById("editPopup").style.display = "none";
        editedMembers = []; // 편집된 멤버 초기화
      }

      function saveChanges() {
    // 선택된 프로젝트가 없는 경우 오류 처리
    if (!selectedProject) {
        console.error("선택된 프로젝트가 없습니다.");
        return;
    }

    // 선택된 프로젝트의 ID 가져오기
    const projectElement = selectedProject.closest(".project");
    if (!projectElement) {
        console.error("프로젝트 요소를 찾을 수 없습니다.");
        return;
    }
    const projectId = projectElement.getAttribute("data-project-id");

    // 수정할 프로젝트의 새로운 정보 가져오기
    const newName = document.getElementById("editName").value.trim();
    const newMembers = editedMembers.join(", ");
    const newTags = document.getElementById("editTags").value.trim();

    // 프로젝트 정보가 모두 입력되었는지 확인
    if (newName === "" || newMembers === "" || newTags === "") {
        alert("프로젝트명, 팀원, 태그를 모두 입력해주세요.");
        return;
    }

    // 수정할 프로젝트 정보와 함께 서버로 요청 보내기
    const requestData = {
        projectId,
        newName,
        newMembers,
        newTags,
    };

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    };

    fetch(`/updateProject`, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data.message); // 성공 메시지 출력
            // 수정 팝업창 닫기 등의 추가 작업 수행
            closeEditPopup();
            location.reload();
        })
        .catch(error => {
            console.error('프로젝트 업데이트 실패:', error);
            // 실패 시 처리 (예: 오류 메시지 표시)
            alert('프로젝트 업데이트에 실패했습니다.');
        });
}

      function showDropdown(button) {
        const dropdownContent = button.nextElementSibling;
        dropdownContent.style.display =
          dropdownContent.style.display === "block" ? "none" : "block";
      }






function joinProject(button) {
    const projectElement = button.closest(".project");
    if (!projectElement) {
        console.error("프로젝트 요소를 찾을 수 없습니다.");
        return;
    }

    const projectId = projectElement.dataset.projectId;

    fetch('/joinProject', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId: projectId }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('프로젝트에 성공적으로 참여했습니다.');
        } else {
            alert('프로젝트 참여에 실패했습니다: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('프로젝트 참여 중 오류가 발생했습니다.');
    });
}
    




      
function goToTodos(element) {
            // 'data-project-id' 속성 값 가져오기
            const projectId = element.getAttribute('data-project-id');
            // 새로운 URL로 이동
            window.location.href = `/projects/${projectId}/todos`;
        }

function goToMypage() {
    window.location.href = `/mypage`;
}

function goToLogin() {
  window.location.href = `/`;
}

function goTopublicproject() {
  window.location.href = `/projectspublic`;
}

function goTomainpage() {
  window.location.href = `/mainpage`;
}