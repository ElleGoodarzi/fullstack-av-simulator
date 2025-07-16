import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import axios from 'axios';
import App from './App';

jest.mock('axios');

test('renders upload form', () => {
  render(<App />);
  expect(screen.getByText(/AV Lane Detection Simulator/i)).toBeInTheDocument();
  expect(screen.getByText(/Process/i)).toBeInTheDocument();
});

test('handles file submit', async () => {
  render(<App />);
  const fileInput = screen.getByLabelText(/file/i);  // If no label, use getByRole('textbox', { type: 'file' })
  const button = screen.getByText(/Process/i);

  fireEvent.change(fileInput, { target: { files: [new File([''], 'test.jpg')] } });
  axios.post.mockResolvedValue({ data: { lane_position: 0.1, fps: 30, output_path: 'output.jpg' } });

  fireEvent.click(button);
  expect(axios.post).toHaveBeenCalledTimes(1);
});

test('matches snapshot', () => {
  const { asFragment } = render(<App />);
  expect(asFragment()).toMatchSnapshot();
});
