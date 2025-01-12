import React from 'react';
import { Link } from 'react-router-dom';

export const BoxContainer = ({ children, className = '' }) => (
  <div className={`w-full flex flex-col items-center mt-2.5 ${className}`}>
    {children}
  </div>
);

export const FormContainer = ({ children, className = '', ...props }) => (
  <form className={`w-full flex flex-col ${className}`} {...props}>
    {children}
  </form>
);

export const MutedLink = ({ children, className = '', href, ...props }) => (
  <Link 
    to={href} 
    className={`text-xs text-gray-400 font-medium no-underline border-b border-dashed border-gray-400 ${className}`}
    {...props}
  >
    {children}
  </Link>
);

export const BoldLink = ({ children, className = '', href, ...props }) => (
  <Link 
    to={href} 
    className={`text-xs text-yellow-500 font-medium no-underline border-b border-dashed border-yellow-500 ${className}`}
    {...props}
  >
    {children}
  </Link>
);

export const Input = React.forwardRef(({ className = '', ...props }, ref) => (
  <input
    ref={ref}
    className={`w-full h-[42px] border border-gray-300 rounded-md px-2.5 transition-all duration-200 ease-in-out mb-1.5 outline-none focus:border-yellow-500 placeholder:text-gray-400 ${className}`}
    {...props}
  />
));
Input.displayName = 'Input';

export const SubmitButton = ({ children, className = '', disabled, ...props }) => (
  <button
    className={`w-full max-w-[150px] px-2.5 py-2.5 text-white text-sm font-semibold border-none rounded-full cursor-pointer transition-all duration-200 ease-in-out bg-gradient-to-r from-yellow-500 to-yellow-400 hover:brightness-105 disabled:opacity-70 disabled:cursor-not-allowed ${className}`}
    disabled={disabled}
    {...props}
  >
    {children}
  </button>
);

export const LineText = ({ children, className = '' }) => (
  <p className={`text-xs text-gray-400 font-medium ${className}`}>
    {children}
  </p>
);