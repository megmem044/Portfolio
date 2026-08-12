// Pure task filtering, sorting, date-key, and calendar-layout helpers.
import type { CalendarView, Filter, Task } from './types';

export function dateToKey(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function parseDate(dateKey: string) {
  const [year, month, day] = dateKey.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function isSameDay(firstDate: Date, secondDate: Date) {
  return firstDate.getFullYear() === secondDate.getFullYear()
    && firstDate.getMonth() === secondDate.getMonth()
    && firstDate.getDate() === secondDate.getDate();
}

export function getWeekStart(date: Date) {
  const result = new Date(date);
  result.setDate(result.getDate() - result.getDay());
  result.setHours(0, 0, 0, 0);
  return result;
}

export function isTaskInView(task: Task, date: Date, view: CalendarView) {
  if (!task.dueDate) return false;
  const taskDate = parseDate(task.dueDate);
  if (view === 'day') return isSameDay(taskDate, date);
  if (view === 'week') {
    const weekStart = getWeekStart(date);
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 7);
    return taskDate >= weekStart && taskDate < weekEnd;
  }
  return taskDate.getFullYear() === date.getFullYear() && taskDate.getMonth() === date.getMonth();
}

export function matchesTask(task: Task, filter: Filter, searchQuery: string) {
  if (filter === 'active' && task.isCompleted) return false;
  if (filter === 'completed' && !task.isCompleted) return false;
  const query = searchQuery.trim().toLowerCase();
  return !query || task.title.toLowerCase().includes(query) || task.description.toLowerCase().includes(query);
}

export function sortTasks(tasks: Task[]) {
  const priorityOrder = { high: 3, medium: 2, low: 1 };
  return [...tasks].sort((firstTask, secondTask) => {
    if (firstTask.isCompleted !== secondTask.isCompleted) return firstTask.isCompleted ? 1 : -1;
    if (firstTask.dueDate !== secondTask.dueDate) return firstTask.dueDate.localeCompare(secondTask.dueDate);
    return priorityOrder[secondTask.priority] - priorityOrder[firstTask.priority];
  });
}

export function formatTimeRange(startTime: string, dueTime: string) {
  const formatTime = (time: string) => {
    if (!time) return '';
    const [hours, minutes] = time.split(':').map(Number);
    return `${hours % 12 || 12}:${String(minutes).padStart(2, '0')} ${hours < 12 ? 'AM' : 'PM'}`;
  };
  const start = formatTime(startTime);
  const due = formatTime(dueTime);
  return start && due ? `${start} - ${due}` : start || (due ? `Ends ${due}` : '');
}

export function calendarLabel(date: Date, view: CalendarView) {
  const today = new Date();
  if (view === 'day') {
    if (isSameDay(date, today)) return 'Today';
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (isSameDay(date, tomorrow)) return 'Tomorrow';
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (isSameDay(date, yesterday)) return 'Yesterday';
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  }
  if (view === 'week') {
    const start = getWeekStart(date);
    const end = new Date(start);
    end.setDate(end.getDate() + 6);
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  }
  return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
}
