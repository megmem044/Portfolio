// Tasks feature boundary: owns task statistics, status filtering, and search controls.
import { StatsPanel } from '../../components/StatsPanel';
import type { Filter, Task } from '../../features/tasks/types';

interface TasksMfeProps {
  tasks: Task[];
  filter: Filter;
  searchQuery: string;
  onFilterChange: (filter: Filter) => void;
  onSearchQueryChange: (query: string) => void;
}

export function TasksMfe({ tasks, filter, searchQuery, onFilterChange, onSearchQueryChange }: TasksMfeProps) {
  const completed = tasks.filter((task) => task.isCompleted).length;

  return <>
    <StatsPanel total={tasks.length} active={tasks.length - completed} completed={completed} />
    <section className="filter-container">{(['all', 'active', 'completed'] as Filter[]).map((option) => <button key={option} className={`filter-btn ${filter === option ? 'active' : ''}`} type="button" onClick={() => onFilterChange(option)}>{option[0].toUpperCase() + option.slice(1)}</button>)}</section>
    <div className="search-container"><i className="fas fa-search" /><input value={searchQuery} onChange={(event) => onSearchQueryChange(event.target.value)} placeholder="Search tasks" aria-label="Search tasks" /></div>
  </>;
}
