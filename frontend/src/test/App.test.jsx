import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    close: vi.fn(),
  })),
}))

// Mock fetch
globalThis.fetch = vi.fn()

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('renders the app header', () => {
    render(<App />)
    expect(screen.getByText(/AutoGen Research Assistant/i)).toBeInTheDocument()
  })

  it('renders the research task form', () => {
    render(<App />)
    expect(screen.getByLabelText(/Research Task/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Start Research/i })).toBeInTheDocument()
  })

  it('shows theme toggle button', () => {
    render(<App />)
    const themeToggle = screen.getByTitle(/Toggle theme/i)
    expect(themeToggle).toBeInTheDocument()
  })

  it('shows connection status', () => {
    render(<App />)
    expect(screen.getByText(/Disconnected|Connected/i)).toBeInTheDocument()
  })

  it('allows user to type in textarea', async () => {
    const user = userEvent.setup()
    render(<App />)

    const textarea = screen.getByLabelText(/Research Task/i)
    await user.type(textarea, 'Test research query')

    expect(textarea.value).toBe('Test research query')
  })

  it('shows error when submitting empty task', async () => {
    const user = userEvent.setup()
    render(<App />)

    const submitButton = screen.getByRole('button', { name: /Start Research/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/Please enter a research task/i)).toBeInTheDocument()
    })
  })

  it('renders history section', () => {
    render(<App />)
    expect(screen.getByText(/Research History/i)).toBeInTheDocument()
    expect(screen.getByText(/No history yet/i)).toBeInTheDocument()
  })
})
