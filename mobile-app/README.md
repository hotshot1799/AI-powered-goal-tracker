# Goal Tracker Mobile App (React Native/Expo)

A cross-platform mobile application for the AI-Powered Goal Tracker platform. Track your personal goals, monitor progress, and receive AI-powered suggestions to help you achieve your objectives.

## Features

- **User Authentication**: Secure login and registration with email verification
- **Goal Management**: Create, view, update, and delete personal goals
- **Progress Tracking**: Update and visualize goal progress with beautiful UI
- **AI Suggestions**: Receive personalized AI-powered recommendations
- **Cross-Platform**: Runs on iOS, Android, and Web
- **Modern UI**: Built with React Native and Expo for a native feel
- **Real-time Sync**: Syncs with backend API for cross-platform access

## Requirements

- **Node.js**: 16.x or later
- **npm** or **yarn**
- **Expo CLI**: For running the development server
- **Expo Go app** (optional): For testing on physical devices
- **Backend API**: The backend must be running

## Tech Stack

- **React Native**: Cross-platform mobile framework
- **Expo**: Development platform for React Native
- **React Navigation**: Navigation library
- **Axios**: HTTP client for API calls
- **AsyncStorage**: Local data persistence
- **Expo Vector Icons**: Icon library
- **Date-fns**: Date formatting and manipulation

## Project Structure

```
mobile-app/
├── src/
│   ├── components/       # Reusable components
│   │   └── GoalCard.js
│   ├── context/          # React Context for state management
│   │   └── AuthContext.js
│   ├── navigation/       # Navigation configuration
│   │   └── AppNavigator.js
│   ├── screens/          # Screen components
│   │   ├── Auth/
│   │   │   ├── LoginScreen.js
│   │   │   └── RegisterScreen.js
│   │   ├── Dashboard/
│   │   │   └── DashboardScreen.js
│   │   └── Goals/
│   │       ├── AddGoalScreen.js
│   │       └── GoalDetailScreen.js
│   ├── services/         # API service layer
│   │   └── api.js
│   └── utils/            # Utility functions
│       └── colors.js
├── App.js                # App entry point
├── app.json              # Expo configuration
├── package.json          # Dependencies
└── babel.config.js       # Babel configuration
```

## Getting Started

### 1. Install Dependencies

```bash
cd mobile-app
npm install
```

Or with yarn:
```bash
yarn install
```

### 2. Configure Backend URL

Open `src/services/api.js` and update the `API_URL`:

```javascript
const API_URL = 'https://your-backend-url.com/api/v1';
```

For local development:
```javascript
const API_URL = 'http://localhost:8000/api/v1';
```

**Note**: For Android emulator testing with local backend, use:
```javascript
const API_URL = 'http://10.0.2.2:8000/api/v1';
```

### 3. Start the Development Server

```bash
npm start
```

Or:
```bash
npx expo start
```

This will open the Expo Developer Tools in your browser.

### 4. Run on Your Device

#### Option 1: Expo Go App (Recommended for Testing)

1. Install **Expo Go** on your iOS or Android device
2. Scan the QR code shown in the terminal or browser
3. The app will load on your device

#### Option 2: iOS Simulator (macOS only)

```bash
npm run ios
```

#### Option 3: Android Emulator

```bash
npm run android
```

#### Option 4: Web Browser

```bash
npm run web
```

## Development

### File Organization

- **Screens**: Located in `src/screens/`, organized by feature
- **Components**: Reusable UI components in `src/components/`
- **Services**: API calls and external integrations in `src/services/`
- **Context**: Global state management in `src/context/`
- **Navigation**: App navigation structure in `src/navigation/`

### Key Files

#### `src/services/api.js`
Handles all API communication:
- Axios instance with interceptors
- Authentication token management
- API endpoint methods for auth, goals, and progress

#### `src/context/AuthContext.js`
Manages authentication state:
- User login/logout
- Token storage with AsyncStorage
- Authentication state across app

#### `src/navigation/AppNavigator.js`
Defines app navigation:
- Auth stack (Login, Register)
- App stack (Dashboard, Goal Details, Add Goal)
- Conditional rendering based on auth state

## API Integration

The app integrates with these backend endpoints:

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user

### Goals
- `GET /goals/user/{userId}` - Get all user goals
- `GET /goals/{goalId}` - Get specific goal
- `POST /goals/create` - Create new goal
- `PUT /goals/update` - Update goal
- `DELETE /goals/{goalId}` - Delete goal
- `GET /goals/suggestions/{userId}` - Get AI suggestions

### Progress
- `GET /progress/{goalId}` - Get progress history
- `POST /progress/{goalId}` - Add progress update

## Building for Production

### Android APK

1. Configure app.json with your app details
2. Build the APK:
   ```bash
   expo build:android
   ```

### iOS IPA (Requires Apple Developer Account)

1. Configure app.json with your app details
2. Build the IPA:
   ```bash
   expo build:ios
   ```

### Publish with EAS Build (Recommended)

1. Install EAS CLI:
   ```bash
   npm install -g eas-cli
   ```

2. Configure EAS:
   ```bash
   eas build:configure
   ```

3. Build for both platforms:
   ```bash
   eas build --platform all
   ```

## Common Issues & Solutions

### Issue: "Network request failed"

**Solution**:
- Check if backend is running
- Verify API_URL in `src/services/api.js`
- For Android emulator, use `10.0.2.2` instead of `localhost`
- Check firewall settings

### Issue: "Cannot connect to Metro bundler"

**Solution**:
- Clear cache: `npx expo start -c`
- Check if port 8081 is available
- Restart the development server

### Issue: "Invariant Violation: Module AppRegistry is not registered"

**Solution**:
- Clear watchman: `watchman watch-del-all`
- Clear node modules: `rm -rf node_modules && npm install`
- Clear cache: `npx expo start -c`

### Issue: AsyncStorage deprecation warning

**Solution**: Already using `@react-native-async-storage/async-storage` - the recommended package.

## Testing

### Manual Testing Checklist

- [ ] User can register with valid credentials
- [ ] User receives registration success message
- [ ] User can login with valid credentials
- [ ] Invalid login shows error message
- [ ] Dashboard displays user's goals
- [ ] User can create a new goal
- [ ] User can view goal details
- [ ] User can update goal progress
- [ ] User can delete a goal
- [ ] AI suggestions are displayed
- [ ] Pull-to-refresh works on dashboard
- [ ] User can logout

## Deployment Options

### 1. Expo Application Services (EAS)
- Easiest deployment option
- Build in the cloud
- Direct submission to app stores

### 2. Self-hosted Builds
- Build locally with Android Studio / Xcode
- More control over build process
- Requires more setup

### 3. Over-The-Air (OTA) Updates
```bash
expo publish
```
Push updates without rebuilding the app.

## Environment Variables

Create a `.env` file for environment-specific configuration:

```env
API_URL=https://your-api-url.com/api/v1
```

Then use with `expo-constants`:
```javascript
import Constants from 'expo-constants';
const API_URL = Constants.manifest.extra.apiUrl;
```

## Performance Tips

1. **Enable Hermes** (Android): Already configured in app.json
2. **Optimize Images**: Use appropriate image sizes
3. **Use FlatList**: For long scrollable lists (already implemented)
4. **Lazy Loading**: Load data as needed
5. **Minimize Re-renders**: Use React.memo for expensive components

## Debugging

### React Native Debugger

1. Install React Native Debugger
2. Start app with `npm start`
3. Press `Cmd+D` (iOS) or `Cmd+M` (Android)
4. Select "Debug"

### Console Logs

View logs in terminal:
```bash
npx expo start
# Then press 'j' to open debugger
```

### Network Requests

Use Reactotron or Flipper for debugging network calls.

## Contributing

When contributing to the mobile app:

1. Follow React Native best practices
2. Use functional components with hooks
3. Keep components small and focused
4. Write descriptive commit messages
5. Test on both iOS and Android
6. Update documentation

## Future Enhancements

- [ ] Push notifications for goal reminders
- [ ] Offline mode with local caching
- [ ] Dark mode support
- [ ] Biometric authentication
- [ ] Charts and analytics
- [ ] Goal sharing with friends
- [ ] Widget support
- [ ] Multiple languages

## Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Expo Icons](https://icons.expo.fyi/)

## Support

For issues or questions:
- Check the main project README
- Review API documentation
- Test backend endpoints independently
- Check Expo logs for detailed error messages

## License

This project is part of the AI-Powered Goal Tracker application.

## Version History

### v1.0.0 (Initial Release)
- User authentication (login/register)
- Goal CRUD operations
- Progress tracking with slider
- AI suggestions display
- Cross-platform support (iOS, Android, Web)
- Modern UI with gradient backgrounds
- Pull-to-refresh functionality
