//
//  GoalsViewModel.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

@MainActor
class GoalsViewModel: ObservableObject {
    @Published var goals: [Goal] = []
    @Published var suggestions: [String] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func fetchGoals() async {
        guard let userId = AuthManager.shared.getUserId() else {
            errorMessage = "User not logged in"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            goals = try await APIService.shared.getGoals(userId: userId)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func fetchSuggestions() async {
        guard let userId = AuthManager.shared.getUserId() else { return }

        do {
            suggestions = try await APIService.shared.getSuggestions(userId: userId)
        } catch {
            // Fallback suggestions
            suggestions = [
                "Start by creating your first goal",
                "Break down your goals into manageable tasks",
                "Track your progress regularly"
            ]
        }
    }

    func createGoal(category: String, description: String, targetDate: Date) async throws {
        guard let userId = AuthManager.shared.getUserId() else {
            throw APIError.unauthorized
        }

        let dateFormatter = ISO8601DateFormatter()
        let targetDateString = dateFormatter.string(from: targetDate)

        _ = try await APIService.shared.createGoal(
            userId: userId,
            category: category,
            description: description,
            targetDate: targetDateString
        )

        await fetchGoals()
    }

    func updateGoal(id: Int, category: String, description: String, targetDate: Date) async throws {
        let dateFormatter = ISO8601DateFormatter()
        let targetDateString = dateFormatter.string(from: targetDate)

        _ = try await APIService.shared.updateGoal(
            id: id,
            category: category,
            description: description,
            targetDate: targetDateString
        )

        await fetchGoals()
    }

    func deleteGoal(id: Int) async throws {
        _ = try await APIService.shared.deleteGoal(id: id)
        await fetchGoals()
    }
}
