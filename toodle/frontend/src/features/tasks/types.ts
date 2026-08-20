// Shared domain contracts used by React components and the API adapter.
export type Priority = 'low' | 'medium' | 'high';
export type Filter = 'all' | 'active' | 'completed';
export type CalendarView = 'day' | 'week' | 'month';

export interface Task {
  id: string;
  title: string;
  description: string;
  startDate: string;
  startTime: string;
  dueDate: string;
  dueTime: string;
  priority: Priority;
  isCompleted: boolean;
  categoryId: string | null;
  categoryColor: string | null;
  createdAt: string;
  version: number;
}

export interface Category {
  id: string;
  name: string;
  color: string;
}

export interface TaskDraft {
  title: string;
  description: string;
  startDate: string;
  startTime: string;
  dueDate: string;
  dueTime: string;
  priority: Priority;
  categoryId: string | null;
}
