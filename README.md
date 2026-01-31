# Toodle - To-Do List Application

A modern, feature-rich to-do list web application with a beautiful warm color palette and intuitive user interface. Toodle helps you organize your daily tasks with multiple calendar views, custom categories, and a delightful user experience.

---

## Table of Contents

1. [Features Overview](#features-overview)
2. [Detailed Feature Documentation](#detailed-feature-documentation)
3. [Design System](#design-system)
4. [System Architecture](#system-architecture)
5. [Component Documentation](#component-documentation)
6. [Getting Started](#getting-started)
7. [Usage Guide](#usage-guide)
8. [Technical Implementation](#technical-implementation)
9. [Browser Support](#browser-support)

---

## Features Overview

| Feature | Description |
|---------|-------------|
| Task Management | Full CRUD operations with rich task details |
| Category System | User-defined categories with 10-color palette |
| Calendar Views | Day, Week, and Month views |
| Filtering & Search | Real-time search and status filtering |
| User Authentication | Login, signup, and password recovery |
| PWA Support | Installable app with offline capabilities |
| Statistics Dashboard | Live task counts and progress tracking |
| Responsive Design | Works on desktop and mobile devices |

---

## Detailed Feature Documentation

### 1. Task Management System

The core functionality of Toodle revolves around comprehensive task management.

#### Creating Tasks
- **Title** (Required): The main task name displayed prominently
- **Description** (Optional): Additional details or notes for the task
- **Start Date**: When the task begins
- **Start Time**: Specific start time with 15-minute interval selector
- **Due Date**: Task deadline
- **Due Time**: Specific end time with 15-minute interval selector
- **Priority Level**: Visual importance indicator (Low/Medium/High)
- **Category**: Optional categorization with color coding

#### Task Display
- **Task Cards**: Each task appears as a card with:
  - Category-colored banner at the top (if category assigned)
  - Task title in the banner (white text on colored background)
  - Checkbox for completion toggle
  - Description text (if provided)
  - Time range display (e.g., "9:00 AM - 10:30 AM")
  - Priority badge (color-coded)
  - Edit and Delete action buttons

#### Task Actions
- **Complete/Uncomplete**: Click the circular checkbox to toggle status
- **Edit**: Opens the task modal with pre-filled data
- **Delete**: Two-step confirmation process to prevent accidents

---

### 2. Category System

A flexible categorization system to organize tasks by project, context, or any custom grouping.

#### Category Features
- **User-Defined Names**: Create categories like "Work", "Personal", "Health", etc.
- **Persistent Storage**: Categories saved in localStorage
- **Single Assignment**: Each task can have one category
- **Visual Indicators**: Category color appears as task banner

#### 10-Color Palette
| Index | Color Name | Hex Code | Best For |
|-------|------------|----------|----------|
| 0 | Sunflower | `#FFDA03` | Bright, cheerful tasks |
| 1 | Mango | `#FF8243` | Creative projects |
| 2 | Persimmon | `#EC5800` | Urgent but not critical |
| 3 | Vermillion | `#E34234` | Important deadlines |
| 4 | Watermelon | `#FD4659` | Fun activities |
| 5 | Bubblegum | `#FF6FD8` | Personal items |
| 6 | Orchid | `#DA70D6` | Wellness/self-care |
| 7 | Strawberry | `#F75394` | Social events |
| 8 | Ruby | `#E0115F` | High priority |
| 9 | Burgundy | `#800020` | Professional/formal |

#### Creating Categories
1. Open the Add/Edit Task modal
2. Click **"+ Add Category"** button
3. Enter a descriptive category name
4. Select a color from the 10 available options
5. Click **"Save"** to create

---

### 3. Calendar Views

Three distinct views to visualize your schedule at different time scales.

#### Day View (Default)
- **Purpose**: Focus on today's tasks
- **Display**: Vertical list of task cards
- **Features**:
  - Full task details visible
  - Easy task completion toggle
  - Quick access to edit/delete
  - Empty state message when no tasks

#### Week View
- **Purpose**: Weekly planning and time blocking
- **Display**: 7-column grid with 24 hourly rows
- **Features**:
  - Tasks positioned by start time
  - Task height reflects duration
  - Category colors for quick identification
  - Today's column highlighted
  - Click any cell to add task at that time
  - Scrollable for all 24 hours

#### Month View
- **Purpose**: Long-term overview and planning
- **Display**: Traditional calendar grid
- **Features**:
  - Day cells showing up to 2 tasks
  - "+N more" indicator for additional tasks
  - Tasks colored by category
  - Previous/next month days shown in muted style
  - Click any day to view that day's tasks
  - Today highlighted with accent color

#### Navigation
- **Previous/Next**: Arrow buttons to navigate time periods
- **Date Label**: Shows current date/week/month
- **View Switcher**: Dropdown menu to change views

---

### 4. Filtering & Search

Powerful filtering options to find and focus on specific tasks.

#### Status Filters
| Filter | Shows | Use Case |
|--------|-------|----------|
| All | Every task | Full overview |
| Active | Incomplete tasks only | Focus mode |
| Completed | Finished tasks only | Review accomplishments |

#### Search Functionality
- **Real-time Search**: Results update as you type
- **Search Fields**: Matches against title and description
- **Case Insensitive**: "Meeting" matches "meeting" or "MEETING"
- **Combines with Filters**: Search within filtered results

---

### 5. Statistics Dashboard

Live metrics displayed at the top of the application.

#### Stat Cards
- **Total**: Count of all tasks
- **Active**: Count of incomplete tasks (lime color)
- **Completed**: Count of finished tasks (raspberry color)

#### How Stats Update
- Automatically recalculated on any task change
- Respects current date context
- Provides instant feedback on productivity

---

### 6. User Authentication

Complete authentication flow for personalized task management.

#### Login Page (`login.html`)
- **Email Input**: User's registered email
- **Password Input**: Secure password field
- **Forgot Password Link**: Navigate to recovery
- **Sign Up Link**: For new users
- **Error Messages**: Clear feedback for invalid credentials

#### Sign Up Page (`signup.html`)
- **Name Input**: User's display name
- **Email Input**: Must be unique
- **Password Input**: Create secure password
- **Confirm Password**: Prevent typos
- **Validation**: Real-time field validation

#### Forgot Password Flow
1. Enter registered email on forgot-password.html
2. Simulated email sent (demo mode)
3. Navigate to reset-password.html
4. Enter new password twice
5. Password updated in localStorage

#### Profile Menu
- **Profile Icon**: Shows user's initial in header
- **Logout Option**: Clears session and redirects to login

---

### 7. Progressive Web App (PWA)

Toodle can be installed as a native-like application.

#### PWA Features
- **Installable**: Add to home screen on mobile/desktop
- **Offline Support**: Service worker caches assets
- **App-like Experience**: Full-screen, no browser chrome
- **Fast Loading**: Cached resources load instantly

#### Manifest Configuration (`manifest.json`)
```json
{
    "name": "Toodle - To-Do List",
    "short_name": "Toodle",
    "start_url": "/index.html",
    "display": "standalone",
    "theme_color": "#BF2B52",
    "background_color": "#FFFCF5"
}
```

#### Service Worker (`sw.js`)
- Caches HTML, CSS, JS, and icon files
- Serves cached content when offline
- Updates cache when online

---

### 8. User Interface Components

#### Header
- **Logo**: "Toodle" in Pacifico font on raspberry background
- **View Button**: Dropdown for Day/Week/Month selection
- **Add Task Button**: Opens task creation modal
- **Profile Icon**: User initial with logout menu

#### Task Modal
- **Modal Overlay**: Darkened background, click to close
- **Modal Header**: Title ("New Task" or "Edit Task") with close button
- **Scrollable Content**: Form fits without page scroll
- **Form Fields**: All task properties editable
- **Action Buttons**: Cancel, Save, Delete (edit mode only)

#### Delete Confirmation Modal
- **Smaller Modal**: Focused confirmation dialog
- **Warning Message**: Clear deletion warning
- **Two Buttons**: Cancel (safe) and Delete (destructive)

#### Custom Scrollbar
- **Track**: Raspberry color (`#BF2B52`)
- **Thumb**: Lemon color (`#F4AF31`)
- **Hover State**: Lime color (`#90EE90`)
- **Width**: 12px for visibility

---

## Design System

### Primary Color Palette

| Color | Variable | Hex Code | RGB | Usage |
|-------|----------|----------|-----|-------|
| Cream | `--cream` | `#FFFCF5` | 255, 252, 245 | Page background |
| Vanilla | `--vanilla` | `#F5E9CF` | 245, 233, 207 | Card backgrounds |
| Lime | `--lime` | `#BFB74B` | 191, 183, 75 | Success, active states |
| Lemon | `--lemon` | `#F4AF31` | 244, 175, 49 | Accents, warnings |
| Pink Grapefruit | `--pink-grapefruit` | `#D96C81` | 217, 108, 129 | Container background |
| Raspberry | `--raspberry` | `#BF2B52` | 191, 43, 82 | Primary actions, buttons |

### Typography

#### Font Families
- **Brand/Logo**: `'Pacifico', cursive`
  - Used for: "Toodle" logo
  - Weight: 400 (regular)
  - Size: 36px in header
  
- **Body Text**: `'Nunito', sans-serif`
  - Used for: All other text
  - Weights: 400, 500, 600, 700
  - Base size: 16px

#### Type Scale
| Element | Size | Weight |
|---------|------|--------|
| Logo | 36px | 400 |
| Modal Title | 24px | 700 |
| Section Headers | 18px | 600 |
| Body Text | 16px | 500 |
| Labels | 14px | 600 |
| Small Text | 12px | 500 |
| Badges | 11px | 600 |

### Spacing System

| Size | Value | Use |
|------|-------|-----|
| xs | 4px | Icon padding |
| sm | 8px | Tight spacing |
| md | 12px | Default gaps |
| lg | 16px | Section spacing |
| xl | 24px | Container padding |
| xxl | 32px | Major sections |

### Border Radius

| Variable | Value | Use |
|----------|-------|-----|
| `--radius` | 12px | Cards, modals, buttons |
| `--radius-sm` | 8px | Small elements, badges |

### Shadows

| Variable | Value | Use |
|----------|-------|-----|
| `--shadow` | `0 2px 8px rgba(191, 183, 75, 0.12)` | Cards, subtle elevation |
| `--shadow-lg` | `0 4px 16px rgba(191, 183, 75, 0.18)` | Modals, hover states |

---

## System Architecture

### Project Structure

```
To-Do List App/
├── README.md                 # This documentation
├── ToDoListApp.swift         # iOS app entry (if building iOS)
├── Models/                   # iOS data models
│   └── Task.swift
├── ViewModels/               # iOS business logic
│   └── TaskViewModel.swift
├── Views/                    # iOS SwiftUI views
│   ├── AddEditTaskView.swift
│   ├── ContentView.swift
│   ├── TaskListView.swift
│   └── TaskRowView.swift
└── web/                      # Web application
    ├── index.html            # Main dashboard
    ├── login.html            # Login page
    ├── signup.html           # Registration page
    ├── forgot-password.html  # Password recovery
    ├── reset-password.html   # Password reset
    ├── app.js                # TaskManager class (1173 lines)
    ├── auth.js               # Authentication utilities
    ├── styles.css            # Main stylesheet (1499 lines)
    ├── auth.css              # Auth page styles
    ├── sw.js                 # Service worker
    ├── manifest.json         # PWA manifest
    └── icons/                # App icons
        ├── icon.svg
        ├── icon-192.png
        └── icon-512.png
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ Header  │  │ Stats   │  │ Filters │  │ Calendar Views  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
│       │            │            │                 │          │
└───────┴────────────┴────────────┴─────────────────┴──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TaskManager Class                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Task CRUD    │  │ Category Mgmt│  │ View Rendering   │   │
│  │ Operations   │  │ Operations   │  │ (Day/Week/Month) │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                    │             │
│  ┌──────┴─────────────────┴────────────────────┴───────┐    │
│  │              Event Handling & State Management       │    │
│  └──────────────────────────┬──────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     localStorage                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐  │
│  │ toodle_tasks    │  │ toodle_categories│  │ users      │  │
│  │ (Task[])        │  │ (Category[])     │  │ (User[])   │  │
│  └─────────────────┘  └──────────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Documentation

### TaskManager Class (`app.js`)

The central controller managing all application logic.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `tasks` | Array | All task objects |
| `categories` | Array | All category objects |
| `currentFilter` | String | 'all', 'active', or 'completed' |
| `currentView` | String | 'day', 'week', or 'month' |
| `currentDate` | Date | Currently viewed date |
| `searchQuery` | String | Current search text |
| `editingTaskId` | Number/null | ID of task being edited |
| `selectedCategoryColor` | Number/null | Selected color index |

#### Core Methods

| Method | Purpose |
|--------|---------|
| `loadTasks()` | Retrieve tasks from localStorage |
| `saveTasks()` | Persist tasks to localStorage |
| `loadCategories()` | Retrieve categories from localStorage |
| `saveCategories()` | Persist categories to localStorage |
| `addTask(task)` | Create new task |
| `updateTask(id, updates)` | Modify existing task |
| `deleteTask(id)` | Remove task by ID |
| `toggleComplete(id)` | Toggle task completion status |

#### Rendering Methods

| Method | Purpose |
|--------|---------|
| `render()` | Main render dispatcher |
| `renderDayView()` | Render day task list |
| `renderWeekView()` | Render week schedule grid |
| `renderMonthView()` | Render month calendar |
| `renderTask(task)` | Generate task card HTML |
| `renderCategories()` | Update category selector |
| `updateStats()` | Refresh statistics display |

#### Event Handlers

| Method | Triggered By |
|--------|--------------|
| `openModal(taskId?)` | Add Task button, Edit button |
| `closeModal()` | Close button, Cancel, overlay click |
| `handleSubmit(e)` | Form submission |
| `navigateDate(delta)` | Previous/Next buttons |
| `setFilter(filter)` | Filter tab clicks |
| `setView(view)` | View dropdown selection |

### Data Models

#### Task Object

```javascript
{
    id: 1706345600000,           // Unix timestamp as ID
    title: "Complete project",    // Required: task name
    description: "Finish docs",   // Optional: details
    dueDate: "2026-01-27",       // ISO date string
    startDate: "2026-01-27",     // ISO date string
    startTime: "09:00",          // 24-hour format
    dueTime: "17:00",            // 24-hour format
    priority: "high",            // 'low' | 'medium' | 'high'
    isCompleted: false,          // Completion status
    categoryId: 1,               // Reference to category
    categoryColor: 3             // Color index (0-9)
}
```

#### Category Object

```javascript
{
    id: 1706345600001,    // Unix timestamp as ID
    name: "Work",         // User-defined name
    color: 3              // Color palette index (0-9)
}
```

#### User Object

```javascript
{
    name: "John Doe",           // Display name
    email: "john@example.com",  // Unique identifier
    password: "hashed_value"    // Stored password
}
```

### CSS Organization (`styles.css`)

```css
/* File Structure (1499 lines) */

/* 1. CSS Variables (Lines 1-27) */
:root { /* Color palette, shadows, spacing */ }

/* 2. Reset & Base (Lines 29-60) */
*, body { /* Global resets, fonts */ }

/* 3. Scrollbar Styles (Lines 36-58) */
::-webkit-scrollbar { /* Custom scrollbar */ }

/* 4. App Container (Lines 70-80) */
.app-container { /* Main wrapper */ }

/* 5. Header (Lines 82-140) */
.app-header { /* Logo, buttons */ }

/* 6. Statistics (Lines 142-200) */
.stats-container, .stat-card { /* Dashboard stats */ }

/* 7. Navigation (Lines 202-260) */
.date-navigation { /* Date controls */ }

/* 8. Filters (Lines 262-320) */
.filter-container, .filter-btn { /* Filter tabs */ }

/* 9. Day View (Lines 322-400) */
.day-view, .task-list { /* Task list */ }

/* 10. Task Cards (Lines 402-600) */
.task-item, .task-banner { /* Task styling */ }

/* 11. Week View (Lines 602-800) */
.week-view, .week-schedule { /* Week grid */ }

/* 12. Month View (Lines 802-1000) */
.month-view, .month-grid { /* Month calendar */ }

/* 13. Modals (Lines 1002-1200) */
.modal-overlay, .modal { /* Dialogs */ }

/* 14. Forms (Lines 1202-1350) */
.form-group, .priority-selector { /* Form elements */ }

/* 15. Categories (Lines 1352-1450) */
.category-selector, .color-picker { /* Category UI */ }

/* 16. Responsive (Lines 1452-1499) */
@media queries { /* Mobile styles */ }
```

---

## Getting Started

### Prerequisites

- **Web Browser**: Chrome 80+, Firefox 75+, Safari 13+, or Edge 80+
- **Local Server** (optional): Python 3 or Node.js for development

### Installation

#### Option 1: Direct File Access
```bash
# Simply open in browser
open web/index.html
```

#### Option 2: Python Server
```bash
cd web
python -m http.server 8080
# Navigate to http://localhost:8080
```

#### Option 3: Node.js Server
```bash
npx http-server web -p 8080
# Navigate to http://localhost:8080
```

### First-Time Setup

1. Open the application (redirects to login.html)
2. Click "Sign up here!" to create an account
3. Fill in name, email, and password
4. Click "Sign Up" to register
5. You're redirected to the main dashboard

### Installing as PWA

**Chrome/Edge Desktop:**
1. Click the install icon (⊕) in the address bar
2. Click "Install" in the popup

**Chrome Mobile:**
1. Tap the three-dot menu
2. Select "Add to Home Screen"
3. Tap "Add"

**Safari iOS:**
1. Tap the Share button
2. Select "Add to Home Screen"
3. Tap "Add"

---

## Usage Guide

### Quick Start Workflow

```
1. Login/Create Account
        ↓
2. Click "Add Task"
        ↓
3. Fill in task details
        ↓
4. (Optional) Create category
        ↓
5. Click "Save"
        ↓
6. View in Day/Week/Month
        ↓
7. Click checkbox when done
```

### Creating Your First Task

1. **Click "Add Task"** in the header
2. **Enter Title**: "Complete project report"
3. **Add Description**: "Include Q4 metrics and projections"
4. **Set Date**: Select start and due dates
5. **Set Time**: Choose start time (9:00 AM) and end time (5:00 PM)
6. **Choose Priority**: Click "High"
7. **Add Category**: Click "+ Add Category", name it "Work", pick red
8. **Save**: Click the "Save" button

### Managing Categories

#### Create Category
1. Open Add Task modal
2. Click "+ Add Category"
3. Type category name
4. Click a color circle
5. Click "Save"

#### Use Category
1. When adding/editing a task
2. Click an existing category button
3. Category is assigned to task

### Switching Views

1. Click "View" button in header
2. Select from dropdown:
   - **Day**: Detailed task list
   - **Week**: 7-day schedule grid
   - **Month**: Calendar overview
3. Use ← → arrows to navigate dates

### Filtering Tasks

| Click | Shows |
|-------|-------|
| "All" tab | Every task for the period |
| "Active" tab | Only incomplete tasks |
| "Completed" tab | Only finished tasks |

### Completing Tasks

**In Day View:**
- Click the circle checkbox on the left of any task

**In Week/Month View:**
- Click on the task to open it
- Click the checkbox in the modal

**Visual Feedback:**
- Completed tasks show reduced opacity
- Text appears with strikethrough

### Editing Tasks

1. Click "Edit" button on task card
2. Modal opens with current values
3. Modify any fields
4. Click "Save" to update

### Deleting Tasks

1. Click "Delete" button on task card
2. Confirmation modal appears
3. Click "Delete" to confirm
4. Or "Cancel" to keep task

---

## Technical Implementation

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Structure | HTML5 | Semantic markup |
| Styling | CSS3 | Layout, theming, animations |
| Logic | JavaScript ES6+ | Application functionality |
| Storage | localStorage API | Client-side persistence |
| Offline | Service Workers | PWA caching |
| Icons | Font Awesome 6 | UI icons |
| Fonts | Google Fonts | Typography |

### Key Implementation Details

#### State Management
- Single source of truth in TaskManager class
- All changes flow through class methods
- Automatic localStorage sync on mutations

#### Event Delegation
```javascript
// Instead of adding listeners to each task
taskList.addEventListener('click', (e) => {
    if (e.target.matches('.edit-btn')) {
        const id = e.target.dataset.id;
        this.openModal(id);
    }
});
```

#### Template Rendering
```javascript
renderTask(task) {
    return `
        <div class="task-item ${task.isCompleted ? 'completed' : ''}">
            <div class="task-banner">${task.title}</div>
            <!-- ... more HTML ... -->
        </div>
    `;
}
```

#### Date Handling
- Dates stored as ISO strings (YYYY-MM-DD)
- Times stored as 24-hour strings (HH:MM)
- JavaScript Date objects for calculations
- Formatted for display (e.g., "Today", "Tomorrow")

### Performance Optimizations

1. **Minimal DOM Updates**: Re-render only changed sections
2. **Event Delegation**: Single listeners on parent containers
3. **CSS Animations**: GPU-accelerated transforms
4. **Lazy Rendering**: Week/Month views only when active

---

## Browser Support

| Browser | Minimum Version | Notes |
|---------|-----------------|-------|
| Chrome | 80+ | Full support, PWA install |
| Firefox | 75+ | Full support |
| Safari | 13+ | Full support, iOS PWA |
| Edge | 80+ | Full support, PWA install |
| Opera | 67+ | Full support |

### Required Features
- CSS Custom Properties
- CSS Grid & Flexbox
- ES6+ JavaScript
- localStorage API
- Service Workers (for PWA)

---

## License

This project is available for personal and educational use.

---

## Credits

- **Fonts**: [Google Fonts](https://fonts.google.com/) (Pacifico, Nunito)
- **Icons**: [Font Awesome](https://fontawesome.com/)
- **Inspiration**: Modern task management applications

---

*Built with love using vanilla HTML, CSS, and JavaScript*
