// Projects tasks into a selectable month grid.
import { useMemo } from 'react';
import { dateToKey, isSameDay } from '../features/tasks/taskUtils';
import type { Task } from '../features/tasks/types';

interface MonthViewProps {
  date: Date;
  tasks: Task[];
  onSelectDate: (date: Date) => void;
  onSelectTask: (task: Task) => void;
}

export function MonthView({ date, tasks, onSelectDate, onSelectTask }: MonthViewProps) {
  const firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
  const lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
  const totalCells = Math.ceil((firstDay.getDay() + lastDay.getDate()) / 7) * 7;
  const dates = Array.from({ length: totalCells }, (_, index) => new Date(date.getFullYear(), date.getMonth(), index - firstDay.getDay() + 1));
  // A date index turns the month projection from cells × tasks into cells + tasks.
  const tasksByDate = useMemo(() => {
    const index = new Map<string, Task[]>();
    for (const task of tasks) {
      if (!task.dueDate) continue;
      index.set(task.dueDate, [...(index.get(task.dueDate) ?? []), task]);
    }
    return index;
  }, [tasks]);
  return <section className="month-view"><div className="month-header">{['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => <div className="month-day-header" key={day}>{day}</div>)}</div><div className="month-grid">{dates.map((day) => {
    const dayTasks = tasksByDate.get(dateToKey(day)) ?? [];
    return <button type="button" className={`month-day ${isSameDay(day, new Date()) ? 'today' : ''} ${day.getMonth() !== date.getMonth() ? 'other-month' : ''}`} key={dateToKey(day)} onClick={() => onSelectDate(day)}><div className="month-day-number">{day.getDate()}</div><div className="month-day-tasks">{dayTasks.slice(0, 2).map((task) => <span role="button" tabIndex={0} key={task.id} className={`task-tag ${task.categoryColor === null ? '' : `category-color-${task.categoryColor}`} ${task.isCompleted ? 'completed' : ''}`} onClick={(event) => { event.stopPropagation(); onSelectTask(task); }}>{task.title}</span>)}{dayTasks.length > 2 && <div className="month-day-more">+{dayTasks.length - 2} more</div>}</div></button>;
  })}</div></section>;
}
