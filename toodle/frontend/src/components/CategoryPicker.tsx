// Category selector with inline category creation for the task form.
import { useState } from 'react';
import type { Category } from '../features/tasks/types';

interface CategoryPickerProps {
  categories: Category[];
  selectedCategoryId: string | null;
  onSelect: (categoryId: string | null) => void;
  onCreate: (name: string, color: string) => Promise<Category>;
}

export function CategoryPicker({ categories, selectedCategoryId, onSelect, onCreate }: CategoryPickerProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [name, setName] = useState('');
  const [color, setColor] = useState<string | null>(null);
  const saveCategory = async () => {
    if (!name.trim() || color === null) return;
    const category = await onCreate(name.trim(), color);
    onSelect(category.id);
    setName('');
    setColor(null);
    setIsAdding(false);
  };
  return <div className="category-selector">
    {categories.map((category) => <button type="button" key={category.id} className={`category-btn color-${category.color} ${selectedCategoryId === category.id ? 'active' : ''}`} onClick={() => onSelect(selectedCategoryId === category.id ? null : category.id)}>{category.name}</button>)}
    <button type="button" className="add-category-btn" onClick={() => setIsAdding(true)}>+ Add Category</button>
    <div className={`new-category-input ${isAdding ? 'show' : ''}`}>
      <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Enter category name" />
      <label className="color-label">Pick a color:</label>
      <div className="color-picker-container">{Array.from({ length: 10 }, (_, index) => String(index)).map((colorIndex) => <button aria-label={`Select color ${colorIndex}`} type="button" key={colorIndex} className={`color-option color-${colorIndex} ${color === colorIndex ? 'selected' : ''}`} onClick={() => setColor(colorIndex)} />)}</div>
      <div className="category-actions"><button type="button" id="saveCategoryBtn" onClick={saveCategory}>Save</button><button type="button" id="cancelCategoryBtn" onClick={() => setIsAdding(false)}>Cancel</button></div>
    </div>
  </div>;
}
