<!-- Custom instructions for GitHub Copilot in this iOS To-Do List project -->

# To-Do List App - Copilot Instructions

## Project Overview
This is an iOS to-do list application built with Swift and SwiftUI following MVVM architecture.

## Technology Stack
- **Language**: Swift 5.9+
- **UI Framework**: SwiftUI
- **Minimum iOS**: 17.0
- **Architecture**: MVVM (Model-View-ViewModel)
- **Persistence**: UserDefaults (can be upgraded to SwiftData)

## Coding Conventions

### Swift Style
- Use Swift's modern concurrency features when needed
- Prefer `let` over `var` when possible
- Use descriptive variable and function names
- Follow Apple's Swift API Design Guidelines

### SwiftUI Patterns
- Use `@StateObject` for view model ownership
- Use `@EnvironmentObject` to share view models
- Extract reusable components into separate views
- Use `#Preview` macros for SwiftUI previews

### Architecture Guidelines
- Keep Views focused on UI only
- Place business logic in ViewModels
- Models should be simple data containers
- Use Codable for persistence

## File Organization
```
Models/          - Data models (Task.swift)
ViewModels/      - Business logic (TaskViewModel.swift)
Views/           - SwiftUI views
```

## Key Components
- `Task`: Core data model with id, title, description, dueDate, isCompleted, priority
- `TaskViewModel`: ObservableObject managing task state and persistence
- `ContentView`: Main navigation and layout
- `TaskListView`: Displays filtered task list
- `TaskRowView`: Individual task display
- `AddEditTaskView`: Form for creating/editing tasks
