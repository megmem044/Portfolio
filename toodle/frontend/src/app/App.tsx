// Application shell: coordinates authentication, remote task state, navigation, and modal workflows.
import { useEffect, useState } from 'react';
import { StatsPanel } from '../components/StatsPanel';
import { TaskForm } from '../components/TaskForm';
import { AuthForm } from '../components/AuthForm';
import { authApi, bffApi, categoryApi, taskApi, type AuthSession } from '../features/tasks/api';
import { calendarLabel, dateToKey, isTaskInView, matchesTask, sortTasks } from '../features/tasks/taskUtils';
import type { CalendarView, Category, Filter, Task, TaskDraft } from '../features/tasks/types';
import { DayView } from '../views/DayView';
import { MonthView } from '../views/MonthView';
import { WeekView } from '../views/WeekView';

type NewTaskDefaults = { date: string; time?: string };

export function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [error, setError] = useState<string>();
  const [session, setSession] = useState<AuthSession | null>(() => authApi.getSession());
  const [view, setView] = useState<CalendarView>('day');
  const [filter, setFilter] = useState<Filter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task>();
  const [newTaskDefaults, setNewTaskDefaults] = useState<NewTaskDefaults>();
  const [deletingTaskId, setDeletingTaskId] = useState<string>();

  useEffect(() => {
    if (!session) return;
    bffApi.bootstrap()
      .then(({ tasks: loadedTasks, categories: loadedCategories }) => { setTasks(loadedTasks); setCategories(loadedCategories); })
      .catch((requestError: Error) => setError(requestError.message));
  }, [session]);
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === 'Escape') { setEditingTask(undefined); setNewTaskDefaults(undefined); setDeletingTaskId(undefined); } };
    window.addEventListener('keydown', closeOnEscape);
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, []);

  const viewTasks = tasks.filter((task) => isTaskInView(task, currentDate, view));
  const displayedTasks = sortTasks(viewTasks.filter((task) => matchesTask(task, filter, searchQuery)));
  const completed = viewTasks.filter((task) => task.isCompleted).length;
  const isFormOpen = editingTask !== undefined || newTaskDefaults !== undefined;

  const openNewTask = (date = dateToKey(currentDate), time?: string) => {
    setEditingTask(undefined);
    setNewTaskDefaults({ date, time });
  };
  const closeForm = () => { setEditingTask(undefined); setNewTaskDefaults(undefined); };
  const openTask = (task: Task) => { setEditingTask(task); setNewTaskDefaults(undefined); };
  const saveTask = async (draft: TaskDraft) => {
    const category = categories.find((item) => item.id === draft.categoryId);
    try {
      const savedTask = editingTask
        ? await taskApi.update({ ...editingTask, ...draft, categoryColor: category?.color ?? null })
        : await taskApi.create(draft);
      setTasks((currentTasks) => editingTask ? currentTasks.map((task) => task.id === savedTask.id ? savedTask : task) : [...currentTasks, savedTask]);
      closeForm();
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to save task'); }
  };
  const deleteTask = async (taskId: string) => {
    try {
      await taskApi.delete(taskId);
      setTasks((currentTasks) => currentTasks.filter((task) => task.id !== taskId));
      setDeletingTaskId(undefined);
      closeForm();
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to delete task'); }
  };
  const createCategory = async (name: string, color: string) => {
    const category = await categoryApi.create(name, color);
    setCategories((currentCategories) => [...currentCategories, category]);
    return category;
  };
  const navigate = (direction: number) => setCurrentDate((date) => {
    const nextDate = new Date(date);
    if (view === 'day') nextDate.setDate(nextDate.getDate() + direction);
    if (view === 'week') nextDate.setDate(nextDate.getDate() + direction * 7);
    if (view === 'month') nextDate.setMonth(nextDate.getMonth() + direction);
    return nextDate;
  });
  const selectView = (selectedView: CalendarView) => { setView(selectedView); setIsMenuOpen(false); };

  if (!session) return <AuthForm onAuthenticated={setSession} />;

  return <main className="app-container">
    <header className="app-header">
      <h1>Toodle</h1>
      <div className="header-actions">
        <div className="view-dropdown-container">
          <button className="header-btn" type="button" onClick={() => setIsMenuOpen((open) => !open)}>View</button>
          <div className={`dropdown-menu ${isMenuOpen ? 'show' : ''}`}>
            <div className="dropdown-section">{(['day', 'week', 'month'] as CalendarView[]).map((option) => <button key={option} className={`view-option ${view === option ? 'active' : ''}`} type="button" onClick={() => selectView(option)}><i className={`fas fa-calendar-${option === 'day' ? 'day' : option === 'week' ? 'week' : 'alt'}`} /> {option[0].toUpperCase() + option.slice(1)}</button>)}</div>
          </div>
        </div>
        <button className="header-btn" type="button" onClick={() => openNewTask()}>Add Task</button>
        <button className="profile-icon" type="button" title={`Sign out ${session.email}`} onClick={() => { authApi.logout(); setSession(null); }}> {session.name.charAt(0).toUpperCase()} </button>
      </div>
    </header>

    <StatsPanel total={viewTasks.length} active={viewTasks.length - completed} completed={completed} />
    <section className="date-navigation"><button className="nav-btn" type="button" aria-label="Previous period" onClick={() => navigate(-1)}><i className="fas fa-chevron-left" /></button><h2 className="current-date">{calendarLabel(currentDate, view)}</h2><button className="nav-btn" type="button" aria-label="Next period" onClick={() => navigate(1)}><i className="fas fa-chevron-right" /></button></section>
    <section className="filter-container">{(['all', 'active', 'completed'] as Filter[]).map((option) => <button key={option} className={`filter-btn ${filter === option ? 'active' : ''}`} type="button" onClick={() => setFilter(option)}>{option[0].toUpperCase() + option.slice(1)}</button>)}</section>
    <div className="search-container"><i className="fas fa-search" /><input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search tasks" aria-label="Search tasks" /></div>
    {error && <p role="alert">{error}</p>}
    {view === 'day' && <DayView tasks={displayedTasks} filter={filter} searchQuery={searchQuery} onToggleComplete={async (taskId) => { const task = tasks.find((item) => item.id === taskId); if (task) { try { const updatedTask = await taskApi.update({ ...task, isCompleted: !task.isCompleted }); setTasks((currentTasks) => currentTasks.map((item) => item.id === taskId ? updatedTask : item)); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to update task'); } } }} onEdit={openTask} onDelete={setDeletingTaskId} />}
    {view === 'week' && <WeekView date={currentDate} tasks={displayedTasks} onSelectTask={openTask} onCreateAt={openNewTask} />}
    {view === 'month' && <MonthView date={currentDate} tasks={displayedTasks} onSelectTask={openTask} onSelectDate={(date) => { setCurrentDate(date); setView('day'); }} />}
    {isFormOpen && <TaskForm task={editingTask} defaultDate={newTaskDefaults?.date ?? dateToKey(currentDate)} defaultStartTime={newTaskDefaults?.time} categories={categories} onCreateCategory={createCategory} onSave={saveTask} onDelete={editingTask ? () => setDeletingTaskId(editingTask.id) : undefined} onClose={closeForm} />}
    {deletingTaskId && <div className="modal-overlay show" role="presentation"><div className="modal modal-small" role="dialog" aria-modal="true"><div className="modal-content"><h3>Delete Task</h3><p>Are you sure you want to delete this task? This action cannot be undone.</p><div className="form-actions"><button className="btn btn-secondary" type="button" onClick={() => setDeletingTaskId(undefined)}>Cancel</button><button className="btn btn-danger" type="button" onClick={() => deleteTask(deletingTaskId)}>Delete</button></div></div></div></div>}
  </main>;
}
