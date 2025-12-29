//
//  AddGoalView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct AddGoalView: View {
    @Environment(\.dismiss) var dismiss
    @ObservedObject var viewModel: GoalsViewModel

    @State private var category = ""
    @State private var description = ""
    @State private var targetDate = Date()
    @State private var isLoading = false
    @State private var errorMessage: String?

    let categories = ["Health", "Career", "Education", "Finance", "Personal", "Other"]

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Goal Details")) {
                    Picker("Category", selection: $category) {
                        ForEach(categories, id: \.self) { category in
                            Text(category).tag(category)
                        }
                    }

                    TextField("Description", text: $description, axis: .vertical)
                        .lineLimit(3...6)

                    DatePicker("Target Date", selection: $targetDate, in: Date()..., displayedComponents: .date)
                }

                if let errorMessage = errorMessage {
                    Section {
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundColor(.red)
                    }
                }

                Section {
                    Button(action: createGoal) {
                        if isLoading {
                            HStack {
                                Spacer()
                                ProgressView()
                                Spacer()
                            }
                        } else {
                            Text("Create Goal")
                                .frame(maxWidth: .infinity)
                                .fontWeight(.semibold)
                        }
                    }
                    .disabled(isLoading || category.isEmpty || description.isEmpty)
                }
            }
            .navigationTitle("New Goal")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .onAppear {
                if category.isEmpty {
                    category = categories[0]
                }
            }
        }
    }

    private func createGoal() {
        errorMessage = nil
        isLoading = true

        Task {
            do {
                try await viewModel.createGoal(
                    category: category,
                    description: description,
                    targetDate: targetDate
                )

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
    AddGoalView(viewModel: GoalsViewModel())
}
