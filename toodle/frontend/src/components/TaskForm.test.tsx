// Task form tests cover the create and edit payloads sent to the application shell.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TaskForm } from './TaskForm';
import type { Task } from '../features/tasks/types';

const commonProps = { defaultDate: '2026-08-12', categories: [], onCreateCategory: vi.fn(), onDelete: vi.fn(), onClose: vi.fn() };

describe('TaskForm', () => {
  it('trims and submits a newly created task', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    render(<TaskForm {...commonProps} onSave={onSave} />);
    await user.type(screen.getByLabelText('Title'), '  Prepare interview  ');
    await user.type(screen.getByLabelText('Description'), '  Review project notes  ');
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ title: 'Prepare interview', description: 'Review project notes', startDate: '2026-08-12' }));
  });

  it('loads and submits edits to an existing task', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    const task: Task = { id: 'task-1', title: 'Old title', description: '', startDate: '2026-08-12', startTime: '', dueDate: '2026-08-12', dueTime: '', priority: 'medium', isCompleted: false, categoryId: null, categoryColor: null, createdAt: '2026-08-12T00:00:00Z', version: 0 };
    render(<TaskForm {...commonProps} task={task} onSave={onSave} />);
    const title = screen.getByLabelText('Title');
    await user.clear(title);
    await user.type(title, 'Updated title');
    await user.click(screen.getByRole('button', { name: 'High' }));
    await user.click(screen.getByRole('button', { name: 'Save' }));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ title: 'Updated title', priority: 'high' }));
  });
});
