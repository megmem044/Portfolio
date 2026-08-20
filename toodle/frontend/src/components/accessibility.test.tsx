// Runs automated axe checks against the main forms and dialog.
import { render } from '@testing-library/react';
import axe from 'axe-core';
import { describe, expect, it, vi } from 'vitest';

import { AuthForm } from './AuthForm';
import { TaskForm } from './TaskForm';

async function expectNoAccessibilityViolations(container: HTMLElement) {
  const results = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } });
  expect(results.violations).toEqual([]);
}

describe('component accessibility', () => {
  it('has no detectable issues on the authentication form', async () => {
    const { container } = render(<AuthForm onAuthenticated={vi.fn()} />);
    await expectNoAccessibilityViolations(container);
  });

  it('has no detectable issues in the new-task dialog', async () => {
    const { container } = render(
      <TaskForm
        defaultDate="2026-08-19"
        categories={[]}
        onCreateCategory={vi.fn()}
        onSave={vi.fn()}
        onClose={vi.fn()}
      />,
    );
    await expectNoAccessibilityViolations(container);
  });
});
