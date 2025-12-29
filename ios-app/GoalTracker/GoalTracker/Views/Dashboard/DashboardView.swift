//
//  DashboardView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct DashboardView: View {
    @StateObject private var viewModel = GoalsViewModel()
    @StateObject private var authManager = AuthManager.shared
    @State private var showAddGoal = false
    @State private var showLogoutAlert = false

    var body: some View {
        NavigationView {
            ZStack {
                Color(UIColor.systemGroupedBackground)
                    .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 20) {
                        // AI Suggestions Card
                        if !viewModel.suggestions.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Image(systemName: "lightbulb.fill")
                                        .foregroundColor(.yellow)
                                    Text("AI Suggestions")
                                        .font(.headline)
                                        .fontWeight(.semibold)
                                }

                                ForEach(Array(viewModel.suggestions.enumerated()), id: \.offset) { index, suggestion in
                                    HStack(alignment: .top, spacing: 10) {
                                        Image(systemName: "sparkles")
                                            .font(.caption)
                                            .foregroundColor(.blue)
                                        Text(suggestion)
                                            .font(.subheadline)
                                            .foregroundColor(.secondary)
                                    }
                                    .padding(.vertical, 4)
                                }
                            }
                            .padding()
                            .background(
                                LinearGradient(
                                    gradient: Gradient(colors: [Color.blue.opacity(0.1), Color.purple.opacity(0.1)]),
                                    startPoint: .leading,
                                    endPoint: .trailing
                                )
                            )
                            .cornerRadius(12)
                            .padding(.horizontal)
                        }

                        // Goals Section
                        if viewModel.isLoading {
                            ProgressView()
                                .padding()
                        } else if viewModel.goals.isEmpty {
                            VStack(spacing: 16) {
                                Image(systemName: "target")
                                    .font(.system(size: 60))
                                    .foregroundColor(.gray)

                                Text("No Goals Yet")
                                    .font(.title2)
                                    .fontWeight(.semibold)

                                Text("Create your first goal to start tracking your progress")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                    .multilineTextAlignment(.center)

                                Button(action: { showAddGoal = true }) {
                                    Label("Create Goal", systemImage: "plus.circle.fill")
                                        .fontWeight(.semibold)
                                }
                                .buttonStyle(.borderedProminent)
                            }
                            .padding(40)
                        } else {
                            LazyVStack(spacing: 16) {
                                ForEach(viewModel.goals) { goal in
                                    NavigationLink(destination: GoalDetailView(goal: goal, viewModel: viewModel)) {
                                        GoalCardView(goal: goal)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                            .padding(.horizontal)
                        }

                        if let errorMessage = viewModel.errorMessage {
                            Text(errorMessage)
                                .font(.caption)
                                .foregroundColor(.red)
                                .padding()
                        }
                    }
                    .padding(.vertical)
                }
                .refreshable {
                    await viewModel.fetchGoals()
                    await viewModel.fetchSuggestions()
                }
            }
            .navigationTitle("Goals")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showAddGoal = true }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title3)
                    }
                }

                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showLogoutAlert = true }) {
                        Image(systemName: "rectangle.portrait.and.arrow.right")
                            .font(.title3)
                    }
                }
            }
            .sheet(isPresented: $showAddGoal) {
                AddGoalView(viewModel: viewModel)
            }
            .alert("Logout", isPresented: $showLogoutAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Logout", role: .destructive) {
                    Task {
                        try? await authManager.logout()
                    }
                }
            } message: {
                Text("Are you sure you want to logout?")
            }
            .task {
                await viewModel.fetchGoals()
                await viewModel.fetchSuggestions()
            }
        }
    }
}

#Preview {
    DashboardView()
}
