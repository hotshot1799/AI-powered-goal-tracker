import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/loading.css'
import './styles/index.css'

// Logger configuration
const logger = {
  development: import.meta.env.MODE !== 'production',

  levels: {
    info: 'color: #2ecc71; font-weight: bold',
    warn: 'color: #f1c40f; font-weight: bold',
    error: 'color: #e74c3c; font-weight: bold',
    debug: 'color: #3498db; font-weight: bold',
  },

  info(message, data = null) {
    if (!this.development) return;
    console.log(`%c[INFO] ${new Date().toISOString()}`, this.levels.info, message, data || '');
  },

  warn(message, data = null) {
    if (!this.development) return;
    console.warn(`%c[WARN] ${new Date().toISOString()}`, this.levels.warn, message, data || '');
  },

  error(message, error = null) {
    if (!this.development) return;
    console.error(`%c[ERROR] ${new Date().toISOString()}`, this.levels.error, message, error || '');
  },

  debug(message, data = null) {
    if (!this.development) return;
    console.debug(`%c[DEBUG] ${new Date().toISOString()}`, this.levels.debug, message, data || '');
  },
};

// Make logger globally available
window.logger = logger;

// Log application startup
logger.info('Application starting...');

// Performance monitoring
const logPerformance = () => {
  if (!window.performance) return;
  const timing = window.performance.timing;

  window.addEventListener('load', () => {
    logger.info('Performance Metrics:', {
      'DNS Lookup': `${timing.domainLookupEnd - timing.domainLookupStart}ms`,
      'Server Connection': `${timing.connectEnd - timing.connectStart}ms`,
      'Server Response': `${timing.responseEnd - timing.requestStart}ms`,
      'DOM Processing': `${timing.domComplete - timing.domLoading}ms`,
      'Total Page Load': `${timing.loadEventEnd - timing.navigationStart}ms`,
    });
  });
};

// Error tracking
window.addEventListener('error', (event) => {
  logger.error('Global error:', {
    message: event.message,
    filename: event.filename,
    lineNumber: event.lineno,
    columnNumber: event.colno,
    error: event.error,
  });
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled Promise rejection:', {
    reason: event.reason,
    promise: event.promise,
  });
});

// Network request interceptor
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  const [url, options = {}] = args;
  logger.info(`API Request: ${options.method || 'GET'} ${url}`, options.body || '');

  try {
    const response = await originalFetch(...args);
    const clonedResponse = response.clone();

    // Log response
    try {
      const data = await clonedResponse.json();
      logger.info(`API Response: ${response.status} ${url}`, data);
    } catch {
      logger.info(`API Response: ${response.status} ${url}`, 'Non-JSON response');
    }

    return response;
  } catch (error) {
    logger.error(`Failed request to ${url}:`, error);
    throw error;
  }
};

// Initialize React application
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Start performance monitoring
logPerformance();

// Log successful mount
logger.info('React application mounted successfully');

// Development vs Production logging notice
if (import.meta.env.MODE === 'production') {
  logger.development = false;
  console.log('%cLogging disabled in production', 'color: #95a5a6');
} else {
  console.log('%cDevelopment mode: Full logging enabled', 'color: #2ecc71; font-weight: bold');
}