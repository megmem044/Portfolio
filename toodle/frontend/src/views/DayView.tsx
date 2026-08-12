import { TaskCard } from '../components/TaskCard';
import type { Filter, Task } from '../features/tasks/types';

interface DayViewProps {
  tasks: Task[];
  filter: Filter;
  searchQuery: string;
  onToggleComplete: (taskId: string) => void;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export function DayView({ tasks, filter, searchQuery, onToggleComplete, onEdit, onDelete }: DayViewProps) {
  const emptyCopy = searchQuery ? ['fas fa-search', 'No Results', 'Try a different search term'] : filter === 'active' ? ['fas fa-check-circle', 'No Active Tasks', 'All caught up!'] : filter === 'completed' ? ['fas fa-clipboard-check', 'No Completed Tasks', 'Complete some tasks to see them here'] : ['fas fa-clipboard-list', 'No Tasks', 'Tap + to add a task for this day'];
  return <section className="day-view">
    {tasks.length ? <div className="task-list">{tasks.map((task) => <TaskCard key={task.id} task={task} onToggleComplete={onToggleComplete} onEdit={onEdit} onDelete={onDelete} />)}</div> : <div className="empty-state show"><i className={emptyCopy[0]} /><h3>{emptyCopy[1]}</h3><p>{emptyCopy[2]}</p></div>}
  </section>;
}