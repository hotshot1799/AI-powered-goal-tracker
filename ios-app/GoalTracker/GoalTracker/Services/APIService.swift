//
//  APIService.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

class APIService {
    static let shared = APIService()

    // Update this URL to match your backend deployment
    private let baseURL = "https://ai-powered-goal-tracker.onrender.com/api/v1"

    private let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()

    private let encoder: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()

    private init() {}

    // MARK: - Generic Request Method

    private func request<T: Decodable>(
        endpoint: String,
        method: String = "GET",
        body: Data? = nil,
        requiresAuth: Bool = true
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if requiresAuth, let token = AuthManager.shared.getToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = body
        }

        do {
            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }

            switch httpResponse.statusCode {
            case 200...299:
                return try decoder.decode(T.self, from: data)
            case 401:
                throw APIError.unauthorized
            case 404:
                throw APIError.notFound
            default:
                if let errorResponse = try? decoder.decode(ErrorResponse.self, from: data) {
                    throw APIError.serverError(errorResponse.detail)
                }
                throw APIError.serverError("Server error: \(httpResponse.statusCode)")
            }
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError.networkError(error)
        }
    }

    // MARK: - Authentication Endpoints

    func register(username: String, email: String, password: String) async throws -> RegisterResponse {
        let userCreate = UserCreate(username: username, email: email, password: password)
        let body = try encoder.encode(userCreate)
        return try await request(endpoint: "/auth/register", method: "POST", body: body, requiresAuth: false)
    }

    func login(username: String, password: String) async throws -> LoginResponse {
        let credentials = UserLogin(username: username, password: password)
        let body = try encoder.encode(credentials)
        return try await request(endpoint: "/auth/login", method: "POST", body: body, requiresAuth: false)
    }

    func logout() async throws -> APIResponse {
        return try await request(endpoint: "/auth/logout", method: "POST")
    }

    func getCurrentUser() async throws -> User {
        struct UserResponse: Codable {
            let success: Bool
            let user: User
        }
        let response: UserResponse = try await request(endpoint: "/auth/me", method: "GET")
        return response.user
    }

    // MARK: - Goals Endpoints

    func getGoals(userId: Int) async throws -> [Goal] {
        let response: GoalsResponse = try await request(endpoint: "/goals/user/\(userId)", method: "GET")
        return response.goals
    }

    func createGoal(userId: Int, category: String, description: String, targetDate: String) async throws -> Goal {
        let goalCreate = GoalCreate(userId: userId, category: category, description: description, targetDate: targetDate)
        let body = try encoder.encode(goalCreate)
        let response: GoalResponse = try await request(endpoint: "/goals/create", method: "POST", body: body)
        return response.goal
    }

    func updateGoal(id: Int, category: String, description: String, targetDate: String) async throws -> Goal {
        let goalUpdate = GoalUpdate(id: id, category: category, description: description, targetDate: targetDate)
        let body = try encoder.encode(goalUpdate)
        let response: GoalResponse = try await request(endpoint: "/goals/update", method: "PUT", body: body)
        return response.goal
    }

    func deleteGoal(id: Int) async throws -> APIResponse {
        return try await request(endpoint: "/goals/\(id)", method: "DELETE")
    }

    func getGoal(id: Int) async throws -> Goal {
        let response: GoalResponse = try await request(endpoint: "/goals/\(id)", method: "GET")
        return response.goal
    }

    func getSuggestions(userId: Int) async throws -> [String] {
        let response: SuggestionsResponse = try await request(endpoint: "/goals/suggestions/\(userId)", method: "GET")
        return response.suggestions
    }

    // MARK: - Progress Endpoints

    func getProgress(goalId: Int) async throws -> [Progress] {
        let response: ProgressResponse = try await request(endpoint: "/progress/\(goalId)", method: "GET")
        return response.progress
    }

    func addProgress(goalId: Int, progressValue: Double, note: String?) async throws -> APIResponse {
        let progressCreate = ProgressCreate(progressValue: progressValue, note: note)
        let body = try encoder.encode(progressCreate)
        return try await request(endpoint: "/progress/\(goalId)", method: "POST", body: body)
    }
}
