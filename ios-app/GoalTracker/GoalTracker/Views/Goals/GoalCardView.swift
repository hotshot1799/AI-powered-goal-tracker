//
//  GoalCardView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct GoalCardView: View {
    let goal: Goal

    private var progressColor: Color {
        if goal.progress >= 70 { return .green }
        if goal.progress >= 30 { return .orange }
        return .red
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header with category and progress
            HStack {
                Text(goal.category)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.2))
                    .foregroundColor(.blue)
                    .cornerRadius(8)

                Spacer()

                Text("\(Int(goal.progress))%")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(progressColor.opacity(0.2))
                    .foregroundColor(progressColor)
                    .cornerRadius(8)
            }

            // Description
            Text(goal.description)
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.primary)
                .lineLimit(2)

            // Progress Bar
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 8)
                        .cornerRadius(4)

                    Rectangle()
                        .fill(progressColor)
                        .frame(width: geometry.size.width * (goal.progress / 100), height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)

            // Target Date
            HStack {
                Image(systemName: "calendar")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Text("Target: \(goal.targetDate, style: .date)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemGroupedBackground))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 2)
    }
}

#Preview {
    GoalCardView(goal: Goal(
        id: 1,
        userId: 1,
        category: "Health",
        description: "Exercise 5 times a week",
        targetDate: Date(),
        progress: 65,
        createdAt: Date()
    ))
    .padding()
}
