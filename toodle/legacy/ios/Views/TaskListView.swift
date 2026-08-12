import SwiftUI

struct TaskListView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    @Binding var selectedTask: Task?
    
    var body: some View {
        List {
            if viewModel.filteredTasks.isEmpty {
                EmptyStateView()
            } else {
                ForEach(viewModel.filteredTasks) { task in
                    TaskRowView(task: task)
                        .contentShape(Rectangle())
                        .onTapGesture {
                            selectedTask = task
                        }
                        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                            Button(role: .destructive) {
                                withAnimation {
                                    viewModel.deleteTask(task)
                                }
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                        .swipeActions(edge: .leading, allowsFullSwipe: true) {
                            Button {
                                withAnimation {
                                    viewModel.toggleCompletion(for: task)
                                }
                            } label: {
                                Label(
                                    task.isCompleted ? "Undo" : "Complete",
                                    systemImage: task.isCompleted ? "arrow.uturn.backward" : "checkmark"
                                )
                            }
                            .tint(task.isCompleted ? .orange : .green)
                        }
                }
            }
        }
        .listStyle(.plain)
        .animation(.default, value: viewModel.filteredTasks)
    }
}

// MARK: - Empty State
struct EmptyStateView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: emptyStateIcon)
                .font(.system(size: 60))
                .foregroundColor(.secondary.opacity(0.5))
            
            Text(emptyStateTitle)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Text(emptyStateMessage)
                .font(.subheadline)
                .foregroundColor(.secondary.opacity(0.8))
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 60)
        .listRowBackground(Color.clear)
        .listRowSeparator(.hidden)
    }
    
    private var emptyStateIcon: String {
        switch viewModel.selectedFilter {
        case .all:
            return "checklist"
        case .active:
            return "tray"
        case .completed:
            return "checkmark.circle"
        }
    }
    
    private var emptyStateTitle: String {
        if !viewModel.searchText.isEmpty {
            return "No Results"
        }
        switch viewModel.selectedFilter {
        case .all:
            return "No Tasks Yet"
        case .active:
            return "No Active Tasks"
        case .completed:
            return "No Completed Tasks"
        }
    }
    
    private var emptyStateMessage: String {
        if !viewModel.searchText.isEmpty {
            return "Try a different search term"
        }
        switch viewModel.selectedFilter {
        case .all:
            return "Tap + to add your first task"
        case .active:
            return "All caught up! 🎉"
        case .completed:
            return "Complete some tasks to see them here"
        }
    }
}

#Preview {
    TaskListView(selectedTask: .constant(nil))
        .environmentObject(TaskViewModel())
}
