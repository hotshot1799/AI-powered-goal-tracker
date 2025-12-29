# Goal Tracker iOS App

An iOS mobile application for the AI-Powered Goal Tracker platform. Track your personal goals, monitor progress, and receive AI-powered suggestions to help you achieve your objectives.

## Features

- **User Authentication**: Secure login and registration with email verification
- **Goal Management**: Create, view, update, and delete personal goals
- **Progress Tracking**: Update and visualize goal progress with detailed metrics
- **AI Suggestions**: Receive personalized AI-powered recommendations
- **Beautiful UI**: Modern SwiftUI interface with smooth animations
- **Real-time Sync**: Syncs with backend API for cross-platform access

## Requirements

- **Xcode**: 15.0 or later
- **iOS**: 16.0 or later
- **Swift**: 5.9 or later
- **Backend API**: The backend must be running (see main README)

## Project Structure

```
GoalTracker/
├── GoalTracker/
│   ├── Models/              # Data models (User, Goal, Progress)
│   ├── Services/            # API service and authentication manager
│   ├── ViewModels/          # Business logic layer
│   ├── Views/               # SwiftUI views
│   │   ├── Auth/           # Login and registration views
│   │   ├── Dashboard/      # Main dashboard
│   │   └── Goals/          # Goal management views
│   ├── Utilities/          # Helper functions and extensions
│   ├── Resources/          # Assets and configuration files
│   ├── GoalTrackerApp.swift
│   └── ContentView.swift
└── GoalTracker.xcodeproj
```

## Setup Instructions

### 1. Prerequisites

Ensure you have:
- A Mac with macOS 13.0 or later
- Xcode 15.0 or later installed from the Mac App Store
- An active Apple Developer account (for device deployment)

### 2. Configure Backend URL

Open `GoalTracker/Services/APIService.swift` and update the `baseURL` to point to your backend:

```swift
private let baseURL = "https://your-backend-url.com/api/v1"
```

For local development:
```swift
private let baseURL = "http://localhost:8000/api/v1"
```

### 3. Open the Project

```bash
cd ios-app/GoalTracker
open GoalTracker.xcodeproj
```

### 4. Build and Run

1. Select a simulator or connected device from the device menu
2. Press `Cmd + R` or click the Play button to build and run
3. The app will launch on your selected device/simulator

### 5. Testing

Create a test account:
1. Tap "Don't have an account? Register"
2. Fill in username, email, and password
3. Check your email for verification (if email service is configured)
4. Login with your credentials

## Architecture

### MVVM Pattern

The app follows the Model-View-ViewModel (MVVM) architecture:

- **Models**: Define data structures (`User`, `Goal`, `Progress`)
- **Views**: SwiftUI views for UI presentation
- **ViewModels**: Handle business logic and state management
- **Services**: Network layer and authentication management

### Key Components

#### 1. APIService
Handles all network requests to the backend API:
- Generic request method with error handling
- Authentication endpoints (login, register, logout)
- Goal management endpoints
- Progress tracking endpoints

#### 2. AuthManager
Manages user authentication state:
- Token storage and retrieval
- User session management
- Login/logout functionality
- Observable for reactive UI updates

#### 3. GoalsViewModel
Manages goal-related state and operations:
- Fetch and display goals
- Create, update, delete goals
- Fetch AI suggestions
- Handle loading and error states

## API Integration

The app integrates with the following backend endpoints:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Goals
- `GET /goals/user/{userId}` - Get all goals for user
- `POST /goals/create` - Create new goal
- `PUT /goals/update` - Update existing goal
- `DELETE /goals/{goalId}` - Delete goal
- `GET /goals/{goalId}` - Get specific goal
- `GET /goals/suggestions/{userId}` - Get AI suggestions

### Progress
- `GET /progress/{goalId}` - Get progress history
- `POST /progress/{goalId}` - Add progress update

## Security Features

- **Secure Token Storage**: JWT tokens stored in UserDefaults
- **HTTPS Only**: App Transport Security enabled
- **Bearer Token Authentication**: All authenticated requests include Bearer token
- **Input Validation**: Client-side validation for forms
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Development Tips

### Running on Simulator

The iOS Simulator allows testing without a physical device:
```bash
# List available simulators
xcrun simctl list devices

# Boot a specific simulator
xcrun simctl boot "iPhone 15 Pro"

# Run app
xcodebuild -scheme GoalTracker -destination 'platform=iOS Simulator,name=iPhone 15 Pro'
```

### Debugging

- Use `print()` statements for console logging
- Set breakpoints in Xcode for step-through debugging
- View network requests in the Console app (macOS)
- Use Xcode's Memory Graph Debugger for memory issues

### Common Issues

**1. "Failed to connect to backend"**
- Verify backend URL in `APIService.swift`
- Ensure backend is running
- Check network connectivity

**2. "Invalid token" errors**
- Clear app data and login again
- Verify SECRET_KEY matches backend

**3. "Build failed" in Xcode**
- Clean build folder: `Cmd + Shift + K`
- Delete Derived Data
- Restart Xcode

## SwiftUI Views

### LoginView
- Email/password authentication
- Form validation
- Navigation to registration
- Error handling

### RegisterView
- User registration form
- Email verification notification
- Password confirmation
- Success/error messaging

### DashboardView
- Goal list display
- AI suggestions card
- Pull-to-refresh
- Navigation to goal details

### GoalDetailView
- Goal information display
- Progress visualization
- Update progress functionality
- Delete goal option

### AddGoalView
- Create new goals
- Category selection
- Date picker for target date
- Form validation

## Future Enhancements

- [ ] Offline mode with local caching
- [ ] Push notifications for goal reminders
- [ ] Charts and analytics for progress visualization
- [ ] Share goals with friends
- [ ] Widget support for iOS home screen
- [ ] Apple Watch companion app
- [ ] Dark mode support (manual toggle)
- [ ] Localization for multiple languages

## Contributing

When contributing to the iOS app:

1. Follow Swift style guidelines
2. Use SwiftUI best practices
3. Write descriptive commit messages
4. Test on multiple device sizes
5. Ensure backwards compatibility with iOS 16.0

## License

This project is part of the AI-Powered Goal Tracker application.

## Support

For issues or questions:
- Check the main project README
- Review API documentation
- Test backend endpoints independently
- Check Xcode console for detailed error messages

## Version History

### v1.0.0 (Initial Release)
- User authentication
- Goal CRUD operations
- Progress tracking
- AI suggestions
- SwiftUI interface
