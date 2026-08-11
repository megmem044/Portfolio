import SwiftUI

struct TaskRowView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    let task: Task
    
    var body: some View {
        HStack(spacing: 12) {
            // Completion Button
            Button {
                withAnimation(.spring(response: 0.3)) {
                    viewModel.toggleCompletion(for: task)
                }
            } label: {
                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .foregroundColor(task.isCompleted ? .green : .gray)
            }
            .buttonStyle(.plain)
            
            // Task Details
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(task.title)
                        .font(.body.weight(.medium))
                        .strikethrough(task.isCompleted, color: .secondary)
                        .foregroundColor(task.isCompleted ? .secondary : .primary)
                    
                    Spacer()
                    
                    // Priority Badge
                    PriorityBadge(priority: task.priority)
                }
                
                if !task.description.isEmpty {
                    Text(task.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
                
                // Due Date
                HStack(spacing: 4) {
                    Image(systemName: "calendar")
                        .font(.caption2)
                    Text(formattedDueDate)
                        .font(.caption)
                }
                .foregroundColor(dueDateColor)
            }
            
            // Chevron
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary.opacity(0.5))
        }
        .padding(.vertical, 8)
    }
    
    private var formattedDueDate: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        
        let calendar = Calendar.current
        if calendar.isDateInToday(task.dueDate) {
            return "Today"
        } else if calendar.isDateInTomorrow(task.dueDate) {
            return "Tomorrow"
        } else if calendar.isDateInYesterday(task.dueDate) {
            return "Yesterday"
        } else {
            let dateFormatter = DateFormatter()
            dateFormatter.dateStyle = .medium
            return dateFormatter.string(from: task.dueDate)
        }
    }
    
    private var dueDateColor: Color {
        if task.isCompleted {
            return .secondary
        }
        let calendar = Calendar.current
        if task.dueDate < Date() && !calendar.isDateInToday(task.dueDate) {
            return .red
        } else if calendar.isDateInToday(task.dueDate) {
            return .orange
        }
        return .secondary
    }
}

// MARK: - Priority Badge
struct PriorityBadge: View {
    let priority: Task.Priority
    
    var body: some View {
        Text(priority.rawValue)
            .font(.caption2.weight(.semibold))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(backgroundColor.opacity(0.15))
            .foregroundColor(backgroundColor)
            .cornerRadius(6)
    }
    
    private var backgroundColor: Color {
        switch priority {
        case .low: return .green
        case .medium: return .orange
        case .high: return .red
        }
    }
}

#Preview {
    List {
        TaskRowView(task: Task.sampleTasks[0])
        TaskRowView(task: Task.sampleTasks[1])
        TaskRowView(task: Task.sampleTasks[3])
    }
    .listStyle(.plain)
    .environmentObject(TaskViewModel())
}
