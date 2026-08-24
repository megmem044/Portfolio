-- Measures the owner-scoped task-list query used by the benchmark account.
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT task.*, category.color
FROM task
LEFT JOIN category ON category.id = task.category_id
WHERE task.owner_id = (
    SELECT owner_id
    FROM task
    GROUP BY owner_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);
