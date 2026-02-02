import SwiftUI

enum TaskEditMode: Identifiable {
    case add
    case edit(Task)
    
    var id: String {
        switch self {
        case .add: return "add"
        case .edit(let task): return task.id.uuidString
        }
    }
}

struct AddEditTaskView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var viewModel: TaskViewModel
    
    let mode: TaskEditMode
    
    @State private var title: String = ""
    @State private var description: String = ""
    @State private var dueDate: Date = Date()
    @State private var priority: Task.Priority = .medium
    @State private var showingDeleteAlert = false
    
    private var isEditing: Bool {
        if case .edit = mode { return true }
        return false
    }
    
    private var existingTask: Task? {
        if case .edit(let task) = mode { return task }
        return nil
    }
    
    var body: some View {
        NavigationStack {
            Form {
                // Title Section
                Section {
                    TextField("Task title", text: $title)
                        .font(.body)
                } header: {
                    Text("Title")
                }
                
                // Description Section
                Section {
                    TextEditor(text: $description)
                        .frame(minHeight: 80)
                } header: {
                    Text("Description")
                } footer: {
                    Text("Optional: Add more details about this task")
                }
                
                // Due Date Section
                Section {
                    DatePicker("Due Date", selection: $dueDate, displayedComponents: [.date, .hourAndMinute])
                } header: {
                    Text("Schedule")
                }
                
                // Priority Section
                Section {
                    Picker("Priority", selection: $priority) {
                        ForEach(Task.Priority.allCases, id: \.self) { priority in
                            HStack {
                                Circle()
                                    .fill(priorityColor(priority))
                                    .frame(width: 10, height: 10)
                                Text(priority.rawValue)
                            }
                            .tag(priority)
                        }
                    }
                    .pickerStyle(.segmented)
                } header: {
                    Text("Priority")
                }
                
                // Delete Button (Edit mode only)
                if isEditing {
                    Section {
                        Button(role: .destructive) {
                            showingDeleteAlert = true
                        } label: {
                            HStack {
                                Spacer()
                                Label("Delete Task", systemImage: "trash")
                                Spacer()
                            }
                        }
                    }
                }
            }
            .navigationTitle(isEditing ? "Edit Task" : "New Task")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        saveTask()
                    }
                    .fontWeight(.semibold)
                    .disabled(title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
            .alert("Delete Task", isPresented: $showingDeleteAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Delete", role: .destructive) {
                    if let task = existingTask {
                        viewModel.deleteTask(task)
                        dismiss()
                    }
                }
            } message: {
                Text("Are you sure you want to delete this task? This action cannot be undone.")
            }
            .onAppear {
                loadExistingTask()
            }
        }
    }
    
    private func priorityColor(_ priority: Task.Priority) -> Color {
        switch priority {
        case .low: return .green
        case .medium: return .orange
        case .high: return .red
        }
    }
    
    private func loadExistingTask() {
        if let task = existingTask {
            title = task.title
            description = task.description
            dueDate = task.dueDate
            priority = task.priority
        }
    }
    
    private func saveTask() {
        let trimmedTitle = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedTitle.isEmpty else { return }
        
        if let existingTask = existingTask {
            // Update existing task
            var updatedTask = existingTask
            updatedTask.title = trimmedTitle
            updatedTask.description = description.trimmingCharacters(in: .whitespacesAndNewlines)
            updatedTask.dueDate = dueDate
            updatedTask.priority = priority
            viewModel.updateTask(updatedTask)
        } else {
            // Create new task
            let newTask = Task(
                title: trimmedTitle,
                description: description.trimmingCharacters(in: .whitespacesAndNewlines),
                dueDate: dueDate,
                priority: priority
            )
            viewModel.addTask(newTask)
        }
        
        dismiss()
    }
}

#Preview("Add Mode") {
    AddEditTaskView(mode: .add)
        .environmentObject(TaskViewModel())
}

#Preview("Edit Mode") {
    AddEditTaskView(mode: .edit(Task.sampleTasks[0]))
        .environmentObject(TaskViewModel())
}
