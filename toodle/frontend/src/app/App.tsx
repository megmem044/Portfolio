// Application shell: coordinates authentication, remote task state, navigation, and modal workflows.
import { useEffect, useState } from 'react';

import { AuthForm } from '../components/AuthForm';
import { TaskForm } from '../components/TaskForm';

import {
  authApi,
  ApiRequestError,
  bffApi,
  categoryApi,
  taskApi,
  type AuthSession,
} from '../features/tasks/api';

import {
  dateToKey,
  isTaskInView,
  matchesTask,
  sortTasks,
} from '../features/tasks/taskUtils';

import type {
  CalendarView,
  Category,
  Filter,
  Task,
  TaskDraft,
} from '../features/tasks/types';

import {
  CalendarMfe,
  CalendarViewSwitcher,
} from '../mfe/calendar/CalendarMfe';

import { TasksMfe } from '../mfe/tasks/TasksMfe';

type NewTaskDefaults = {
  date: string;
  time?: string;
};

export function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [error, setError] = useState<string>();

  const [session, setSession] = useState<AuthSession | null>(() =>
    authApi.getSession()
  );

  const [view, setView] = useState<CalendarView>('day');
  const [filter, setFilter] = useState<Filter>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const [currentDate, setCurrentDate] = useState(() => new Date());

  const [editingTask, setEditingTask] = useState<Task>();
  const [newTaskDefaults, setNewTaskDefaults] =
    useState<NewTaskDefaults>();

  const [deletingTaskId, setDeletingTaskId] =
    useState<string>();

  // Load the user's tasks and categories after authentication.
  useEffect(() => {
    if (!session) {
      return;
    }

    bffApi
      .bootstrap()
      .then(
        ({
          tasks: loadedTasks,
          categories: loadedCategories,
        }) => {
          setTasks(loadedTasks);
          setCategories(loadedCategories);
        }
      )
      .catch((requestError: Error) => {
        setError(requestError.message);
      });
  }, [session]);

  // Allow Escape to close any open task/delete modal.
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setEditingTask(undefined);
        setNewTaskDefaults(undefined);
        setDeletingTaskId(undefined);
      }
    };

    window.addEventListener('keydown', closeOnEscape);

    return () => {
      window.removeEventListener('keydown', closeOnEscape);
    };
  }, []);

  // Tasks shown for the currently selected calendar view.
  const viewTasks = tasks.filter((task) =>
    isTaskInView(task, currentDate, view)
  );

  // Tasks shown after search and filter logic.
  const filteredTasks = sortTasks(
    tasks.filter((task) =>
      matchesTask(task, filter, searchQuery)
    )
  );

  const isFormOpen =
    editingTask !== undefined ||
    newTaskDefaults !== undefined;

  const openNewTask = (
    date = dateToKey(currentDate),
    time?: string
  ) => {
    setEditingTask(undefined);

    setNewTaskDefaults({
      date,
      time,
    });
  };

  const closeForm = () => {
    setEditingTask(undefined);
    setNewTaskDefaults(undefined);
  };

  const openTask = (task: Task) => {
    setEditingTask(task);
    setNewTaskDefaults(undefined);
  };

  const refreshAfterConflict = async () => {
    try {
      const refreshed = await bffApi.bootstrap();
      setTasks(refreshed.tasks);
      setCategories(refreshed.categories);
      closeForm();
      setError('This task changed in another tab. Your task list was refreshed. Reopen it and try again.');
    } catch {
      setError('This task changed in another tab. Refresh the page, then reopen it and try again.');
    }
  };

  const saveTask = async (draft: TaskDraft) => {
    const category = categories.find(
      (item) => item.id === draft.categoryId
    );

    try {
      const savedTask = editingTask
        ? await taskApi.update({
            ...editingTask,
            ...draft,
            categoryColor: category?.color ?? null,
          })
        : await taskApi.create(draft);

      setTasks((currentTasks) =>
        editingTask
          ? currentTasks.map((task) =>
              task.id === savedTask.id
                ? savedTask
                : task
            )
          : [...currentTasks, savedTask]
      );

      closeForm();
    } catch (requestError) {
      if (requestError instanceof ApiRequestError && requestError.status === 409) {
        await refreshAfterConflict();
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to save task'
      );
    }
  };

  const deleteTask = async (taskId: string) => {
    try {
      await taskApi.delete(taskId);

      setTasks((currentTasks) =>
        currentTasks.filter(
          (task) => task.id !== taskId
        )
      );

      setDeletingTaskId(undefined);
      closeForm();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to delete task'
      );
    }
  };

  const createCategory = async (
    name: string,
    color: string
  ) => {
    const category = await categoryApi.create(
      name,
      color
    );

    setCategories((currentCategories) => [
      ...currentCategories,
      category,
    ]);

    return category;
  };

  const toggleTaskComplete = async (
    taskId: string
  ) => {
    const task = tasks.find(
      (item) => item.id === taskId
    );

    if (!task) {
      return;
    }

    try {
      const updatedTask = await taskApi.update({
        ...task,
        isCompleted: !task.isCompleted,
      });

      setTasks((currentTasks) =>
        currentTasks.map((item) =>
          item.id === taskId
            ? updatedTask
            : item
        )
      );
    } catch (requestError) {
      if (requestError instanceof ApiRequestError && requestError.status === 409) {
        await refreshAfterConflict();
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to update task'
      );
    }
  };

  // Authentication screen.
  if (!session) {
    return (
      <AuthForm
        onAuthenticated={setSession}
      />
    );
  }

  const firstName =
    session.name.trim().split(/\s+/)[0] ||
    'there';

  return (
    <main className="app-container">
      {/* Application header */}
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true"><span /></span>
          <h1>Toodle</h1>
        </div>

        <div className="header-actions">
          <CalendarViewSwitcher
            view={view}
            onViewChange={setView}
          />

          <button
            className="header-btn"
            type="button"
            onClick={() => openNewTask()}
          >
            + Add Task
          </button>

          <button
            className="profile-icon"
            type="button"
            title={`Sign out ${session.email}`}
            onClick={() => {
              authApi.logout();
              setSession(null);
            }}
          >
            {session.name
              .charAt(0)
              .toUpperCase()}
          </button>
        </div>
      </header>

      {/* Welcome / mascot area */}
      <section className="welcome-panel">
        <div className="shape-field" aria-hidden="true">
          <span className="shape shape-sunburst" />
          <span className="shape shape-arch" />
          <span className="shape shape-dot" />
          <span className="shape shape-cloud" />
          <span className="shape shape-spark" />
        </div>
        <div className="welcome-copy">
          <p className="welcome-eyebrow">
            YOUR SPACE
          </p>

          <h2>
            Hey {firstName}, what are we
            <span> getting done today?</span>
          </h2>

          <p className="welcome-description">
            Keep your day clear, colorful,
            and under control.
          </p>
        </div>
      </section>

      {/* API / application errors */}
      {error && (
        <p role="alert">
          {error}
        </p>
      )}

      {/* Tasks micro-frontend */}
      <TasksMfe
        tasks={viewTasks}
        filter={filter}
        searchQuery={searchQuery}
        onFilterChange={setFilter}
        onSearchQueryChange={
          setSearchQuery
        }
      />

      {/* Calendar micro-frontend */}
      <CalendarMfe
        tasks={filteredTasks}
        currentDate={currentDate}
        view={view}
        onViewChange={setView}
        onDateChange={setCurrentDate}
        onEditTask={openTask}
        onCreateTask={openNewTask}
        filter={filter}
        searchQuery={searchQuery}
        onToggleComplete={
          toggleTaskComplete
        }
        onDeleteTask={
          setDeletingTaskId
        }
      />

      {/* Create / edit task modal */}
      {isFormOpen && (
        <TaskForm
          task={editingTask}
          defaultDate={
            newTaskDefaults?.date ??
            dateToKey(currentDate)
          }
          defaultStartTime={
            newTaskDefaults?.time
          }
          categories={categories}
          onCreateCategory={
            createCategory
          }
          onSave={saveTask}
          onDelete={
            editingTask
              ? () =>
                  setDeletingTaskId(
                    editingTask.id
                  )
              : undefined
          }
          onClose={closeForm}
        />
      )}

      {/* Delete confirmation modal */}
      {deletingTaskId && (
        <div
          className="modal-overlay show"
          role="presentation"
        >
          <div
            className="modal modal-small"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-task-title"
          >
            <div className="modal-content">
              <h3 id="delete-task-title">
                Delete Task
              </h3>

              <p>
                Are you sure you want to
                delete this task? This action
                cannot be undone.
              </p>

              <div className="form-actions">
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() =>
                    setDeletingTaskId(
                      undefined
                    )
                  }
                >
                  Cancel
                </button>

                <button
                  className="btn btn-danger"
                  type="button"
                  onClick={() =>
                    deleteTask(
                      deletingTaskId
                    )
                  }
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
