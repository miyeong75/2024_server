let currentYear = new Date().getFullYear();
let currentMonth = new Date().getMonth();

// 캘린더 생성 함수
function createCalendar(year, month) {
    const monthNames = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"];
    document.getElementById('month-display').innerText = `${year}년 ${monthNames[month]}`;

    const calendar = document.getElementById('calendar');
    calendar.innerHTML = ""; // 캘린더 초기화

    const headerRow = calendar.insertRow();
    const days = ["일", "월", "화", "수", "목", "금", "토"];
    days.forEach(day => {
        const headerCell = document.createElement('th');
        headerCell.innerText = day;
        headerRow.appendChild(headerCell);
    });

    const firstDay = new Date(year, month).getDay();
    const lastDay = new Date(year, month + 1, 0).getDate();

    let date = 1;
    for (let i = 0; i < 6; i++) {
        const row = calendar.insertRow();
        for (let j = 0; j < 7; j++) {
            const cell = row.insertCell();
            cell.setAttribute('data-date', `${year}-${month + 1}-${date}`);
            const eventContainer = document.createElement('div');
            eventContainer.className = 'event-container';
            cell.appendChild(eventContainer);

            if (i === 0 && j < firstDay || date > lastDay) {
                // Skip cells before the first day of the month and after the last day
            } else {
                const dateSpan = document.createElement('span');
                dateSpan.textContent = date;
                if (date === new Date().getDate() && year === new Date().getFullYear() && month === new Date().getMonth()) {
                    dateSpan.classList.add('today');
                    cell.classList.add('today'); // 오늘 날짜 칸에 음영 추가
                }
                eventContainer.appendChild(dateSpan);
                date++;
            }
        }
    }
    // Fetch todos after calendar is setup
    fetchTodos(year, month);
}

// Fetch todos based on year and month
function fetchTodos(year, month) {
    const projectIds = JSON.parse(document.querySelector('script[data-project-ids]').getAttribute('data-project-ids')); // Fetch project IDs from the script tag
    fetch(`/api/multiple_projects_todos?project_ids=${projectIds.join(',')}`)
        .then(response => response.json())
        .then(todos => {
            todos.forEach(todo => {
                const date = new Date(todo.deadline);
                const dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
                const cell = document.querySelector(`[data-date="${dateString}"] .event-container`);
                if (cell) {
                    const eventDiv = document.createElement('div');
                    eventDiv.textContent = todo.description;
                    if (todo.completed) {
                        eventDiv.style.textDecoration = 'line-through';
                    }
                    cell.appendChild(eventDiv);
                }
            });
        })
        .catch(error => console.error('Error loading the todos:', error));
}

// 월 변경 함수
function changeMonth(step) {
    currentMonth += step;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    } else if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    createCalendar(currentYear, currentMonth);
}

window.onload = function() {
    createCalendar(currentYear, currentMonth);
};
