// Calendar tests verify view-aware navigation behavior.
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { CalendarMfe } from './CalendarMfe';
import type { CalendarView } from '../../features/tasks/types';

function renderCalendar(view: CalendarView) {
  const onDateChange = vi.fn();
  render(<CalendarMfe tasks={[]} currentDate={new Date(2026, 7, 12)} view={view} onViewChange={vi.fn()} onDateChange={onDateChange} onEditTask={vi.fn()} onCreateTask={vi.fn()} filter="all" searchQuery="" onToggleComplete={vi.fn()} onDeleteTask={vi.fn()} />);
  return onDateChange;
}

describe('CalendarMfe', () => {
  it.each([
    ['day', new Date(2026, 7, 13)],
    ['week', new Date(2026, 7, 19)],
    ['month', new Date(2026, 8, 12)],
  ] as const)('moves the %s view forward by one period', async (view, expectedDate) => {
    const user = userEvent.setup();
    const onDateChange = renderCalendar(view);
    await user.click(screen.getByRole('button', { name: 'Next period' }));
    expect(onDateChange).toHaveBeenCalledOnce();
    expect(onDateChange.mock.calls[0][0]).toEqual(expectedDate);
  });
});
