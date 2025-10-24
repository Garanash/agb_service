import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock the API service
jest.mock('../services/api', () => ({
  apiService: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);
    // Basic test to ensure the app renders
    expect(document.body).toBeInTheDocument();
  });

  test('has basic structure', () => {
    render(<App />);
    // Test that the app has some basic structure
    const appElement = document.querySelector('.App');
    expect(appElement).toBeInTheDocument();
  });
});

// Simple test to ensure Jest is working
describe('Basic Tests', () => {
  test('should pass basic assertion', () => {
    expect(1 + 1).toBe(2);
  });

  test('should handle strings', () => {
    const greeting = 'Hello, World!';
    expect(greeting).toContain('Hello');
  });
});