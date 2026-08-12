import Foundation

struct Task: Identifiable, Codable, Equatable {
    var id: UUID
    var title: String
    var description: String
    var dueDate: Date
    var isCompleted: Bool
    var createdAt: Date
    var priority: Priority
    
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
    
    init(
        id: UUID = UUID(),
        title: String,
        description: String = "",
        dueDate: Date = Date(),
        isCompleted: Bool = false,
        createdAt: Date = Date(),
        priority: Priority = .medium
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.dueDate = dueDate
        self.isCompleted = isCompleted
        self.createdAt = createdAt
        self.priority = priority
    }
}

// MARK: - Sample Data
extension Task {
    static let sampleTasks: [Task] = [
        Task(title: "Buy groceries", description: "Milk, eggs, bread, fruits", dueDate: Date().addingTimeInterval(86400), priority: .medium),
        Task(title: "Finish project report", description: "Complete the quarterly report", dueDate: Date().addingTimeInterval(172800), priority: .high),
        Task(title: "Call mom", description: "Weekly catch-up call", dueDate: Date(), priority: .low),
        Task(title: "Gym workout", description: "Leg day", dueDate: Date(), isCompleted: true, priority: .medium)
    ]
}
