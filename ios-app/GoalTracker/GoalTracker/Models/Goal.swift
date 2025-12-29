//
//  Goal.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

struct Goal: Codable, Identifiable {
    let id: Int
    let userId: Int
    let category: String
    let description: String
    let targetDate: Date
    let progress: Double
    let createdAt: Date?

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case category
        case description
        case targetDate = "target_date"
        case progress
        case createdAt = "created_at"
    }
}

struct GoalCreate: Codable {
    let userId: Int
    let category: String
    let description: String
    let targetDate: String

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case category
        case description
        case targetDate = "target_date"
    }
}

struct GoalUpdate: Codable {
    let id: Int
    let category: String
    let description: String
    let targetDate: String

    enum CodingKeys: String, CodingKey {
        case id
        case category
        case description
        case targetDate = "target_date"
    }
}

struct GoalsResponse: Codable {
    let success: Bool
    let goals: [Goal]
}

struct GoalResponse: Codable {
    let success: Bool
    let goal: Goal
}

struct SuggestionsResponse: Codable {
    let success: Bool
    let suggestions: [String]
}
