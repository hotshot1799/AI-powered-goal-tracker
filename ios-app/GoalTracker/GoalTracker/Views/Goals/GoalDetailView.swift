//
//  GoalDetailView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct GoalDetailView: View {
    let goal: Goal
    @ObservedObject var viewModel: GoalsViewModel

    @State private var showAddProgress = false
    @State private var showDeleteAlert = false
    @State private var progressValue: Double = 0
    @State private var progressNote = ""
    @State private var isLoading = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Goal Header
                VStack(alignment: .leading, spacing: 12) {
                    Text(goal.category)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Color.blue.opacity(0.2))
                        .foregroundColor(.blue)
                        .cornerRadius(8)

                    Text(goal.description)
                        .font(.title2)
                        .fontWeight(.bold)

                    HStack {
                        Image(systemName: "calendar")
                            .foregroundColor(.secondary)
                        Text("Target: \(goal.targetDate, style: .date)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(UIColor.secondarySystemGroupedBackground))
                .cornerRadius(12)

                // Progress Section
                VStack(alignment: .leading, spacing: 12) {
                    Text("Progress")
                        .font(.headline)

                    VStack(spacing: 8) {
                        HStack {
                            Text("\(Int(goal.progress))%")
                                .font(.title)
                                .fontWeight(.bold)

                            Spacer()
                        }

                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                Rectangle()
                                    .fill(Color.gray.opacity(0.2))
                                    .frame(height: 20)
                                    .cornerRadius(10)

                                Rectangle()
                                    .fill(LinearGradient(
                                        gradient: Gradient(colors: [Color.blue, Color.purple]),
                                        startPoint: .leading,
                                        endPoint: .trailing
                                    ))
                                    .frame(width: geometry.size.width * (goal.progress / 100), height: 20)
                                    .cornerRadius(10)
                            }
                        }
                        .frame(height: 20)
                    }
                }
                .padding()
                .background(Color(UIColor.secondarySystemGroupedBackground))
                .cornerRadius(12)

                // Update Progress Button
                Button(action: { showAddProgress = true }) {
                    Label("Update Progress", systemImage: "arrow.up.circle.fill")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }

                // Delete Goal Button
                Button(action: { showDeleteAlert = true }) {
                    Label("Delete Goal", systemImage: "trash")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .foregroundColor(.red)
                        .cornerRadius(10)
                }

                Spacer()
            }
            .padding()
        }
        .background(Color(UIColor.systemGroupedBackground))
        .navigationTitle("Goal Details")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showAddProgress) {
            AddProgressView(goalId: goal.id, currentProgress: goal.progress, viewModel: viewModel)
        }
        .alert("Delete Goal", isPresented: $showDeleteAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Delete", role: .destructive) {
                deleteGoal()
            }
        } message: {
            Text("Are you sure you want to delete this goal? This action cannot be undone.")
        }
    }

    private func deleteGoal() {
        Task {
            do {
                try await viewModel.deleteGoal(id: goal.id)
            } catch {
                print("Error deleting goal: \(error)")
            }
        }
    }
}

struct AddProgressView: View {
    @Environment(\.dismiss) var dismiss
    let goalId: Int
    let currentProgress: Double
    @ObservedObject var viewModel: GoalsViewModel

    @State private var progressValue: Double
    @State private var note = ""
    @State private var isLoading = false
    @State private var errorMessage: String?

    init(goalId: Int, currentProgress: Double, viewModel: GoalsViewModel) {
        self.goalId = goalId
        self.currentProgress = currentProgress
        self.viewModel = viewModel
        _progressValue = State(initialValue: currentProgress)
    }

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Progress Update")) {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Progress:")
                            Spacer()
                            Text("\(Int(progressValue))%")
                                .fontWeight(.bold)
                        }

                        Slider(value: $progressValue, in: 0...100, step: 1)
                    }

                    TextField("Note (optional)", text: $note, axis: .vertical)
                        .lineLimit(3...6)
                }

                if let errorMessage = errorMessage {
                    Section {
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }

                Section {
                    Button(action: updateProgress) {
                        if isLoading {
                            HStack {
                                Spacer()
                                ProgressView()
                                Spacer()
                            }
                        } else {
                            Text("Update Progress")
                                .frame(maxWidth: .infinity)
                                .fontWeight(.semibold)
                        }
                    }
                    .disabled(isLoading)
                }
            }
            .navigationTitle("Update Progress")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
        }
    }

    private func updateProgress() {
        isLoading = true
        errorMessage = nil

        Task {
            do {
                try await APIService.shared.addProgress(
                    goalId: goalId,
                    progressValue: progressValue,
                    note: note.isEmpty ? nil : note
                )

                await viewModel.fetchGoals()

                await MainActor.run {
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}

#Preview {
    NavigationView {
        GoalDetailView(
            goal: Goal(
                id: 1,
                userId: 1,
                category: "Health",
                description: "Exercise 5 times a week",
                targetDate: Date(),
                progress: 65,
                createdAt: Date()
            ),
            viewModel: GoalsViewModel()
        )
    }
}
