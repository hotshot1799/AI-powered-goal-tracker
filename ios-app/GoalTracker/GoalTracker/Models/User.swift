//
//  User.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String
    let isVerified: Bool
    let createdAt: Date?

    enum CodingKeys: String, CodingKey {
        case id
        case username
        case email
        case isVerified = "is_verified"
        case createdAt = "created_at"
    }
}

struct UserCreate: Codable {
    let username: String
    let email: String
    let password: String
}

struct UserLogin: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let success: Bool
    let token: String
    let userId: Int
    let username: String

    enum CodingKeys: String, CodingKey {
        case success
        case token
        case userId = "user_id"
        case username
    }
}

struct RegisterResponse: Codable {
    let success: Bool
    let message: String
}
