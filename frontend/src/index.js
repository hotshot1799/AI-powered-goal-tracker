import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/loading.css';
import './styles/index.css';

// Logger configuration
const logger = {
  development: true, // Toggle based on environment
  
  // Log levels with corresponding styles
  levels: {
    info: 'color: #2ecc71; font-weight: bold',
    warn: 'color: #f1c40f; font-weight: bold',
    error: 'color: #e74c3c; font-weight: bold',
    debug: 'color: #3498db; font-weight: bold'
  },

  // Logging methods
  info: function(message, data = null) {
    if (!this.development) return;
    if (data) {
      console.log(`%c[INFO] ${new Date().toISOString()}`, this.levels.info, message, data);
    } else {
      console.log(`%c[INFO] ${new Date().toISOString()}`, this.levels.info, message);
    }
  },

  warn: function(message, data = null) {
    if (!this.development) return;
    if (data) {
      console.warn(`%c[WARN] ${new Date().toISOString()}`, this.levels.warn, message, data);
    } else {
      console.warn(`%c[WARN] ${new Date().toISOString()}`, this.levels.warn, message);
    }
  },

  error: function(message, error = null) {
    if (!this.development) return;
    if (error) {
      console.error(`%c[ERROR] ${new Date().toISOString()}`, this.levels.error, message, error);
    } else {
      console.error(`%c[ERROR] ${new Date().toISOString()}`, this.levels.error, message);
    }
  },

  debug: function(message, data = null) {
    if (!this.development) return;
    if (data) {
      console.debug(`%c[DEBUG] ${new Date().toISOString()}`, this.levels.debug, message, data);
    } else {
      console.debug(`%c[DEBUG] ${new Date().toISOString()}`, this.levels.debug, message);
    }
  },

  // Network request logging
  logRequest: function(url, method, data = null) {
    this.info(`🌐 API Request: ${method} ${url}`, data);
  },

  logResponse: function(url, status, data = null) {
    if (status >= 200 && status < 300) {
      this.info(`✅ API Response: ${status} ${url}`, data);
    } else {
      this.error(`❌ API Response: ${status} ${url}`, data);
    }
  }
};

// Make logger globally available
window.logger = logger;

// Log application startup
logger.info('Application starting...');

// Performance monitoring
const logPerformance = () => {
  if (window.performance) {
    const timing = window.performance.timing;
    const navigationStart = timing.navigationStart;

    window.addEventListener('load', () => {
      logger.info('Performance Metrics:', {
        'DNS Lookup': timing.domainLookupEnd - timing.domainLookupStart + 'ms',
        'Server Connection': timing.connectEnd - timing.connectStart + 'ms',
        'Server Response': timing.responseEnd - timing.requestStart + 'ms',
        'DOM Processing': timing.domComplete - timing.domLoading + 'ms',
        'Total Page Load': timing.loadEventEnd - navigationStart + 'ms'
      });
    });
  }
};

// Error tracking
window.addEventListener('error', (event) => {
  logger.error('Global error:', {
    message: event.message,
    filename: event.filename,
    lineNumber: event.lineno,
    columnNumber: event.colno,
    error: event.error
  });
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled Promise rejection:', {
    reason: event.reason,
    promise: event.promise
  });
});

// Network request interceptor
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  const [url, options = {}] = args;
  logger.logRequest(url, options.method || 'GET', options.body);
  
  try {
    const response = await originalFetch(...args);
    const clonedResponse = response.clone();
    
    // Log response
    try {
      const data = await clonedResponse.json();
      logger.logResponse(url, response.status, data);
    } catch (e) {
      logger.logResponse(url, response.status, 'Non-JSON response');
    }
    
    return response;
  } catch (error) {
    logger.error(`Failed request to ${url}:`, error);
    throw error;
  }
};

// Initialize React application
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Start performance monitoring
logPerformance();

// Log successful mount
logger.info('React application mounted successfully');

// Development vs Production logging notice
if (process.env.NODE_ENV === 'production') {
  logger.development = false;
  console.log('%cLogging disabled in production', 'color: #95a5a6');
} else {
  console.log('%cDevelopment mode: Full logging enabled', 'color: #2ecc71; font-weight: bold');
}
