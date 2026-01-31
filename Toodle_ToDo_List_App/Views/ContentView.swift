import SwiftUI

struct ContentView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    @State private var showingAddTask = false
    @State private var selectedTask: Task?
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Statistics Header
                StatisticsHeaderView()
                
                // Filter Picker
                FilterPickerView()
                
                // Task List
                TaskListView(selectedTask: $selectedTask)
            }
            .navigationTitle("My Tasks")
            .searchable(text: $viewModel.searchText, prompt: "Search tasks...")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddTask = true }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                    }
                }
                
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Button(role: .destructive, action: viewModel.clearCompleted) {
                            Label("Clear Completed", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(isPresented: $showingAddTask) {
                AddEditTaskView(mode: .add)
            }
            .sheet(item: $selectedTask) { task in
                AddEditTaskView(mode: .edit(task))
            }
        }
    }
}

// MARK: - Statistics Header
struct StatisticsHeaderView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    
    var body: some View {
        HStack(spacing: 20) {
            StatCard(title: "Total", count: viewModel.totalCount, color: .blue)
            StatCard(title: "Active", count: viewModel.activeCount, color: .orange)
            StatCard(title: "Done", count: viewModel.completedCount, color: .green)
        }
        .padding()
        .background(Color(.systemGroupedBackground))
    }
}

struct StatCard: View {
    let title: String
    let count: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 4) {
            Text("\(count)")
                .font(.title2.bold())
                .foregroundColor(color)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
    }
}

// MARK: - Filter Picker
struct FilterPickerView: View {
    @EnvironmentObject var viewModel: TaskViewModel
    
    var body: some View {
        Picker("Filter", selection: $viewModel.selectedFilter) {
            ForEach(TaskFilter.allCases, id: \.self) { filter in
                Text(filter.rawValue).tag(filter)
            }
        }
        .pickerStyle(.segmented)
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
}

// MARK: - Preview
#Preview {
    ContentView()
        .environmentObject(TaskViewModel())
}
