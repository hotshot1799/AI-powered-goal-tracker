//
//  GoalTrackerApp.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

@main
struct GoalTrackerApp: App {
    @StateObject private var authManager = AuthManager.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
        }
    }
}
