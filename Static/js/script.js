// LeavePortal Interactive Frontend System

document.addEventListener('DOMContentLoaded', function() {
    initPasswordStrengthChecker();
    initDateCalculator();
    initTaskTogglers();
    initInteractiveCalendar();
});

// 1. Password Strength Checker
function initPasswordStrengthChecker() {
    const passwordInput = document.getElementById('password_strength');
    if (!passwordInput) return;

    const lengthItem = document.getElementById('req_length');
    const upperItem = document.getElementById('req_uppercase');
    const lowerItem = document.getElementById('req_lowercase');
    const numberItem = document.getElementById('req_number');
    const specialItem = document.getElementById('req_special');

    passwordInput.addEventListener('keyup', function() {
        const val = passwordInput.value;

        // Check length
        toggleItem(lengthItem, val.length >= 8);
        // Check uppercase
        toggleItem(upperItem, /[A-Z]/.test(val));
        // Check lowercase
        toggleItem(lowerItem, /[a-z]/.test(val));
        // Check number
        toggleItem(numberItem, /[0-9]/.test(val));
        // Check special char
        toggleItem(specialItem, /[_@$!%*#?&]/.test(val));
    });

    function toggleItem(item, isValid) {
        if (!item) return;
        if (isValid) {
            item.classList.add('valid');
        } else {
            item.classList.remove('valid');
        }
    }
}

// 2. Leave Application Date Calculator
function initDateCalculator() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    const displayBox = document.getElementById('date_calc_display');

    if (!startDateInput || !endDateInput || !displayBox) return;

    startDateInput.addEventListener('change', calculateDays);
    endDateInput.addEventListener('change', calculateDays);

    function calculateDays() {
        const startStr = startDateInput.value;
        const endStr = endDateInput.value;

        if (!startStr || !endStr) {
            displayBox.style.display = 'none';
            return;
        }

        const start = new Date(startStr);
        const end = new Date(endStr);

        if (end < start) {
            displayBox.style.display = 'block';
            displayBox.innerHTML = '<span style="color: var(--danger); font-weight: bold;">Error: End Date cannot be before Start Date!</span>';
            return;
        }

        // Count business days (skipping Sat/Sun)
        let count = 0;
        let cur = new Date(start);
        while (cur <= end) {
            const dayOfWeek = cur.getDay(); // 0 is Sunday, 6 is Saturday
            if (dayOfWeek !== 0 && dayOfWeek !== 6) {
                count++;
            }
            cur.setDate(cur.getDate() + 1);
        }

        displayBox.style.display = 'block';
        if (count === 0) {
            displayBox.innerHTML = '<span style="color: var(--warning); font-weight: bold;">Warning: Selected dates fall entirely on weekends. 0 leaves will be deducted.</span>';
        } else {
            displayBox.innerHTML = `<span style="color: var(--success); font-weight: bold;">Total leave days: ${count} business day(s)</span> (excluding weekends)`;
        }
    }
}

// 3. Real-time Task Status Toggler
function initTaskTogglers() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    checkboxes.forEach(cb => {
        cb.addEventListener('click', function() {
            const taskId = this.getAttribute('data-id');
            const taskText = document.getElementById(`task-text-${taskId}`);
            
            fetch(`/task/toggle/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.new_status === 'Completed') {
                        this.classList.add('checked');
                        if (taskText) taskText.classList.add('checked');
                    } else {
                        this.classList.remove('checked');
                        if (taskText) taskText.classList.remove('checked');
                    }
                }
            })
            .catch(err => console.error("Error toggling task status:", err));
        });
    });
}

// 4. Interactive Calendar Renderer
function initInteractiveCalendar() {
    const container = document.getElementById('calendar_container');
    if (!container) return;

    // Load calendar events from global variable defined in templates
    const rawEvents = window.calendarEvents || [];
    
    // Parse calendar events date strings
    const events = rawEvents.map(e => ({
        ...e,
        startDate: new Date(e.start),
        endDate: new Date(e.end)
    }));

    let currentDate = new Date();
    renderMonth(currentDate.getFullYear(), currentDate.getMonth());

    function renderMonth(year, month) {
        container.innerHTML = '';
        
        // Navigation bar
        const navBar = document.createElement('div');
        navBar.className = 'calendar-nav-bar';
        
        const monthNames = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ];
        
        navBar.innerHTML = `
            <button class="btn btn-secondary" id="cal_prev" style="width: auto; padding: 6px 12px;"><i class="fas fa-chevron-left"></i> Previous</button>
            <h3 style="font-weight: 800; font-size: 18px;">${monthNames[month]} ${year}</h3>
            <button class="btn btn-secondary" id="cal_next" style="width: auto; padding: 6px 12px;">Next <i class="fas fa-chevron-right"></i></button>
        `;
        container.appendChild(navBar);
        
        // Setup Grid
        const grid = document.createElement('div');
        grid.className = 'calendar-grid';
        
        // Weekday Headers
        const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
        days.forEach(day => {
            const h = document.createElement('div');
            h.className = 'calendar-day-header';
            h.innerText = day;
            grid.appendChild(h);
        });

        // Date Calculations
        const firstDayIndex = new Date(year, month, 1).getDay();
        const lastDay = new Date(year, month + 1, 0).getDate();
        const prevLastDay = new Date(year, month, 0).getDate();
        
        // Render previous month overlap cells
        for (let x = firstDayIndex; x > 0; x--) {
            const dayNum = prevLastDay - x + 1;
            createCell(dayNum, true);
        }

        // Render current month cells
        const today = new Date();
        for (let i = 1; i <= lastDay; i++) {
            const isToday = (today.getDate() === i && today.getMonth() === month && today.getFullYear() === year);
            createCell(i, false, isToday, new Date(year, month, i));
        }

        // Render next month overlap cells
        const totalCells = firstDayIndex + lastDay;
        const rem = totalCells % 7;
        if (rem > 0) {
            const nextDays = 7 - rem;
            for (let j = 1; j <= nextDays; j++) {
                createCell(j, true);
            }
        }
        
        container.appendChild(grid);

        // Bind Nav actions
        document.getElementById('cal_prev').addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() - 1);
            renderMonth(currentDate.getFullYear(), currentDate.getMonth());
        });
        document.getElementById('cal_next').addEventListener('click', () => {
            currentDate.setMonth(currentDate.getMonth() + 1);
            renderMonth(currentDate.getFullYear(), currentDate.getMonth());
        });

        function createCell(num, isOtherMonth, isToday = false, cellDate = null) {
            const cell = document.createElement('div');
            cell.className = 'calendar-cell';
            if (isOtherMonth) cell.classList.add('other-month');
            if (isToday) cell.classList.add('today');
            
            cell.innerHTML = `<span class="calendar-date">${num}</span>`;
            
            // Add events that match this date
            if (cellDate && !isOtherMonth) {
                // Remove time parts for accurate comparison
                const cellTime = new Date(cellDate.getFullYear(), cellDate.getMonth(), cellDate.getDate()).getTime();
                
                events.forEach(evt => {
                    const startVal = new Date(evt.startDate.getFullYear(), evt.startDate.getMonth(), evt.startDate.getDate()).getTime();
                    const endVal = new Date(evt.endDate.getFullYear(), evt.endDate.getMonth(), evt.endDate.getDate()).getTime();
                    
                    if (cellTime >= startVal && cellTime <= endVal) {
                        const eventDiv = document.createElement('div');
                        eventDiv.className = 'calendar-event';
                        
                        if (evt.type === 'leave') {
                            if (evt.status === 'Approved') {
                                eventDiv.classList.add('event-leave-approved');
                            } else {
                                eventDiv.classList.add('event-leave-pending');
                            }
                        } else if (evt.type === 'team-leave') {
                            eventDiv.classList.add('event-team-leave');
                        } else {
                            eventDiv.classList.add('event-task');
                        }
                        
                        eventDiv.innerText = evt.title;
                        eventDiv.title = evt.title; // hover tooltip
                        cell.appendChild(eventDiv);
                    }
                });
            }
            grid.appendChild(cell);
        }
    }
}
