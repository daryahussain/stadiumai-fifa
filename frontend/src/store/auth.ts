import { create } from "zustand"
import { persist } from "zustand/middleware"
import { loginUser, registerUser, getMe } from "@/lib/auth"

interface User {
  id: string
  email: string
  full_name: string
  role: string
}

interface AuthStore {
  token: string | null
  user: User | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const data = await loginUser(email, password)
          set({ token: data.access_token, isLoading: false })
          await get().loadUser()
        } catch (e) {
          set({ isLoading: false, error: (e as Error).message })
        }
      },

      register: async (email, password, fullName) => {
        set({ isLoading: true, error: null })
        try {
          const data = await registerUser(email, password, fullName)
          set({ token: data.access_token, isLoading: false })
          await get().loadUser()
        } catch (e) {
          set({ isLoading: false, error: (e as Error).message })
        }
      },

      logout: () => {
        set({ token: null, user: null })
      },

      loadUser: async () => {
        const { token } = get()
        if (!token) return
        try {
          const user = await getMe(token)
          set({ user })
        } catch {
          set({ token: null, user: null })
        }
      },
    }),
    { name: "stadium-auth", partialize: (state) => ({ token: state.token }) }
  )
)
