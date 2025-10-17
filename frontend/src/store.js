import { create } from 'zustand'

const useStore = create((set) => ({
  // Theme
  theme: localStorage.getItem('theme') || 'light',
  setTheme: (theme) => {
    localStorage.setItem('theme', theme)
    set({ theme })
  },

  // Current task
  currentTask: null,
  setCurrentTask: (task) => set({ currentTask: task }),

  // Task history
  taskHistory: [],
  addTaskToHistory: (task) =>
    set((state) => ({
      taskHistory: [task, ...state.taskHistory].slice(0, 20)
    })),
  clearTaskHistory: () => set({ taskHistory: [] }),

  // Loading state
  loading: false,
  setLoading: (loading) => set({ loading }),

  // Error state
  error: null,
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // WebSocket connection
  socket: null,
  setSocket: (socket) => set({ socket }),
  connected: false,
  setConnected: (connected) => set({ connected }),
}))

export default useStore
