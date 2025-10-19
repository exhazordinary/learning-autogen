import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { formatDistanceToNow } from 'date-fns'
import useStore from './store'
import './App.css'

function App() {
  const [taskInput, setTaskInput] = useState('')
  const [messages, setMessages] = useState([])
  const [taskId, setTaskId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [history, setHistory] = useState([])

  const {
    theme,
    setTheme,
    loading,
    setLoading,
    error,
    setError,
    clearError,
    socket,
    setSocket,
    connected,
    setConnected
  } = useStore()

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

  // Initialize WebSocket connection
  useEffect(() => {
    const newSocket = io(API_URL)

    newSocket.on('connect', () => {
      console.log('Connected to server')
      setConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server')
      setConnected(false)
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [API_URL, setConnected, setSocket])

  // Set up message listeners when taskId changes
  useEffect(() => {
    if (!socket || !taskId) return

    const handleTaskUpdate = (data) => {
      console.log('Task update:', data)
      if (data.task_id === taskId) {
        setProgress(data.progress)
      }
    }

    const handleAgentMessage = (data) => {
      console.log('Agent message received:', data)
      if (data.task_id === taskId) {
        // Append new message in real-time
        setMessages(prev => [...prev, {
          agent: data.agent,
          content: data.content,
          order: data.order
        }])
      }
    }

    socket.on('task_update', handleTaskUpdate)
    socket.on('agent_message', handleAgentMessage)

    return () => {
      socket.off('task_update', handleTaskUpdate)
      socket.off('agent_message', handleAgentMessage)
    }
  }, [socket, taskId])

  // Load history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('researchHistory')
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory))
    }
  }, [])

  // Save history to localStorage
  useEffect(() => {
    localStorage.setItem('researchHistory', JSON.stringify(history))
  }, [history])

  // Apply theme
  useEffect(() => {
    document.body.className = theme
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!taskInput.trim()) {
      setError('Please enter a research task')
      return
    }

    setLoading(true)
    clearError()
    setMessages([])
    setProgress(null)

    try {
      const response = await fetch(`${API_URL}/api/v1/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task: taskInput }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to start research')
      }

      const newTaskId = data.task_id
      setTaskId(newTaskId)

      // Subscribe to task updates
      if (socket && connected) {
        socket.emit('subscribe_task', { task_id: newTaskId })
      }

      // Poll for task completion
      pollTaskStatus(newTaskId)

    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const pollTaskStatus = async (id) => {
    const maxAttempts = 120 // 10 minutes with 5s intervals
    let attempts = 0

    const poll = async () => {
      try {
        const response = await fetch(`${API_URL}/api/v1/research/${id}/status`)
        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch status')
        }

        if (data.celery_status === 'PROCESSING' && data.meta) {
          setProgress(data.meta)
        }

        if (data.status === 'completed') {
          // Fetch full task details
          const taskResponse = await fetch(`${API_URL}/api/v1/research/${id}`)
          const taskData = await taskResponse.json()

          if (taskData.success) {
            setMessages(taskData.task.messages || [])

            // Add to history
            const historyItem = {
              id,
              task: taskInput,
              timestamp: new Date().toISOString(),
              status: 'completed'
            }
            setHistory(prev => [historyItem, ...prev].slice(0, 20))
          }

          setLoading(false)
          return
        }

        if (data.status === 'failed') {
          setError(data.error || 'Task failed')
          setLoading(false)
          return
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000) // Poll every 5 seconds
        } else {
          setError('Task timed out')
          setLoading(false)
        }

      } catch (err) {
        setError(err.message)
        setLoading(false)
      }
    }

    poll()
  }

  const loadHistoryItem = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/research/${id}`)
      const data = await response.json()

      if (data.success) {
        setMessages(data.task.messages || [])
        setTaskInput(data.task.task)
        setTaskId(id)
      }
    } catch {
      setError('Failed to load history item')
    }
  }

  const exportToMarkdown = async () => {
    if (!taskId) return

    try {
      const response = await fetch(`${API_URL}/api/v1/research/${taskId}/export`)
      const data = await response.json()

      if (data.success) {
        const blob = new Blob([data.markdown], { type: 'text/markdown' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `research_${taskId}.md`
        a.click()
        URL.revokeObjectURL(url)
      }
    } catch {
      setError('Failed to export')
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => alert('Copied to clipboard!'))
      .catch(() => setError('Failed to copy'))
  }

  return (
    <div className={`app ${theme}`}>
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🤖 AutoGen Research Assistant</h1>
            <p>Multi-agent AI research system powered by AutoGen</p>
          </div>
          <div className="header-actions">
            <button onClick={toggleTheme} className="theme-toggle" title="Toggle theme">
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
            {connected ? (
              <span className="connection-status connected">● Connected</span>
            ) : (
              <span className="connection-status disconnected">● Disconnected</span>
            )}
          </div>
        </div>
      </header>

      <div className="layout">
        <aside className="sidebar">
          <h3>Research History</h3>
          {history.length === 0 ? (
            <p className="empty-history">No history yet</p>
          ) : (
            <div className="history-list">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => loadHistoryItem(item.id)}
                >
                  <div className="history-task">{item.task.slice(0, 50)}...</div>
                  <div className="history-time">
                    {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                  </div>
                </div>
              ))}
            </div>
          )}
          {history.length > 0 && (
            <button
              onClick={() => setHistory([])}
              className="clear-history-btn"
            >
              Clear History
            </button>
          )}
        </aside>

        <main className="main">
          <form onSubmit={handleSubmit} className="research-form">
            <div className="form-group">
              <label htmlFor="task">Research Task</label>
              <textarea
                id="task"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
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
              <button onClick={clearError} className="close-btn">×</button>
            </div>
          )}

          {loading && (
            <div className="loading-box">
              <div className="spinner"></div>
              <p>
                {progress ? progress.status : 'AI agents are working on your research task...'}
              </p>
              {progress && progress.progress && (
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${progress.progress}%` }}
                  />
                </div>
              )}
            </div>
          )}

          {messages.length > 0 && (
            <div className="results">
              <div className="results-header">
                <h2>Research Results</h2>
                <div className="results-actions">
                  <button onClick={exportToMarkdown} className="action-btn">
                    📥 Export
                  </button>
                  <button
                    onClick={() => copyToClipboard(
                      messages.map(m => `${m.agent}:\n${m.content}`).join('\n\n')
                    )}
                    className="action-btn"
                  >
                    📋 Copy
                  </button>
                </div>
              </div>
              <div className="messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message message-${msg.agent.toLowerCase()}`}>
                    <div className="message-header">
                      <strong>{msg.agent}</strong>
                      <button
                        onClick={() => copyToClipboard(msg.content)}
                        className="copy-message-btn"
                        title="Copy message"
                      >
                        📋
                      </button>
                    </div>
                    <div className="message-content">
                      <ReactMarkdown
                        components={{
                          code({ inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '')
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={theme === 'dark' ? vscDarkPlus : vs}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            )
                          }
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
