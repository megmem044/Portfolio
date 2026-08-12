// Application shell: coordinates authentication, remote task state, navigation, and modal workflows.
import { useEffect, useState } from 'react';
import { TaskForm } from '../components/TaskForm';
import { AuthForm } from '../components/AuthForm';
import { authApi, bffApi, categoryApi, taskApi, type AuthSession } from '../features/tasks/api';
import { dateToKey, isTaskInView, matchesTask, sortTasks } from '../features/tasks/taskUtils';
import type { CalendarView, Category, Filter, Task, TaskDraft } from '../features/tasks/types';
import { CalendarMfe, CalendarViewSwitcher } from '../mfe/calendar/CalendarMfe';
import { TasksMfe } from '../mfe/tasks/TasksMfe';

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
  const filteredTasks = sortTasks(tasks.filter((task) => matchesTask(task, filter, searchQuery)));
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
  if (!session) return <AuthForm onAuthenticated={setSession} />;

  return <main className="app-container">
    <header className="app-header">
      <h1>Toodle</h1>
      <div className="header-actions">
        <CalendarViewSwitcher view={view} onViewChange={setView} />
        <button className="header-btn" type="button" onClick={() => openNewTask()}>Add Task</button>
        <button className="profile-icon" type="button" title={`Sign out ${session.email}`} onClick={() => { authApi.logout(); setSession(null); }}> {session.name.charAt(0).toUpperCase()} </button>
      </div>
    </header>

    {error && <p role="alert">{error}</p>}
    <TasksMfe tasks={viewTasks} filter={filter} searchQuery={searchQuery} onFilterChange={setFilter} onSearchQueryChange={setSearchQuery} />
    <CalendarMfe tasks={filteredTasks} currentDate={currentDate} view={view} onViewChange={setView} onDateChange={setCurrentDate} onEditTask={openTask} onCreateTask={openNewTask} filter={filter} searchQuery={searchQuery} onToggleComplete={async (taskId) => { const task = tasks.find((item) => item.id === taskId); if (task) { try { const updatedTask = await taskApi.update({ ...task, isCompleted: !task.isCompleted }); setTasks((currentTasks) => currentTasks.map((item) => item.id === taskId ? updatedTask : item)); } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to update task'); } } }} onDeleteTask={setDeletingTaskId} />
    {isFormOpen && <TaskForm task={editingTask} defaultDate={newTaskDefaults?.date ?? dateToKey(currentDate)} defaultStartTime={newTaskDefaults?.time} categories={categories} onCreateCategory={createCategory} onSave={saveTask} onDelete={editingTask ? () => setDeletingTaskId(editingTask.id) : undefined} onClose={closeForm} />}
    {deletingTaskId && <div className="modal-overlay show" role="presentation"><div className="modal modal-small" role="dialog" aria-modal="true"><div className="modal-content"><h3>Delete Task</h3><p>Are you sure you want to delete this task? This action cannot be undone.</p><div className="form-actions"><button className="btn btn-secondary" type="button" onClick={() => setDeletingTaskId(undefined)}>Cancel</button><button className="btn btn-danger" type="button" onClick={() => deleteTask(deletingTaskId)}>Delete</button></div></div></div></div>}
  </main>;
}
