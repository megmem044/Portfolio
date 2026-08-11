# Toodle - Source Code Guide

A comprehensive developer guide for the Toodle To-Do List application, covering both the **iOS/SwiftUI** and **Web/JavaScript** implementations.

---

## Project Structure Overview

```
To-Do List App/
├── ToDoListApp.swift          # iOS app entry point
├── Models/
│   └── Task.swift             # Core data model
├── ViewModels/
│   └── TaskViewModel.swift    # Business logic & state management
├── Views/
│   ├── ContentView.swift      # Main container view
│   ├── TaskListView.swift     # Task list display
│   ├── TaskRowView.swift      # Individual task row
│   └── AddEditTaskView.swift  # Task creation/editing form
├── web/
│   ├── index.html             # Main web app page
│   ├── app.js                 # Core JavaScript logic
│   ├── styles.css             # Main stylesheet
│   ├── auth.js                # Authentication logic
│   ├── auth.css               # Auth page styles
│   ├── login.html             # Login page
│   ├── signup.html            # Registration page
│   ├── forgot-password.html   # Password recovery
│   ├── reset-password.html    # Password reset
│   ├── manifest.json          # PWA manifest
│   ├── sw.js                  # Service worker
│   └── icons/                 # App icons
└── README.md                  # Project documentation
```

---

## iOS/SwiftUI Implementation

### Architecture: MVVM (Model-View-ViewModel)

The iOS app follows the MVVM pattern for clean separation of concerns:
- **Model**: Data structures (`Task`)
- **View**: SwiftUI views (UI only)
- **ViewModel**: Business logic and state (`TaskViewModel`)

---

### Entry Point: `ToDoListApp.swift`

```swift
@main
struct ToDoListApp: App {
    @StateObject private var taskViewModel = TaskViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(taskViewModel)
        }
    }
}
```

**Key Concepts:**
- `@main` marks the app entry point
- `@StateObject` creates and owns the `TaskViewModel` instance
- `.environmentObject()` injects the view model into the view hierarchy
- All child views can access it via `@EnvironmentObject`

---

### Model Layer: `Models/Task.swift`

#### Task Struct

```swift
struct Task: Identifiable, Codable, Equatable {
    var id: UUID
    var title: String
    var description: String
    var dueDate: Date
    var isCompleted: Bool
    var createdAt: Date
    var priority: Priority
}
```

**Protocol Conformance:**
| Protocol | Purpose |
|----------|---------|
| `Identifiable` | Enables use in `ForEach` without explicit id |
| `Codable` | JSON encoding/decoding for persistence |
| `Equatable` | Comparison for SwiftUI diffing and animations |

#### Priority Enum

```swift
enum Priority: String, Codable, CaseIterable {
    case low = "Low"
    case medium = "Medium"
    case high = "High"
    
    var color: String {
        switch self {
        case .low: return "green"
        case .medium: return "orange"
        case .high: return "red"
        }
    }
}
```

**Features:**
- `CaseIterable` enables iteration for UI pickers
- `rawValue` provides human-readable strings
- Computed `color` property for consistent styling

#### Sample Data

```swift
extension Task {
    static let sampleTasks: [Task] = [
        Task(title: "Buy groceries", ...),
        // More samples for previews and testing
    ]
}
```

---

### ViewModel Layer: `ViewModels/TaskViewModel.swift`

#### Class Declaration

```swift
class TaskViewModel: ObservableObject {
    @Published var tasks: [Task] = [] {
        didSet { saveTasks() }
    }
    @Published var selectedFilter: TaskFilter = .all
    @Published var searchText: String = ""
}
```

**Key Patterns:**
- `ObservableObject` enables SwiftUI observation
- `@Published` triggers view updates on change
- `didSet` observer auto-saves on any task modification

#### Filter Enum

```swift
enum TaskFilter: String, CaseIterable {
    case all = "All"
    case active = "Active"
    case completed = "Completed"
}
```

#### Computed Properties

```swift
// Filtered and sorted task list
var filteredTasks: [Task] {
    var result = tasks
    
    // Apply filter (all/active/completed)
    switch selectedFilter { ... }
    
    // Apply search text
    if !searchText.isEmpty { ... }
    
    // Sort by: incomplete first, then due date, then priority
    return result.sorted { ... }
}

// Statistics
var completedCount: Int { tasks.filter { $0.isCompleted }.count }
var activeCount: Int { tasks.filter { !$0.isCompleted }.count }
var totalCount: Int { tasks.count }
```

#### CRUD Operations

| Method | Description |
|--------|-------------|
| `addTask(_ task:)` | Appends new task to array |
| `updateTask(_ task:)` | Finds by ID and replaces |
| `deleteTask(_ task:)` | Removes matching task |
| `deleteTasks(at:)` | Batch delete by IndexSet |
| `toggleCompletion(for:)` | Toggles `isCompleted` flag |
| `clearCompleted()` | Removes all completed tasks |

#### Persistence (UserDefaults)

```swift
private let tasksKey = "savedTasks"

private func saveTasks() {
    if let encoded = try? JSONEncoder().encode(tasks) {
        UserDefaults.standard.set(encoded, forKey: tasksKey)
    }
}

private func loadTasks() {
    if let data = UserDefaults.standard.data(forKey: tasksKey),
       let decoded = try? JSONDecoder().decode([Task].self, from: data) {
        tasks = decoded
    }
}
```

---

### View Layer

#### `Views/ContentView.swift`

The main container view with navigation and layout.

**Structure:**
```
NavigationStack
├── VStack
│   ├── StatisticsHeaderView     # Task counts
│   ├── FilterPickerView         # All/Active/Completed
│   └── TaskListView             # Task list
├── .navigationTitle("My Tasks")
├── .searchable(...)             # Search bar
├── .toolbar { ... }             # Add & menu buttons
└── .sheet { ... }               # Modal presentations
```

**Key Components:**

1. **StatisticsHeaderView** - Displays task counts
   ```swift
   HStack {
       StatCard(title: "Total", count: viewModel.totalCount, color: .blue)
       StatCard(title: "Active", count: viewModel.activeCount, color: .orange)
       StatCard(title: "Done", count: viewModel.completedCount, color: .green)
   }
   ```

2. **FilterPickerView** - Segmented control for filtering
   ```swift
   Picker("Filter", selection: $viewModel.selectedFilter) {
       ForEach(TaskFilter.allCases, id: \.self) { filter in
           Text(filter.rawValue).tag(filter)
       }
   }
   .pickerStyle(.segmented)
   ```

3. **Sheet Presentations**
   ```swift
   .sheet(isPresented: $showingAddTask) {
       AddEditTaskView(mode: .add)
   }
   .sheet(item: $selectedTask) { task in
       AddEditTaskView(mode: .edit(task))
   }
   ```

---

#### `Views/TaskListView.swift`

Displays the filtered task list with swipe actions.

**Key Features:**

1. **Empty State Handling**
   ```swift
   if viewModel.filteredTasks.isEmpty {
       EmptyStateView()
   } else {
       ForEach(viewModel.filteredTasks) { task in ... }
   }
   ```

2. **Swipe Actions**
   ```swift
   .swipeActions(edge: .trailing) {
       Button(role: .destructive) { viewModel.deleteTask(task) }
   }
   .swipeActions(edge: .leading) {
       Button { viewModel.toggleCompletion(for: task) }
   }
   ```

3. **Dynamic Empty State** - Different messages based on filter and search state

---

#### `Views/TaskRowView.swift`

Individual task row with all details.

**Layout:**
```
HStack
├── Completion Button (circle/checkmark)
├── VStack (Task Details)
│   ├── HStack
│   │   ├── Title (with strikethrough if completed)
│   │   └── PriorityBadge
│   ├── Description (if present)
│   └── Due Date with icon
└── Chevron indicator
```

**Smart Date Formatting:**
```swift
private var formattedDueDate: String {
    if calendar.isDateInToday(task.dueDate) { return "Today" }
    else if calendar.isDateInTomorrow(task.dueDate) { return "Tomorrow" }
    else if calendar.isDateInYesterday(task.dueDate) { return "Yesterday" }
    else { return dateFormatter.string(from: task.dueDate) }
}
```

**Due Date Color Logic:**
```swift
private var dueDateColor: Color {
    if task.isCompleted { return .secondary }
    if task.dueDate < Date() { return .red }      // Overdue
    if calendar.isDateInToday(task.dueDate) { return .orange }
    return .secondary
}
```

---

#### `Views/AddEditTaskView.swift`

Form for creating and editing tasks.

**Mode Enum:**
```swift
enum TaskEditMode: Identifiable {
    case add
    case edit(Task)
}
```

**Form Sections:**
1. **Title** - Required text field
2. **Description** - Optional TextEditor
3. **Schedule** - DatePicker with date and time
4. **Priority** - Segmented picker with color indicators
5. **Delete** - Only shown in edit mode

**Key Patterns:**

1. **State Initialization on Appear**
   ```swift
   .onAppear { loadExistingTask() }
   
   private func loadExistingTask() {
       if let task = existingTask {
           title = task.title
           description = task.description
           // ... load other fields
       }
   }
   ```

2. **Unified Save Logic**
   ```swift
   private func saveTask() {
       if let existingTask = existingTask {
           // Update existing
           var updatedTask = existingTask
           updatedTask.title = trimmedTitle
           viewModel.updateTask(updatedTask)
       } else {
           // Create new
           let newTask = Task(title: trimmedTitle, ...)
           viewModel.addTask(newTask)
       }
       dismiss()
   }
   ```

3. **Delete Confirmation**
   ```swift
   .alert("Delete Task", isPresented: $showingDeleteAlert) {
       Button("Cancel", role: .cancel) { }
       Button("Delete", role: .destructive) { ... }
   }
   ```

---

## Web Implementation

### Architecture: Class-Based JavaScript

The web app uses a single `TaskManager` class to handle all functionality.

---

### Core Class: `web/app.js`

```javascript
class TaskManager {
    constructor() {
        this.tasks = this.loadTasks();
        this.categories = this.loadCategories();
        this.currentFilter = 'all';
        this.currentView = 'day';       // day, week, month
        this.currentDate = new Date();
        this.searchQuery = '';
        this.editingTaskId = null;
        
        this.initializeElements();
        this.bindEvents();
        this.renderCategories();
        this.render();
    }
}
```

**Initialization Flow:**
1. Load persisted data from localStorage
2. Cache DOM element references
3. Bind event listeners
4. Render initial UI

---

### Data Persistence

```javascript
loadTasks() {
    const saved = localStorage.getItem('toodle_tasks');
    return saved ? JSON.parse(saved) : [];
}

saveTasks() {
    localStorage.setItem('toodle_tasks', JSON.stringify(this.tasks));
}

loadCategories() {
    const saved = localStorage.getItem('toodle_categories');
    return saved ? JSON.parse(saved) : [];
}
```

---

### Key Features

#### 1. Calendar Views

| View | Description |
|------|-------------|
| **Day** | List of tasks for selected date |
| **Week** | 7-day grid with time slots |
| **Month** | Calendar grid with task dots |

#### 2. Category System

- User-defined categories with names
- 10-color palette for visual distinction
- Categories stored separately in localStorage

#### 3. Task Properties

```javascript
{
    id: uniqueId,
    title: "Task name",
    description: "Optional details",
    startDate: "2026-01-29",
    startTime: "09:00",
    dueDate: "2026-01-29",
    dueTime: "17:00",
    priority: "medium",     // low, medium, high
    categoryId: "uuid",     // optional
    completed: false,
    createdAt: timestamp
}
```

---

### HTML Structure: `web/index.html`

```
app-container
├── app-header
│   ├── Logo ("Toodle")
│   ├── View dropdown (Day/Week/Month)
│   ├── Add Task button
│   └── Profile icon
├── stats-container
│   ├── Total count
│   ├── Active count
│   └── Completed count
├── date-navigation
│   ├── Previous button
│   ├── Current date label
│   └── Next button
├── filter-container (All/Active/Completed)
├── day-view (task list)
├── week-view (time grid)
├── month-view (calendar)
├── empty-state
└── task-modal (add/edit form)
```

---

### Authentication: `web/auth.js`

Handles user registration, login, and password recovery.

**Pages:**
- `login.html` - User sign-in
- `signup.html` - New user registration
- `forgot-password.html` - Password recovery request
- `reset-password.html` - Password reset form

**Session Management:**
```javascript
// Check authentication on main page
if (!localStorage.getItem('currentUser')) {
    window.location.href = 'login.html';
}

// Logout
localStorage.removeItem('currentUser');
window.location.href = 'login.html';
```

---

### PWA Support

#### `web/manifest.json`
- App name and icons
- Theme colors
- Display mode (standalone)

#### `web/sw.js`
- Service worker for offline support
- Asset caching strategy

---

## Data Flow Comparison

### iOS (SwiftUI)

```
User Action
    ↓
View (e.g., TaskRowView)
    ↓
ViewModel Method (e.g., toggleCompletion)
    ↓
@Published property updates
    ↓
didSet triggers saveTasks()
    ↓
SwiftUI re-renders affected views
```

### Web (JavaScript)

```
User Action
    ↓
Event Listener
    ↓
TaskManager Method
    ↓
this.tasks array updated
    ↓
this.saveTasks() called
    ↓
this.render() updates DOM
```

---

## Design System

### Color Palette

| Purpose | iOS (SwiftUI) | Web (CSS) |
|---------|---------------|-----------|
| Low Priority | `.green` | `#4CAF50` / `green` |
| Medium Priority | `.orange` | `#FF9800` / `orange` |
| High Priority | `.red` | `#F44336` / `red` |
| Background | `.systemGroupedBackground` | Warm palette |

### Category Colors (Web)

```javascript
const CATEGORY_COLORS = [
    '#FFDA03', // Sunflower
    '#FF8243', // Mango
    '#EC5800', // Persimmon
    '#E34234', // Vermillion
    '#FD4659', // Watermelon
    '#FF6FD8', // Bubblegum
    '#DA70D6', // Orchid
    '#F75394', // Strawberry
    '#E0115F', // Ruby
    '#800020'  // Burgundy
];
```

---

## SwiftUI Best Practices Used

| Practice | Example |
|----------|---------|
| `@StateObject` for ownership | App entry point owns ViewModel |
| `@EnvironmentObject` for sharing | Views access shared ViewModel |
| `@State` for local state | Form field values |
| `@Binding` for child-to-parent | Selected task in list |
| Computed properties | `filteredTasks`, `formattedDueDate` |
| `#Preview` macros | Each view has preview variants |

---

## Future Enhancements

### iOS
- [ ] SwiftData migration (from UserDefaults)
- [ ] CloudKit sync
- [ ] Widget support
- [ ] Notifications for due dates

### Web
- [ ] Backend API integration
- [ ] Real-time sync
- [ ] Drag-and-drop task ordering
- [ ] Dark mode toggle

---

## Quick Reference

### Add a New Task (iOS)

```swift
let task = Task(
    title: "New Task",
    description: "Details here",
    dueDate: Date().addingTimeInterval(86400),
    priority: .high
)
viewModel.addTask(task)
```

### Filter Tasks (iOS)

```swift
viewModel.selectedFilter = .active
viewModel.searchText = "groceries"
// filteredTasks computed property auto-updates
```

### Toggle Completion (iOS)

```swift
viewModel.toggleCompletion(for: task)
// Animates with .spring(response: 0.3)
```

---

*Last Updated: January 29, 2026*
