import { useState } from 'react'
import './App.css'

function App() {
  const [task, setTask] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [metrics, setMetrics] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!task.trim()) {
      setError('Please enter a research task')
      return
    }

    setLoading(true)
    setError(null)
    setMessages([])
    setMetrics(null)

    try {
      const response = await fetch(`${API_URL}/api/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to complete research')
      }

      setMessages(data.messages || [])
      setMetrics(data.metrics || null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AutoGen Research Assistant</h1>
        <p>Multi-agent AI research system powered by AutoGen</p>
      </header>

      <main className="main">
        <form onSubmit={handleSubmit} className="research-form">
          <div className="form-group">
            <label htmlFor="task">Research Task</label>
            <textarea
              id="task"
              value={task}
              onChange={(e) => setTask(e.target.value)}
              placeholder="Enter your research question or task here..."
              rows={4}
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? '🔄 Researching...' : '🚀 Start Research'}
          </button>
        </form>

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>AI agents are working on your research task...</p>
          </div>
        )}

        {messages.length > 0 && (
          <div className="results">
            <h2>Research Results</h2>
            <div className="messages">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message message-${msg.agent.toLowerCase()}`}>
                  <div className="message-header">
                    <strong>{msg.agent}</strong>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {metrics && (
          <div className="metrics">
            <h3>Performance Metrics</h3>
            <div className="metrics-grid">
              <div className="metric-card">
                <span className="metric-label">Total Tasks</span>
                <span className="metric-value">{metrics.total_tasks || 0}</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Successful</span>
                <span className="metric-value">{metrics.successful_tasks || 0}</span>
              </div>
              <div className="metric-card">
                <span className="metric-label">Avg Duration</span>
                <span className="metric-value">
                  {metrics.average_duration ? `${metrics.average_duration.toFixed(2)}s` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
