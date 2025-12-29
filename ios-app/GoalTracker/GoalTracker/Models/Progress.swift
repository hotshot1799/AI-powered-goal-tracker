//
//  Progress.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

struct Progress: Codable, Identifiable {
    let id: Int
    let goalId: Int
    let progressValue: Double
    let note: String?
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case goalId = "goal_id"
        case progressValue = "progress_value"
        case note
        case createdAt = "created_at"
    }
}

struct ProgressCreate: Codable {
    let progressValue: Double
    let note: String?

    enum CodingKeys: String, CodingKey {
        case progressValue = "progress_value"
        case note
    }
}

struct ProgressResponse: Codable {
    let success: Bool
    let progress: [Progress]
}
