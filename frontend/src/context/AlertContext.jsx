import React, { createContext, useContext, useState } from 'react';

const AlertContext = createContext(null);

export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);

  const showAlert = (message, type = 'success') => {
    const id = Date.now();
    setAlerts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      hideAlert(id);
    }, 3000);
  };

  const hideAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  return (
    <AlertContext.Provider value={{ showAlert, hideAlert }}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {alerts.map(alert => (
          <div
            key={alert.id}
            className={`p-4 rounded-md shadow-lg ${
              alert.type === 'error' ? 'bg-red-500' : 'bg-green-500'
            } text-white`}
          >
            {alert.message}
          </div>
        ))}
      </div>
    </AlertContext.Provider>
  );
};

export const useAlert = () => {
  const context = useContext(AlertContext);
  if (context === null) {
    throw new Error('useAlert must be used within an AlertProvider');
  }
  return context;
};