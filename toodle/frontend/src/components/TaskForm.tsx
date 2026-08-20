// Controlled create/edit dialog that converts form state into a typed task draft.
import { useEffect, useRef, useState } from 'react';
import { CategoryPicker } from './CategoryPicker';
import type { Category, Priority, Task, TaskDraft } from '../features/tasks/types';

interface TaskFormProps {
  task?: Task;
  defaultDate: string;
  defaultStartTime?: string;
  categories: Category[];
  onCreateCategory: (name: string, color: string) => Promise<Category>;
  onSave: (draft: TaskDraft) => void;
  onDelete?: () => void;
  onClose: () => void;
}

function draftFor(task: Task | undefined, defaultDate: string, defaultStartTime = ''): TaskDraft {
  return task ? {
    title: task.title, description: task.description, startDate: task.startDate, startTime: task.startTime,
    dueDate: task.dueDate, dueTime: task.dueTime, priority: task.priority, categoryId: task.categoryId,
  } : { title: '', description: '', startDate: defaultDate, startTime: defaultStartTime, dueDate: defaultDate, dueTime: '', priority: 'medium', categoryId: null };
}

function timeOptions() {
  const options = [''];
  for (let hour = 0; hour < 24; hour += 1) for (const minute of [0, 30]) options.push(`${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`);
  return options;
}

function displayTime(time: string) {
  if (!time) return 'No time';
  const [hours, minutes] = time.split(':').map(Number);
  return `${hours % 12 || 12}:${String(minutes).padStart(2, '0')} ${hours < 12 ? 'AM' : 'PM'}`;
}

export function TaskForm({ task, defaultDate, defaultStartTime, categories, onCreateCategory, onSave, onDelete, onClose }: TaskFormProps) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const [draft, setDraft] = useState(() => draftFor(task, defaultDate, defaultStartTime));
  useEffect(() => setDraft(draftFor(task, defaultDate, defaultStartTime)), [task, defaultDate, defaultStartTime]);
  useEffect(() => {
    const keepFocusInDialog = (event: KeyboardEvent) => {
      if (event.key !== 'Tab' || !dialogRef.current) return;
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex="-1"])'));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', keepFocusInDialog);
    return () => document.removeEventListener('keydown', keepFocusInDialog);
  }, []);
  const update = <Key extends keyof TaskDraft>(key: Key, value: TaskDraft[Key]) => setDraft((currentDraft) => ({ ...currentDraft, [key]: value }));
  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (draft.title.trim()) onSave({ ...draft, title: draft.title.trim(), description: draft.description.trim() });
  };
  const closeOnBackdrop = (event: React.MouseEvent<HTMLDivElement>) => { if (event.target === event.currentTarget) onClose(); };
  return <div className="modal-overlay show" onMouseDown={closeOnBackdrop} role="presentation">
    <div ref={dialogRef} className="modal" role="dialog" aria-modal="true" aria-labelledby="task-form-title">
      <div className="modal-header"><h2 id="task-form-title">{task ? 'Edit Task' : 'New Task'}</h2><button className="close-btn" type="button" aria-label="Close" onClick={onClose}>x</button></div>
      <div className="modal-content"><form onSubmit={submit}>
        <div className="form-group"><label htmlFor="task-title">Title</label><input id="task-title" value={draft.title} onChange={(event) => update('title', event.target.value)} placeholder="Task title" required autoFocus /></div>
        <div className="form-group"><label htmlFor="task-description">Description</label><textarea id="task-description" value={draft.description} onChange={(event) => update('description', event.target.value)} placeholder="Add more details (optional)" rows={3} /></div>
        <div className="form-row">
          <div className="form-group form-group-half"><label htmlFor="task-start-date">Start Date</label><input id="task-start-date" type="date" value={draft.startDate} onChange={(event) => update('startDate', event.target.value)} /></div>
          <div className="form-group form-group-half"><label htmlFor="task-start-time">Time</label><select id="task-start-time" className="time-select" value={draft.startTime} disabled={!draft.startDate} onChange={(event) => update('startTime', event.target.value)}>{timeOptions().map((time) => <option key={time || 'none'} value={time}>{displayTime(time)}</option>)}</select></div>
        </div>
        <div className="form-row">
          <div className="form-group form-group-half"><label htmlFor="task-due-date">Due Date</label><input id="task-due-date" type="date" value={draft.dueDate} onChange={(event) => update('dueDate', event.target.value)} /></div>
          <div className="form-group form-group-half"><label htmlFor="task-due-time">Time</label><select id="task-due-time" className="time-select" value={draft.dueTime} disabled={!draft.dueDate} onChange={(event) => update('dueTime', event.target.value)}>{timeOptions().map((time) => <option key={time || 'none'} value={time}>{displayTime(time)}</option>)}</select></div>
        </div>
        <fieldset className="form-group form-fieldset"><legend>Priority</legend><div className="priority-selector">{(['low', 'medium', 'high'] as Priority[]).map((priority) => <button key={priority} type="button" aria-pressed={draft.priority === priority} className={`priority-btn ${draft.priority === priority ? 'active' : ''}`} data-priority={priority} onClick={() => update('priority', priority)}>{priority[0].toUpperCase() + priority.slice(1)}</button>)}</div></fieldset>
        <fieldset className="form-group form-fieldset"><legend>Category</legend><CategoryPicker categories={categories} selectedCategoryId={draft.categoryId} onSelect={(categoryId) => update('categoryId', categoryId)} onCreate={onCreateCategory} /></fieldset>
        <div className="form-actions"><button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button><button type="submit" className="btn btn-primary">Save</button></div>
        {task && <button type="button" className="btn btn-danger" onClick={onDelete}><i className="fas fa-trash" /> Delete Task</button>}
      </form></div>
    </div>
  </div>;
}
