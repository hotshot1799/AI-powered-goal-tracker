//
//  LoginView.swift
//  GoalTracker
//
//  AI-Powered Goal Tracker - iOS Application
//

import SwiftUI

struct LoginView: View {
    @StateObject private var authManager = AuthManager.shared
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var showRegister = false

    var body: some View {
        NavigationView {
            ZStack {
                // Gradient Background
                LinearGradient(
                    gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.purple.opacity(0.6)]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(spacing: 20) {
                    // Logo/Title
                    VStack(spacing: 10) {
                        Image(systemName: "target")
                            .font(.system(size: 80))
                            .foregroundColor(.white)

                        Text("Goal Tracker")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.white)

                        Text("Track your goals with AI")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.9))
                    }
                    .padding(.bottom, 40)

                    // Login Form
                    VStack(spacing: 16) {
                        TextField("Username", text: $username)
                            .textFieldStyle(RoundedTextFieldStyle())
                            .autocapitalization(.none)

                        SecureField("Password", text: $password)
                            .textFieldStyle(RoundedTextFieldStyle())

                        if let errorMessage = errorMessage {
                            Text(errorMessage)
                                .font(.caption)
                                .foregroundColor(.red)
                                .padding(.horizontal)
                        }

                        Button(action: login) {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("Login")
                                    .fontWeight(.semibold)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                        .disabled(isLoading)

                        Button(action: { showRegister = true }) {
                            Text("Don't have an account? Register")
                                .font(.subheadline)
                                .foregroundColor(.white)
                        }
                    }
                    .padding(.horizontal, 40)

                    Spacer()
                }
                .padding(.top, 60)
            }
            .sheet(isPresented: $showRegister) {
                RegisterView()
            }
        }
    }

    private func login() {
        guard !username.isEmpty, !password.isEmpty else {
            errorMessage = "Please enter username and password"
            return
        }

        isLoading = true
        errorMessage = nil

        Task {
            do {
                try await authManager.login(username: username, password: password)
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}

struct RoundedTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding()
            .background(Color.white)
            .cornerRadius(10)
            .shadow(radius: 2)
    }
}

#Preview {
    LoginView()
}
