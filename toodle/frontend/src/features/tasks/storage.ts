// Legacy migration helpers retained while browser-local persistence is phased out.
import type { Category, Task } from './types';

function readList<T>(key: string): T[] {
  try {
    const storedValue = localStorage.getItem(key);
    return storedValue ? (JSON.parse(storedValue) as T[]) : [];
  } catch {
    return [];
  }
}

export function loadTasks(): Task[] {
  return readList<Task>('tasks');
}

export function loadCategories(): Category[] {
  return readList<Category>('toodle_categories');
}

export function saveTasks(tasks: Task[]) {
  localStorage.setItem('tasks', JSON.stringify(tasks));
}

export function saveCategories(categories: Category[]) {
  localStorage.setItem('toodle_categories', JSON.stringify(categories));
}
