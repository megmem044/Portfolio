// Task Manager Application
class TaskManager {
    constructor() {
        this.tasks = this.loadTasks();
        this.categories = this.loadCategories();
        this.currentFilter = 'all';
        this.currentView = 'day';
        this.currentDate = new Date();
        this.searchQuery = '';
        this.editingTaskId = null;
        this.selectedCategoryColor = null;
        
        this.initializeElements();
        this.bindEvents();
        this.renderCategories();
        this.render();
    }
    
    loadCategories() {
        const saved = localStorage.getItem('toodle_categories');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveCategories() {
        localStorage.setItem('toodle_categories', JSON.stringify(this.categories));
    }
    
    initializeElements() {
        this.taskList = document.getElementById('taskList');
        this.emptyState = document.getElementById('emptyState');
        this.searchInput = document.getElementById('searchInput');
        
        this.totalCount = document.getElementById('totalCount');
        this.activeCount = document.getElementById('activeCount');
        this.completedCount = document.getElementById('completedCount');
        
        this.addTaskBtn = document.getElementById('addTaskBtn');
        this.menuBtn = document.getElementById('menuBtn');
        this.dropdownMenu = document.getElementById('dropdownMenu');
        this.clearCompletedBtn = document.getElementById('clearCompletedBtn');
        
        // View elements
        this.viewOptions = document.querySelectorAll('.view-option');
        this.dayView = document.getElementById('dayView');
        this.weekView = document.getElementById('weekView');
        this.monthView = document.getElementById('monthView');
        this.weekGrid = document.getElementById('weekGrid');
        this.monthGrid = document.getElementById('monthGrid');
        
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.todayBtn = document.getElementById('todayBtn');
        this.currentDateLabel = document.getElementById('currentDateLabel');
        
        this.filterBtns = document.querySelectorAll('.filter-btn');
        
        this.taskModal = document.getElementById('taskModal');
        this.modalTitle = document.getElementById('modalTitle');
        this.taskForm = document.getElementById('taskForm');
        this.taskIdInput = document.getElementById('taskId');
        this.taskTitleInput = document.getElementById('taskTitle');
        this.taskDescriptionInput = document.getElementById('taskDescription');
        this.taskStartDateInput = document.getElementById('taskStartDate');
        this.taskStartTimeInput = document.getElementById('taskStartTime');
        this.taskDueDateInput = document.getElementById('taskDueDate');
        this.taskDueTimeInput = document.getElementById('taskDueTime');
        this.priorityBtns = document.querySelectorAll('.priority-btn');
        this.categorySelector = document.getElementById('categorySelector');
        this.addCategoryBtn = document.getElementById('addCategoryBtn');
        this.newCategoryInput = document.getElementById('newCategoryInput');
        this.newCategoryName = document.getElementById('newCategoryName');
        this.colorPicker = document.getElementById('colorPicker');
        this.saveCategoryBtn = document.getElementById('saveCategoryBtn');
        this.cancelCategoryBtn = document.getElementById('cancelCategoryBtn');
        this.closeModalBtn = document.getElementById('closeModalBtn');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.deleteTaskBtn = document.getElementById('deleteTaskBtn');
        
        this.deleteModal = document.getElementById('deleteModal');
        this.cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
        this.confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        
        // Quick Add button
        this.quickAddButton = document.getElementById('quickAddButton');
    }
    
    bindEvents() {
        if (this.addTaskBtn) {
            this.addTaskBtn.addEventListener('click', () => this.openModal());
        }
        
        // Update time options when date changes
        if (this.taskStartDateInput) {
            this.taskStartDateInput.addEventListener('change', () => this.updateTimeOptions('start'));
        }
        if (this.taskDueDateInput) {
            this.taskDueDateInput.addEventListener('change', () => this.updateTimeOptions('due'));
        }
        
        // Quick Add button opens the modal
        if (this.quickAddButton) {
            this.quickAddButton.addEventListener('click', () => this.openModal());
        }
        
        if (this.menuBtn) {
            this.menuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.dropdownMenu.classList.toggle('show');
            });
        }
        
        // Prevent dropdown from closing when clicking inside it
        if (this.dropdownMenu) {
            this.dropdownMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
        
        // View options in dropdown menu
        this.viewOptions.forEach(btn => {
            btn.addEventListener('click', () => {
                this.viewOptions.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentView = btn.dataset.view;
                this.updateDateLabel();
                this.render();
                this.dropdownMenu.classList.remove('show');
            });
        });
        
        document.addEventListener('click', () => {
            if (this.dropdownMenu) this.dropdownMenu.classList.remove('show');
        });
        
        if (this.clearCompletedBtn) {
            this.clearCompletedBtn.addEventListener('click', () => this.clearCompleted());
        }
        
        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                localStorage.removeItem('currentUser');
                window.location.href = 'login.html';
            });
        }
        
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.navigateDate(-1));
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.navigateDate(1));
        }
        if (this.todayBtn) {
            this.todayBtn.addEventListener('click', () => {
                this.currentDate = new Date();
                this.updateDateLabel();
                this.render();
            });
        }
        
        this.filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFilter = btn.dataset.filter;
                this.render();
            });
        });
        
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.render();
            });
        }
        
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeModal());
        }
        if (this.cancelBtn) {
            this.cancelBtn.addEventListener('click', () => this.closeModal());
        }
        if (this.taskModal) {
            this.taskModal.addEventListener('click', (e) => {
                if (e.target === this.taskModal) this.closeModal();
            });
        }
        
        this.priorityBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.priorityBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
        
        // Color picker for new categories
        if (this.colorPicker) {
            this.colorPicker.querySelectorAll('.color-option').forEach(option => {
                option.addEventListener('click', () => {
                    this.colorPicker.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
                    option.classList.add('selected');
                    this.selectedCategoryColor = option.dataset.color;
                });
            });
        }
        
        if (this.addCategoryBtn) {
            this.addCategoryBtn.addEventListener('click', () => {
                this.newCategoryInput.classList.add('show');
                this.newCategoryName.focus();
                this.selectedCategoryColor = null;
                this.colorPicker.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            });
        }
        
        if (this.saveCategoryBtn) {
            this.saveCategoryBtn.addEventListener('click', () => {
                const name = this.newCategoryName.value.trim();
                if (name && this.selectedCategoryColor !== null) {
                    this.addNewCategory(name, this.selectedCategoryColor);
                    this.newCategoryInput.classList.remove('show');
                    this.newCategoryName.value = '';
                } else if (!name) {
                    alert('Please enter a category name');
                } else {
                    alert('Please select a color');
                }
            });
        }
        
        if (this.cancelCategoryBtn) {
            this.cancelCategoryBtn.addEventListener('click', () => {
                this.newCategoryInput.classList.remove('show');
                this.newCategoryName.value = '';
            });
        }
        
        if (this.taskForm) {
            this.taskForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveTask();
            });
        }
        
        if (this.deleteTaskBtn) {
            this.deleteTaskBtn.addEventListener('click', () => this.openDeleteModal());
        }
        
        if (this.cancelDeleteBtn) {
            this.cancelDeleteBtn.addEventListener('click', () => this.closeDeleteModal());
        }
        if (this.confirmDeleteBtn) {
            this.confirmDeleteBtn.addEventListener('click', () => {
                this.deleteTask(this.editingTaskId);
                this.closeDeleteModal();
                this.closeModal();
            });
        }
        if (this.deleteModal) {
            this.deleteModal.addEventListener('click', (e) => {
                if (e.target === this.deleteModal) this.closeDeleteModal();
            });
        }
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.closeDeleteModal();
            }
        });
    }
    
    navigateDate(direction) {
        switch (this.currentView) {
            case 'day':
                this.currentDate.setDate(this.currentDate.getDate() + direction);
                break;
            case 'week':
                this.currentDate.setDate(this.currentDate.getDate() + (direction * 7));
                break;
            case 'month':
                this.currentDate.setMonth(this.currentDate.getMonth() + direction);
                break;
        }
        this.updateDateLabel();
        this.render();
    }
    
    updateDateLabel() {
        if (!this.currentDateLabel) return;
        
        const today = new Date();
        const options = { weekday: 'short', month: 'short', day: 'numeric' };
        
        switch (this.currentView) {
            case 'day':
                if (this.isSameDay(this.currentDate, today)) {
                    this.currentDateLabel.textContent = 'Today';
                } else if (this.isSameDay(this.currentDate, new Date(today.getTime() + 86400000))) {
                    this.currentDateLabel.textContent = 'Tomorrow';
                } else if (this.isSameDay(this.currentDate, new Date(today.getTime() - 86400000))) {
                    this.currentDateLabel.textContent = 'Yesterday';
                } else {
                    this.currentDateLabel.textContent = this.currentDate.toLocaleDateString('en-US', options);
                }
                break;
            case 'week':
                const weekStart = this.getWeekStart(this.currentDate);
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekEnd.getDate() + 6);
                this.currentDateLabel.textContent = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${weekEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
                break;
            case 'month':
                this.currentDateLabel.textContent = this.currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
                break;
        }
    }
    
    getWeekStart(date) {
        const d = new Date(date);
        d.setDate(d.getDate() - d.getDay());
        d.setHours(0, 0, 0, 0);
        return d;
    }
    
    isSameDay(date1, date2) {
        return date1.getFullYear() === date2.getFullYear() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getDate() === date2.getDate();
    }
    
    isDateInRange(taskDate) {
        if (!taskDate) return false;
        
        // Parse date as local time (not UTC)
        const [year, month, day] = taskDate.split('-').map(Number);
        const date = new Date(year, month - 1, day);
        
        switch (this.currentView) {
            case 'day':
                return this.isSameDay(date, this.currentDate);
            case 'week':
                const weekStart = this.getWeekStart(this.currentDate);
                const weekEnd = new Date(weekStart);
                weekEnd.setDate(weekEnd.getDate() + 7);
                return date >= weekStart && date < weekEnd;
            case 'month':
                return date.getMonth() === this.currentDate.getMonth() &&
                       date.getFullYear() === this.currentDate.getFullYear();
        }
        return false;
    }
    
    loadTasks() {
        const saved = localStorage.getItem('tasks');
        return saved ? JSON.parse(saved) : [];
    }
    
    saveTasks() {
        localStorage.setItem('tasks', JSON.stringify(this.tasks));
    }
    
    getFilteredTasks() {
        let filtered = [...this.tasks];
        
        filtered = filtered.filter(t => this.isDateInRange(t.dueDate));
        
        if (this.currentFilter === 'active') {
            filtered = filtered.filter(t => !t.isCompleted);
        } else if (this.currentFilter === 'completed') {
            filtered = filtered.filter(t => t.isCompleted);
        }
        
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filtered = filtered.filter(t => 
                t.title.toLowerCase().includes(query) ||
                t.description.toLowerCase().includes(query)
            );
        }
        
        filtered.sort((a, b) => {
            if (a.isCompleted !== b.isCompleted) return a.isCompleted ? 1 : -1;
            if (a.dueDate && b.dueDate) return new Date(a.dueDate) - new Date(b.dueDate);
            if (a.dueDate) return -1;
            if (b.dueDate) return 1;
            const priorityOrder = { high: 3, medium: 2, low: 1 };
            return priorityOrder[b.priority] - priorityOrder[a.priority];
        });
        
        return filtered;
    }
    
    render() {
        this.updateDateLabel();
        
        // Show/hide view containers based on current view
        if (this.dayView) this.dayView.style.display = this.currentView === 'day' ? 'block' : 'none';
        if (this.weekView) this.weekView.style.display = this.currentView === 'week' ? 'block' : 'none';
        if (this.monthView) this.monthView.style.display = this.currentView === 'month' ? 'block' : 'none';
        
        // Update stats based on current view
        const viewTasks = this.tasks.filter(t => this.isDateInRange(t.dueDate));
        const total = viewTasks.length;
        const completed = viewTasks.filter(t => t.isCompleted).length;
        const active = total - completed;
        
        if (this.totalCount) this.totalCount.textContent = total;
        if (this.activeCount) this.activeCount.textContent = active;
        if (this.completedCount) this.completedCount.textContent = completed;
        
        // Render the appropriate view
        switch (this.currentView) {
            case 'day':
                this.renderDayView();
                break;
            case 'week':
                this.renderWeekView();
                break;
            case 'month':
                this.renderMonthView();
                break;
        }
    }
    
    renderDayView() {
        const filtered = this.getFilteredTasks();
        
        if (filtered.length === 0) {
            if (this.taskList) this.taskList.innerHTML = '';
            if (this.emptyState) this.emptyState.classList.add('show');
            this.updateEmptyState();
        } else {
            if (this.emptyState) this.emptyState.classList.remove('show');
            if (this.taskList) {
                this.taskList.innerHTML = filtered.map(task => this.renderTask(task)).join('');
                this.bindTaskEvents();
            }
        }
    }
    
    renderWeekView() {
        const weekSchedule = document.getElementById('weekSchedule');
        if (!weekSchedule) return;
        if (this.emptyState) this.emptyState.classList.remove('show');
        
        const weekStart = this.getWeekStart(this.currentDate);
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const today = new Date();
        
        // Find which column is today
        let todayColIndex = -1;
        for (let i = 0; i < 7; i++) {
            const day = new Date(weekStart);
            day.setDate(day.getDate() + i);
            if (this.isSameDay(day, today)) {
                todayColIndex = i;
                break;
            }
        }
        
        // Build table header with days
        let html = '<table><thead><tr><th></th>';
        for (let i = 0; i < 7; i++) {
            const day = new Date(weekStart);
            day.setDate(day.getDate() + i);
            const isToday = this.isSameDay(day, today);
            html += `<th class="${isToday ? 'today' : ''}"><span class="day-name">${days[i]}</span><span class="date-num">${day.getDate()}</span></th>`;
        }
        html += '</tr></thead><tbody>';
        
        // Get all tasks for this week with their positions
        const weekTasks = this.getWeekTasksWithPositions(weekStart);
        
        // Build rows for each hour (full 24 hours)
        for (let hour = 0; hour < 24; hour++) {
            const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour);
            const ampm = hour < 12 ? 'AM' : 'PM';
            
            html += `<tr><td><span>${displayHour} ${ampm}</span></td>`;
            
            for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
                const cellDate = new Date(weekStart);
                cellDate.setDate(cellDate.getDate() + dayIndex);
                const dateStr = this.formatDateString(cellDate);
                const isToday = dayIndex === todayColIndex;
                
                // Find tasks that START at this hour
                const cellTasks = weekTasks.filter(t => 
                    t.dateStr === dateStr && t.startHour === hour
                );
                
                html += `<td class="${isToday ? 'today-col' : ''}" data-date="${dateStr}" data-hour="${hour}">`;
                cellTasks.forEach(task => {
                    const heightPx = task.duration * 24; // 24px per hour
                    const categoryClass = task.categoryColor !== null && task.categoryColor !== undefined ? `category-color-${task.categoryColor}` : '';
                    html += `<div class="task-event ${categoryClass} ${task.isCompleted ? 'completed' : ''}" data-id="${task.id}" style="height: ${heightPx}px;">${this.escapeHtml(task.title)}</div>`;
                });
                html += '</td>';
            }
            
            html += '</tr>';
        }
        
        html += '</tbody></table>';
        weekSchedule.innerHTML = html;
        this.bindCalendarEvents();
    }
    
    getWeekTasksWithPositions(weekStart) {
        const result = [];
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + 7);
        
        this.tasks.forEach(task => {
            const taskDate = task.startDate || task.dueDate;
            if (!taskDate) return;
            
            const [year, month, day] = taskDate.split('-').map(Number);
            const date = new Date(year, month - 1, day);
            
            if (date >= weekStart && date < weekEnd) {
                let startHour = 9; // Default
                let endHour = 10; // Default 1 hour
                
                if (task.startTime) {
                    startHour = parseInt(task.startTime.split(':')[0], 10);
                }
                if (task.dueTime) {
                    endHour = parseInt(task.dueTime.split(':')[0], 10);
                } else {
                    endHour = startHour + 1;
                }
                
                const duration = Math.max(1, endHour - startHour);
                
                result.push({
                    ...task,
                    dateStr: taskDate,
                    startHour,
                    endHour,
                    duration
                });
            }
        });
        
        return result;
    }
    
    formatDateString(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    getTasksForHour(date, hour) {
        const dateStr = this.formatDateString(date);
        return this.tasks.filter(task => {
            if (!task.startDate && !task.dueDate) return false;
            const taskDate = task.startDate || task.dueDate;
            if (taskDate !== dateStr) return false;
            
            // Check if task starts at this hour
            if (task.startTime) {
                const taskHour = parseInt(task.startTime.split(':')[0], 10);
                return taskHour === hour;
            }
            // If no time, show at 9 AM by default
            return hour === 9;
        });
    }
    
    renderMonthView() {
        if (!this.monthGrid) return;
        if (this.emptyState) this.emptyState.classList.remove('show');
        
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        
        // First day of month
        const firstDay = new Date(year, month, 1);
        const startDay = firstDay.getDay(); // 0 = Sunday
        
        // Last day of month
        const lastDay = new Date(year, month + 1, 0);
        const totalDays = lastDay.getDate();
        
        // Previous month days to show
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        
        let html = '';
        let dayCount = 1;
        let nextMonthDay = 1;
        
        // Calculate total cells needed (6 rows max)
        const totalCells = Math.ceil((startDay + totalDays) / 7) * 7;
        
        for (let i = 0; i < totalCells; i++) {
            let dayNum, dateStr, isOtherMonth = false, cellDate;
            
            if (i < startDay) {
                // Previous month
                dayNum = prevMonthLastDay - startDay + i + 1;
                cellDate = new Date(year, month - 1, dayNum);
                isOtherMonth = true;
            } else if (dayCount > totalDays) {
                // Next month
                dayNum = nextMonthDay++;
                cellDate = new Date(year, month + 1, dayNum);
                isOtherMonth = true;
            } else {
                // Current month
                dayNum = dayCount++;
                cellDate = new Date(year, month, dayNum);
            }
            
            dateStr = cellDate.toISOString().split('T')[0];
            const isToday = this.isSameDay(cellDate, new Date());
            
            // Get tasks for this day
            const dayTasks = this.getTasksForDate(cellDate);
            const maxShow = 2;
            const moreTasks = dayTasks.length > maxShow ? dayTasks.length - maxShow : 0;
            
            html += `
                <div class="month-day ${isToday ? 'today' : ''} ${isOtherMonth ? 'other-month' : ''}" data-date="${dateStr}">
                    <div class="month-day-number">${dayNum}</div>
                    <div class="month-day-tasks">
                        ${dayTasks.slice(0, maxShow).map(task => {
                            const categoryClass = task.categoryColor !== null && task.categoryColor !== undefined ? `category-color-${task.categoryColor}` : '';
                            return `<div class="task-tag ${categoryClass} ${task.isCompleted ? 'completed' : ''}" data-id="${task.id}">
                                ${this.escapeHtml(task.title)}
                            </div>`;
                        }).join('')}
                        ${moreTasks > 0 ? `<div class="month-day-more">+${moreTasks} more</div>` : ''}
                    </div>
                </div>
            `;
        }
        
        this.monthGrid.innerHTML = html;
        this.bindCalendarEvents();
    }
    
    getTasksForDate(date) {
        const dateStr = date.toISOString().split('T')[0];
        let tasks = this.tasks.filter(t => t.dueDate === dateStr);
        
        // Apply current filter
        if (this.currentFilter === 'active') {
            tasks = tasks.filter(t => !t.isCompleted);
        } else if (this.currentFilter === 'completed') {
            tasks = tasks.filter(t => t.isCompleted);
        }
        
        // Apply search
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            tasks = tasks.filter(t => 
                t.title.toLowerCase().includes(query) ||
                t.description.toLowerCase().includes(query)
            );
        }
        
        return tasks;
    }
    
    bindCalendarEvents() {
        // Click on day cell to switch to day view for that day
        document.querySelectorAll('.week-day, .month-day').forEach(cell => {
            cell.addEventListener('click', (e) => {
                if (e.target.classList.contains('task-tag')) return;
                const date = cell.dataset.date;
                this.currentDate = new Date(date);
                this.currentView = 'day';
                this.viewOptions.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.view === 'day');
                });
                this.render();
            });
        });
        
        // Click on task tag to open it
        document.querySelectorAll('.task-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openModal(tag.dataset.id);
            });
        });
    }
    
    updateEmptyState() {
        if (!this.emptyState) return;
        const icon = this.emptyState.querySelector('i');
        const title = this.emptyState.querySelector('h3');
        const message = this.emptyState.querySelector('p');
        
        if (this.searchQuery) {
            icon.className = 'fas fa-search';
            title.textContent = 'No Results';
            message.textContent = 'Try a different search term';
        } else if (this.currentFilter === 'active') {
            icon.className = 'fas fa-check-circle';
            title.textContent = 'No Active Tasks';
            message.textContent = 'All caught up! 🎉';
        } else if (this.currentFilter === 'completed') {
            icon.className = 'fas fa-clipboard-check';
            title.textContent = 'No Completed Tasks';
            message.textContent = 'Complete some tasks to see them here';
        } else {
            icon.className = 'fas fa-clipboard-list';
            title.textContent = 'No Tasks';
            message.textContent = 'Tap + to add a task for this period';
        }
    }
    
    renderTask(task) {
        const timeDisplay = this.formatTimeRange(task.startTime, task.dueTime);
        const categoryClass = task.categoryColor !== null && task.categoryColor !== undefined ? `category-color-${task.categoryColor}` : '';
        const hasBanner = task.categoryColor !== null && task.categoryColor !== undefined;
        return `
            <div class="task-item ${task.isCompleted ? 'completed' : ''} ${categoryClass}" data-id="${task.id}">
                ${hasBanner ? `<div class="task-banner"><span class="banner-title">${this.escapeHtml(task.title)}</span></div>` : ''}
                <div class="task-body">
                    <div class="task-checkbox ${task.isCompleted ? 'checked' : ''}" data-id="${task.id}">
                        ${task.isCompleted ? '<i class="fas fa-check"></i>' : ''}
                    </div>
                    <div class="task-content">
                        ${!hasBanner ? `<div class="task-header"><span class="task-title">${this.escapeHtml(task.title)}</span></div>` : ''}
                        ${task.description ? `<p class="task-description">${this.escapeHtml(task.description)}</p>` : ''}
                        ${timeDisplay ? `
                            <div class="task-meta">
                                <i class="fas fa-clock"></i>
                                <span>${timeDisplay}</span>
                            </div>
                        ` : ''}
                    </div>
                    <div class="task-right">
                        <span class="priority-badge ${task.priority}">${task.priority}</span>
                        <div class="task-actions">
                            <button class="task-btn edit-btn" data-id="${task.id}">Edit</button>
                            <button class="task-btn delete-btn" data-id="${task.id}">Delete</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatTimeRange(startTime, endTime) {
        if (!startTime && !endTime) return '';
        
        const formatTime = (timeStr) => {
            if (!timeStr) return '';
            const [hours, minutes] = timeStr.split(':').map(Number);
            const displayHour = hours === 0 ? 12 : (hours > 12 ? hours - 12 : hours);
            const ampm = hours < 12 ? 'AM' : 'PM';
            return `${displayHour}:${minutes.toString().padStart(2, '0')} ${ampm}`;
        };
        
        const start = formatTime(startTime);
        const end = formatTime(endTime);
        
        if (start && end) {
            return `${start} - ${end}`;
        } else if (start) {
            return start;
        } else if (end) {
            return `Ends ${end}`;
        }
        return '';
    }
    
    formatDueDate(dateString, timeString) {
        if (!dateString) return { text: '', class: '' };
        
        // Parse date as local time (not UTC)
        const [year, month, day] = dateString.split('-').map(Number);
        const date = new Date(year, month - 1, day);
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const taskDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
        
        let text, className = '';
        
        if (taskDate.getTime() === today.getTime()) {
            text = 'Today';
            className = 'today';
        } else if (taskDate.getTime() === tomorrow.getTime()) {
            text = 'Tomorrow';
        } else if (taskDate < today) {
            text = this.formatDate(date);
            className = 'overdue';
        } else {
            text = this.formatDate(date);
        }
        
        // Append time if provided
        if (timeString) {
            const [hours, minutes] = timeString.split(':').map(Number);
            const displayHour = hours === 0 ? 12 : (hours > 12 ? hours - 12 : hours);
            const ampm = hours < 12 ? 'AM' : 'PM';
            text += ` at ${displayHour}:${minutes.toString().padStart(2, '0')} ${ampm}`;
        }
        
        return { text, class: className };
    }
    
    formatDate(date) {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    bindTaskEvents() {
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleComplete(checkbox.dataset.id);
            });
        });
        
        document.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't open modal if clicking on buttons
                if (e.target.closest('.task-btn')) return;
                this.openModal(item.dataset.id);
            });
        });
        
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openModal(btn.dataset.id);
            });
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm('Are you sure you want to delete this task?')) {
                    this.deleteTask(btn.dataset.id);
                }
            });
        });
    }
    
    toggleComplete(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.isCompleted = !task.isCompleted;
            this.saveTasks();
            this.render();
        }
    }
    
    openModal(taskId = null) {
        this.editingTaskId = taskId;
        
        if (taskId) {
            const task = this.tasks.find(t => t.id === taskId);
            if (task) {
                this.modalTitle.textContent = 'Edit Task';
                this.taskIdInput.value = task.id;
                this.taskTitleInput.value = task.title;
                this.taskDescriptionInput.value = task.description;
                
                // Parse start date and time
                if (task.startDate) {
                    const startDateObj = new Date(task.startDate);
                    this.taskStartDateInput.value = startDateObj.toISOString().split('T')[0];
                    this.updateTimeOptions('start');
                    if (task.startTime) {
                        this.taskStartTimeInput.value = task.startTime;
                    }
                } else {
                    this.taskStartDateInput.value = '';
                    this.updateTimeOptions('start');
                }
                
                // Parse due date and time
                if (task.dueDate) {
                    const dateObj = new Date(task.dueDate);
                    this.taskDueDateInput.value = dateObj.toISOString().split('T')[0];
                    this.updateTimeOptions('due');
                    if (task.dueTime) {
                        this.taskDueTimeInput.value = task.dueTime;
                    }
                } else {
                    this.taskDueDateInput.value = '';
                    this.updateTimeOptions('due');
                }
                
                this.priorityBtns.forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.priority === task.priority);
                });
                
                // Set category (single select)
                document.querySelectorAll('.category-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.category === task.categoryId);
                });
                
                this.deleteTaskBtn.style.display = 'block';
            }
        } else {
            this.modalTitle.textContent = 'New Task';
            this.taskForm.reset();
            this.taskIdInput.value = '';
            
            // Set default dates based on current view
            const defaultDate = new Date(this.currentDate);
            const defaultDateStr = defaultDate.toISOString().split('T')[0];
            this.taskStartDateInput.value = defaultDateStr;
            this.taskDueDateInput.value = defaultDateStr;
            
            // Populate time options for both
            this.updateTimeOptions('start');
            this.updateTimeOptions('due');
            
            this.priorityBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.priority === 'medium');
            });
            
            // Clear category selection
            document.querySelectorAll('.category-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Hide new category input
            if (this.newCategoryInput) {
                this.newCategoryInput.classList.remove('show');
                this.newCategoryName.value = '';
            }
            
            this.deleteTaskBtn.style.display = 'none';
        }
        
        // Also hide new category input when editing
        if (this.newCategoryInput) {
            this.newCategoryInput.classList.remove('show');
        }
        
        this.taskModal.classList.add('show');
        this.taskTitleInput.focus();
    }
    
    renderCategories() {
        if (!this.categorySelector) return;
        
        // Clear existing category buttons (except Add button)
        const existingBtns = this.categorySelector.querySelectorAll('.category-btn');
        existingBtns.forEach(btn => btn.remove());
        
        // Add category buttons from saved categories
        this.categories.forEach(cat => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `category-btn color-${cat.color}`;
            btn.dataset.category = cat.id;
            btn.dataset.color = cat.color;
            btn.textContent = cat.name;
            btn.addEventListener('click', () => {
                // Single select - remove active from all others
                this.categorySelector.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
            
            // Insert before the Add button
            this.categorySelector.insertBefore(btn, this.addCategoryBtn);
        });
    }
    
    addNewCategory(name, colorIndex) {
        const id = Date.now().toString(36);
        const newCategory = {
            id: id,
            name: name,
            color: colorIndex
        };
        
        this.categories.push(newCategory);
        this.saveCategories();
        this.renderCategories();
        
        // Auto-select the new category
        const newBtn = this.categorySelector.querySelector(`[data-category="${id}"]`);
        if (newBtn) {
            this.categorySelector.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            newBtn.classList.add('active');
        }
    }
    
    // Update time dropdown based on selected date
    updateTimeOptions(type = 'due') {
        const dateInput = type === 'start' ? this.taskStartDateInput : this.taskDueDateInput;
        const timeInput = type === 'start' ? this.taskStartTimeInput : this.taskDueTimeInput;
        
        if (!timeInput || !dateInput) return;
        
        const selectedDate = dateInput.value;
        timeInput.innerHTML = '<option value="">No time</option>';
        
        if (!selectedDate) {
            timeInput.disabled = true;
            return;
        }
        
        timeInput.disabled = false;
        
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const todayStr = `${year}-${month}-${day}`;
        const isToday = selectedDate === todayStr;
        
        let startHour = 0;
        let startMinute = 0;
        
        if (isToday) {
            // Round current time up to nearest 30 minutes
            const currentHour = today.getHours();
            const currentMinute = today.getMinutes();
            
            if (currentMinute === 0) {
                startHour = currentHour;
                startMinute = 0;
            } else if (currentMinute <= 30) {
                startHour = currentHour;
                startMinute = 30;
            } else {
                startHour = currentHour + 1;
                startMinute = 0;
            }
            
            // If we've passed 23:30, no times available today
            if (startHour >= 24) {
                timeInput.innerHTML = '<option value="">No times available</option>';
                return;
            }
        }
        
        // Generate time options in 30-minute intervals
        for (let hour = startHour; hour < 24; hour++) {
            for (let minute = (hour === startHour ? startMinute : 0); minute < 60; minute += 30) {
                const hourStr = hour.toString().padStart(2, '0');
                const minStr = minute.toString().padStart(2, '0');
                const value = `${hourStr}:${minStr}`;
                
                // Format display time (12-hour format)
                const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour);
                const ampm = hour < 12 ? 'AM' : 'PM';
                const displayTime = `${displayHour}:${minStr} ${ampm}`;
                
                const option = document.createElement('option');
                option.value = value;
                option.textContent = displayTime;
                timeInput.appendChild(option);
            }
        }
    }
    
    closeModal() {
        if (this.taskModal) this.taskModal.classList.remove('show');
        this.editingTaskId = null;
    }
    
    saveTask() {
        const title = this.taskTitleInput.value.trim();
        if (!title) return;
        
        const description = this.taskDescriptionInput.value.trim();
        const startDate = this.taskStartDateInput.value;
        const startTime = this.taskStartTimeInput ? this.taskStartTimeInput.value : '';
        const dueDate = this.taskDueDateInput.value;
        const dueTime = this.taskDueTimeInput ? this.taskDueTimeInput.value : '';
        const priority = document.querySelector('.priority-btn.active').dataset.priority;
        
        // Get selected category (single select)
        const activeCategory = document.querySelector('#categorySelector .category-btn.active');
        const categoryId = activeCategory ? activeCategory.dataset.category : null;
        const categoryColor = activeCategory ? activeCategory.dataset.color : null;
        
        console.log('Saving category:', categoryId, 'Color:', categoryColor);
        
        if (this.editingTaskId) {
            const task = this.tasks.find(t => t.id === this.editingTaskId);
            if (task) {
                task.title = title;
                task.description = description;
                task.startDate = startDate;
                task.startTime = startTime;
                task.dueDate = dueDate;
                task.dueTime = dueTime;
                task.priority = priority;
                task.categoryId = categoryId;
                task.categoryColor = categoryColor;
            }
        } else {
            this.tasks.push({
                id: Date.now().toString(36) + Math.random().toString(36).substr(2),
                title,
                description,
                startDate,
                startTime,
                dueDate,
                dueTime,
                priority,
                categoryId,
                categoryColor,
                isCompleted: false,
                createdAt: new Date().toISOString()
            });
        }
        
        this.saveTasks();
        this.closeModal();
        this.render();
    }
    
    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.saveTasks();
        this.render();
    }
    
    clearCompleted() {
        this.tasks = this.tasks.filter(t => !t.isCompleted);
        this.saveTasks();
        this.render();
        if (this.dropdownMenu) this.dropdownMenu.classList.remove('show');
    }
    
    openDeleteModal() {
        if (this.deleteModal) this.deleteModal.classList.add('show');
    }
    
    closeDeleteModal() {
        if (this.deleteModal) this.deleteModal.classList.remove('show');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TaskManager();

    // Profile icon logic
    const profileIcon = document.getElementById('profileIcon');
    if (profileIcon) {
        let user = null;
        try {
            user = JSON.parse(localStorage.getItem('currentUser'));
        } catch {}
        if (user) {
            // Use name if available, else email
            const displayName = user.name || user.email || '';
            const initial = displayName.charAt(0).toUpperCase();
            profileIcon.textContent = initial;
            profileIcon.title = displayName;
        } else {
            profileIcon.textContent = '?';
            profileIcon.title = 'Profile';
        }
    }
});
