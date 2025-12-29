//
//  AuthManager.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

class AuthManager: ObservableObject {
    static let shared = AuthManager()

    @Published var isAuthenticated = false
    @Published var currentUser: User?

    private let tokenKey = "auth_token"
    private let userIdKey = "user_id"
    private let usernameKey = "username"

    private init() {
        // Check if user is already logged in
        if getToken() != nil {
            isAuthenticated = true
        }
    }

    // MARK: - Token Management

    func saveToken(_ token: String) {
        UserDefaults.standard.set(token, forKey: tokenKey)
        isAuthenticated = true
    }

    func getToken() -> String? {
        return UserDefaults.standard.string(forKey: tokenKey)
    }

    func removeToken() {
        UserDefaults.standard.removeObject(forKey: tokenKey)
        isAuthenticated = false
    }

    // MARK: - User Data Management

    func saveUserData(userId: Int, username: String) {
        UserDefaults.standard.set(userId, forKey: userIdKey)
        UserDefaults.standard.set(username, forKey: usernameKey)
    }

    func getUserId() -> Int? {
        let userId = UserDefaults.standard.integer(forKey: userIdKey)
        return userId == 0 ? nil : userId
    }

    func getUsername() -> String? {
        return UserDefaults.standard.string(forKey: usernameKey)
    }

    func clearUserData() {
        UserDefaults.standard.removeObject(forKey: userIdKey)
        UserDefaults.standard.removeObject(forKey: usernameKey)
    }

    // MARK: - Authentication Actions

    func login(username: String, password: String) async throws {
        let response = try await APIService.shared.login(username: username, password: password)

        if response.success {
            saveToken(response.token)
            saveUserData(userId: response.userId, username: response.username)

            await MainActor.run {
                isAuthenticated = true
            }
        } else {
            throw APIError.serverError("Login failed")
        }
    }

    func register(username: String, email: String, password: String) async throws {
        let response = try await APIService.shared.register(username: username, email: email, password: password)

        if !response.success {
            throw APIError.serverError(response.message ?? "Registration failed")
        }
    }

    func logout() async throws {
        _ = try await APIService.shared.logout()

        await MainActor.run {
            removeToken()
            clearUserData()
            currentUser = nil
            isAuthenticated = false
        }
    }

    func fetchCurrentUser() async throws {
        let user = try await APIService.shared.getCurrentUser()

        await MainActor.run {
            currentUser = user
        }
    }
}
