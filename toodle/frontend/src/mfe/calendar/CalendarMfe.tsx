// Calendar feature boundary: owns period navigation and day/week/month projections.
import { useState } from 'react';
import { calendarLabel, isTaskInView, matchesTask, sortTasks } from '../../features/tasks/taskUtils';
import type { CalendarView, Filter, Task } from '../../features/tasks/types';
import { DayView } from '../../views/DayView';
import { MonthView } from '../../views/MonthView';
import { WeekView } from '../../views/WeekView';

interface CalendarMfeProps {
  tasks: Task[];
  currentDate: Date;
  view: CalendarView;
  onViewChange: (view: CalendarView) => void;
  onDateChange: (date: Date) => void;
  onEditTask: (task: Task) => void;
  onCreateTask: (date: string, time?: string) => void;
  filter: Filter;
  searchQuery: string;
  onToggleComplete: (taskId: string) => void;
  onDeleteTask: (taskId: string) => void;
}

export function CalendarMfe({ tasks, currentDate, view, onViewChange, onDateChange, onEditTask, onCreateTask, filter, searchQuery, onToggleComplete, onDeleteTask }: CalendarMfeProps) {
  const navigate = (direction: number) => {
    // Use calendar arithmetic rather than millisecond offsets so DST transitions remain correct.
    const nextDate = new Date(currentDate);
    if (view === 'day') nextDate.setDate(nextDate.getDate() + direction);
    if (view === 'week') nextDate.setDate(nextDate.getDate() + direction * 7);
    if (view === 'month') nextDate.setMonth(nextDate.getMonth() + direction);
    onDateChange(nextDate);
  };
  const calendarTasks = sortTasks(tasks.filter((task) => isTaskInView(task, currentDate, view) && matchesTask(task, 'all', '')));

  return <>
    <section className="date-navigation"><button className="nav-btn" type="button" aria-label="Previous period" onClick={() => navigate(-1)}><i className="fas fa-chevron-left" /></button><h2 className="current-date">{calendarLabel(currentDate, view)}</h2><button className="nav-btn" type="button" aria-label="Next period" onClick={() => navigate(1)}><i className="fas fa-chevron-right" /></button></section>
    {view === 'day' && <DayView tasks={calendarTasks} filter={filter} searchQuery={searchQuery} onToggleComplete={onToggleComplete} onEdit={onEditTask} onDelete={onDeleteTask} />}
    {view === 'week' && <WeekView date={currentDate} tasks={calendarTasks} onSelectTask={onEditTask} onCreateAt={onCreateTask} />}
    {view === 'month' && <MonthView date={currentDate} tasks={calendarTasks} onSelectTask={onEditTask} onSelectDate={(date) => { onDateChange(date); onViewChange('day'); }} />}
  </>;
}

interface CalendarViewSwitcherProps {
  view: CalendarView;
  onViewChange: (view: CalendarView) => void;
}

export function CalendarViewSwitcher({ view, onViewChange }: CalendarViewSwitcherProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const selectView = (nextView: CalendarView) => { onViewChange(nextView); setIsMenuOpen(false); };
  return <div className="view-dropdown-container">
    <button className="header-btn" type="button" onClick={() => setIsMenuOpen((open) => !open)}>View</button>
    <div className={`dropdown-menu ${isMenuOpen ? 'show' : ''}`}><div className="dropdown-section">{(['day', 'week', 'month'] as CalendarView[]).map((option) => <button key={option} className={`view-option ${view === option ? 'active' : ''}`} type="button" onClick={() => selectView(option)}><i className={`fas fa-calendar-${option === 'day' ? 'day' : option === 'week' ? 'week' : 'alt'}`} /> {option[0].toUpperCase() + option.slice(1)}</button>)}</div></div>
  </div>;
}
