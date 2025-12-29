//
//  RegisterView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct RegisterView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var authManager = AuthManager.shared
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var successMessage: String?

    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 20) {
                        VStack(spacing: 10) {
                            Image(systemName: "person.badge.plus")
                                .font(.system(size: 60))
                                .foregroundColor(.white)

                            Text("Create Account")
                                .font(.largeTitle)
                                .fontWeight(.bold)
                                .foregroundColor(.white)
                        }
                        .padding(.top, 40)
                        .padding(.bottom, 20)

                        VStack(spacing: 16) {
                            TextField("Username", text: $username)
                                .textFieldStyle(RoundedTextFieldStyle())
                                .autocapitalization(.none)

                            TextField("Email", text: $email)
                                .textFieldStyle(RoundedTextFieldStyle())
                                .autocapitalization(.none)
                                .keyboardType(.emailAddress)

                            SecureField("Password", text: $password)
                                .textFieldStyle(RoundedTextFieldStyle())

                            SecureField("Confirm Password", text: $confirmPassword)
                                .textFieldStyle(RoundedTextFieldStyle())

                            if let errorMessage = errorMessage {
                                Text(errorMessage)
                                    .font(.caption)
                                    .foregroundColor(.red)
                                    .padding(.horizontal)
                            }

                            if let successMessage = successMessage {
                                Text(successMessage)
                                    .font(.caption)
                                    .foregroundColor(.green)
                                    .padding(.horizontal)
                            }

                            Button(action: register) {
                                if isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Text("Register")
                                        .fontWeight(.semibold)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                            .disabled(isLoading)

                            Button(action: { dismiss() }) {
                                Text("Already have an account? Login")
                                    .font(.subheadline)
                                    .foregroundColor(.white)
                            }
                        }
                        .padding(.horizontal, 40)
                    }
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
            }
        }
    }

    private func register() {
        errorMessage = nil
        successMessage = nil

        guard !username.isEmpty, !email.isEmpty, !password.isEmpty else {
            errorMessage = "Please fill in all fields"
            return
        }

        guard password == confirmPassword else {
            errorMessage = "Passwords do not match"
            return
        }

        guard password.count >= 6 else {
            errorMessage = "Password must be at least 6 characters"
            return
        }

        isLoading = true

        Task {
            do {
                try await authManager.register(username: username, email: email, password: password)
                await MainActor.run {
                    successMessage = "Registration successful! Please check your email to verify your account."
                    isLoading = false

                    // Dismiss after 2 seconds
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        dismiss()
                    }
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
    RegisterView()
}
