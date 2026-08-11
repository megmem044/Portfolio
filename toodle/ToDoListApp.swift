import SwiftUI

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
