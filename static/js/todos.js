window.onload = function() {
  fetchTodos(); // 페이지 로딩 시 할 일 목록을 불러옵니다.

  document.getElementById('modal-save').addEventListener('click', function() {
    const todoId = document.getElementById('todo-id').value;
    const todoText = document.getElementById('todo-content').value;
    const deadline = document.getElementById('todo-date').value;
    if (todoText && deadline) {
      if (todoId) {
        updateTodo(todoId, todoText, deadline);
      } else {
        saveTodo(todoText, deadline); // 서버에 할 일 추가 요청을 보냅니다.
      }
      closeModal(); // 모달 닫기
    }
  });

  document.getElementById('modal-cancel').addEventListener('click', closeModal);
  document.querySelector('.close-button').addEventListener('click', closeModal);

  window.addEventListener('click', function(event) {
    if (event.target.className === 'modal') {
      closeModal();
    }
  });

  // '할 일 추가' 버튼 클릭 시 모달 열기
  document.querySelector('.add-todo').addEventListener('click', function() {
    addNewTodo(); // 모달 열기
  });
};

function fetchTodos() {
  fetch(`/api/projects/${projectId}/todos`)
    .then(response => response.json())
    .then(data => {
      const todoList = document.getElementById('todo-list');
      todoList.innerHTML = ''; // 기존 목록 초기화
      data.forEach(todo => {
        const deadline = new Date(todo.deadline);
        const formattedDeadline = deadline.toLocaleDateString('ko-KR', { 
          weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
        });
        const newTodoItem = document.createElement('div');
        newTodoItem.classList.add('todo-item');
        newTodoItem.innerHTML = `
          <span class="todo-text">${todo.description}</span>
          <span class="todo-deadline">마감: ${formattedDeadline}</span>
          <div class="todo-actions">
            <button class="edit-todo" onclick="editTodo(${todo.id}, '${todo.description}', '${todo.deadline}')">수정</button><button class="delete-todo" onclick="deleteTodo(${todo.id})">삭제</button>
          </div>
          <input type="checkbox" ${todo.completed ? 'checked' : ''} data-id="${todo.id}" class="todo-checkbox">
        `;
        todoList.appendChild(newTodoItem);

        // 체크박스에 대한 이벤트 리스너를 추가
        newTodoItem.querySelector('input[type="checkbox"]').addEventListener('change', function(e) {
          updateTodoCompleted(this, e.target.checked, todo.description, todo.deadline);
        });
      });
    })
    .catch(error => console.error('Error loading the todos:', error));
}

function updateTodoCompleted(element, completed, description, deadline) {
  const todoId = element.dataset.id;  // data-id 속성을 사용하여 ID를 가져옵니다.
  const formattedDeadline = new Date(deadline).toISOString().split('T')[0]; // Convert to 'YYYY-MM-DD' format
  fetch(`/api/projects/${projectId}/todos/${todoId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description: description, deadline: formattedDeadline, completed: completed })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(errorData => { throw new Error(errorData.error); });
    }
    return response.json();
  })
  .then(data => {
    console.log(`Todo ${todoId} completed status updated to ${completed}`);
  })
  .catch(error => console.error('Error updating todo completed status:', error));
}

function saveTodo(todoText, deadline) {
  fetch(`/api/projects/${projectId}/todos`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description: todoText, deadline: deadline })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Todo added:', data);
    fetchTodos(); // 목록 다시 불러오기
  })
  .catch(error => console.error('Error adding todo:', error));
}

function updateTodo(todoId, todoText, deadline) {
  const formattedDeadline = new Date(deadline).toISOString().split('T')[0]; // Convert to 'YYYY-MM-DD' format
  fetch(`/api/projects/${projectId}/todos/${todoId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description: todoText, deadline: formattedDeadline, completed: false })
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(errorData => { throw new Error(errorData.error); });
    }
    return response.json();
  })
  .then(data => {
    console.log(`Todo ${todoId} updated`);
    fetchTodos(); // 목록 다시 불러오기
  })
  .catch(error => console.error('Error updating todo:', error));
}

function deleteTodo(todoId) {
  fetch(`/api/projects/${projectId}/todos/${todoId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(errorData => { throw new Error(errorData.error); });
    }
    return response.json();
  })
  .then(data => {
    console.log(`Todo ${todoId} deleted`);
    fetchTodos(); // 목록 다시 불러오기
  })
  .catch(error => console.error('Error deleting todo:', error));
}

function openModal(todoId = '', todoText = '', deadline = '') {
  document.getElementById('todo-id').value = todoId;
  document.getElementById('todo-content').value = todoText;
  document.getElementById('todo-date').value = deadline ? new Date(deadline).toISOString().split('T')[0] : '';
  document.getElementById('modal').style.display = 'block';
}

function closeModal() {
  document.getElementById('modal').style.display = 'none';
}

// 새로운 할 일 추가를 위한 함수
function addNewTodo() {
  openModal(); // 모달을 열고 새로운 할 일을 추가할 준비를 합니다.
}

// 할 일 수정을 위한 함수
function editTodo(todoId, todoText, deadline) {
  openModal(todoId, todoText, deadline); // 모달을 열고 기존 할 일 데이터를 로드합니다.
}
