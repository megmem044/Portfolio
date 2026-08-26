// Projects tasks into the seven-day calendar grid.
import { useMemo } from 'react';
import { dateToKey, getWeekStart, isSameDay } from '../features/tasks/taskUtils';
import type { Task } from '../features/tasks/types';

interface WeekViewProps {
  date: Date;
  tasks: Task[];
  onSelectTask: (task: Task) => void;
  onCreateAt: (date: string, time: string) => void;
}

export function WeekView({ date, tasks, onSelectTask, onCreateAt }: WeekViewProps) {
  const weekStart = getWeekStart(date);
  const days = Array.from({ length: 7 }, (_, index) => { const value = new Date(weekStart); value.setDate(value.getDate() + index); return value; });
  const hours = Array.from({ length: 24 }, (_, index) => index);
  // Index once per task-list change instead of scanning every task for all 168 cells.
  const tasksBySlot = useMemo(() => {
    const index = new Map<string, Task[]>();
    for (const task of tasks) {
      const taskDate = task.startDate || task.dueDate;
      if (!taskDate) continue;
      const hour = Number((task.startTime || '09:00').slice(0, 2));
      const key = `${taskDate}:${hour}`;
      index.set(key, [...(index.get(key) ?? []), task]);
    }
    return index;
  }, [tasks]);
  return <section className="week-view"><div className="week-schedule"><table><thead><tr><th /><>{days.map((day) => <th className={isSameDay(day, new Date()) ? 'today' : ''} key={dateToKey(day)}><span className="day-name">{day.toLocaleDateString('en-US', { weekday: 'long' })}</span><span className="date-num">{day.getDate()}</span></th>)}</></tr></thead><tbody>{hours.map((hour) => <tr key={hour}><td><span>{hour % 12 || 12} {hour < 12 ? 'AM' : 'PM'}</span></td>{days.map((day) => {
    const dateKey = dateToKey(day);
    const startingTasks = tasksBySlot.get(`${dateKey}:${hour}`) ?? [];
    return <td key={dateKey} className={isSameDay(day, new Date()) ? 'today-col' : ''} onClick={() => onCreateAt(dateKey, `${String(hour).padStart(2, '0')}:00`)}>{startingTasks.map((task) => <button type="button" key={task.id} className={`task-event ${task.categoryColor === null ? '' : `category-color-${task.categoryColor}`} ${task.isCompleted ? 'completed' : ''}`} onClick={(event) => { event.stopPropagation(); onSelectTask(task); }}>{task.title}</button>)}</td>;
  })}</tr>)}</tbody></table></div></section>;
}
