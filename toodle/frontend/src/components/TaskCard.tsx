// Reusable task summary card with completion, edit, and delete actions.
import { formatTimeRange } from '../features/tasks/taskUtils';
import type { Task } from '../features/tasks/types';

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export function TaskCard({ task, onToggleComplete, onEdit, onDelete }: TaskCardProps) {
  const categoryClass = task.categoryColor === null ? '' : `category-color-${task.categoryColor}`;
  const hasBanner = task.categoryColor !== null;
  const timeRange = formatTimeRange(task.startTime, task.dueTime);
  return <article className={`task-item ${task.isCompleted ? 'completed' : ''} ${categoryClass}`} onClick={() => onEdit(task)}>
    {hasBanner && <div className="task-banner"><span className="banner-title">{task.title}</span></div>}
    <div className="task-body">
      <button className={`task-checkbox ${task.isCompleted ? 'checked' : ''}`} aria-label={`Mark ${task.title} ${task.isCompleted ? 'active' : 'complete'}`} onClick={(event) => { event.stopPropagation(); onToggleComplete(task.id); }}>
        {task.isCompleted && <i className="fas fa-check" />}
      </button>
      <div className="task-content">
        {!hasBanner && <div className="task-header"><span className="task-title">{task.title}</span></div>}
        {task.description && <p className="task-description">{task.description}</p>}
        {timeRange && <div className="task-meta"><i className="fas fa-clock" /><span>{timeRange}</span></div>}
      </div>
      <div className="task-right">
        <span className={`priority-badge ${task.priority}`}>{task.priority}</span>
        <div className="task-actions">
          <button className="task-btn edit-btn" onClick={(event) => { event.stopPropagation(); onEdit(task); }}>Edit</button>
          <button className="task-btn delete-btn" onClick={(event) => { event.stopPropagation(); onDelete(task.id); }}>Delete</button>
        </div>
      </div>
    </div>
  </article>;
}
