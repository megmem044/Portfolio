import Foundation
import SwiftUI

enum TaskFilter: String, CaseIterable {
    case all = "All"
    case active = "Active"
    case completed = "Completed"
}

class TaskViewModel: ObservableObject {
    @Published var tasks: [Task] = [] {
        didSet {
            saveTasks()
        }
    }
    @Published var selectedFilter: TaskFilter = .all
    @Published var searchText: String = ""
    
    private let tasksKey = "savedTasks"
    
    init() {
        loadTasks()
    }
    
    // MARK: - Filtered Tasks
    var filteredTasks: [Task] {
        var result = tasks
        
        // Apply filter
        switch selectedFilter {
        case .all:
            break
        case .active:
            result = result.filter { !$0.isCompleted }
        case .completed:
            result = result.filter { $0.isCompleted }
        }
        
        // Apply search
        if !searchText.isEmpty {
            result = result.filter { task in
                task.title.localizedCaseInsensitiveContains(searchText) ||
                task.description.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        // Sort by due date, then by priority
        return result.sorted { task1, task2 in
            if task1.isCompleted != task2.isCompleted {
                return !task1.isCompleted
            }
            if task1.dueDate != task2.dueDate {
                return task1.dueDate < task2.dueDate
            }
            return priorityOrder(task1.priority) > priorityOrder(task2.priority)
        }
    }
    
    private func priorityOrder(_ priority: Task.Priority) -> Int {
        switch priority {
        case .high: return 3
        case .medium: return 2
        case .low: return 1
        }
    }
    
    // MARK: - Statistics
    var completedCount: Int {
        tasks.filter { $0.isCompleted }.count
    }
    
    var activeCount: Int {
        tasks.filter { !$0.isCompleted }.count
    }
    
    var totalCount: Int {
        tasks.count
    }
    
    // MARK: - CRUD Operations
    func addTask(_ task: Task) {
        tasks.append(task)
    }
    
    func updateTask(_ task: Task) {
        if let index = tasks.firstIndex(where: { $0.id == task.id }) {
            tasks[index] = task
        }
    }
    
    func deleteTask(_ task: Task) {
        tasks.removeAll { $0.id == task.id }
    }
    
    func deleteTasks(at offsets: IndexSet) {
        let tasksToDelete = offsets.map { filteredTasks[$0] }
        for task in tasksToDelete {
            deleteTask(task)
        }
    }
    
    func toggleCompletion(for task: Task) {
        if let index = tasks.firstIndex(where: { $0.id == task.id }) {
            tasks[index].isCompleted.toggle()
        }
    }
    
    // MARK: - Persistence
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
    
    // MARK: - Helper Methods
    func clearCompleted() {
        tasks.removeAll { $0.isCompleted }
    }
}
