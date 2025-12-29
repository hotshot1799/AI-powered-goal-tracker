//
//  APIResponse.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import Foundation

struct APIResponse: Codable {
    let success: Bool
    let message: String?
    let detail: String?
}

struct ErrorResponse: Codable {
    let success: Bool
    let detail: String
}

enum APIError: Error, LocalizedError {
    case invalidURL
    case invalidResponse
    case networkError(Error)
    case decodingError(Error)
    case serverError(String)
    case unauthorized
    case notFound

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .invalidResponse:
            return "Invalid response from server"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .decodingError(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .serverError(let message):
            return message
        case .unauthorized:
            return "Unauthorized. Please login again."
        case .notFound:
            return "Resource not found"
        }
    }
}
