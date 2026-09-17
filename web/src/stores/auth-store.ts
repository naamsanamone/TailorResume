import { create } from 'zustand';
import { authAPI } from '@/lib/api';
import { setToken, removeToken, getToken } from '@/lib/auth';

interface User {
  id: number;
  email: string;
  name: string | null;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const { data } = await authAPI.login({ email, password });
    setToken(data.access_token);
    set({ user: data.user, isAuthenticated: true });
  },

  register: async (email: string, password: string, name?: string) => {
    const { data } = await authAPI.register({ email, password, name });
    setToken(data.access_token);
    set({ user: data.user, isAuthenticated: true });
  },

  logout: () => {
    removeToken();
    set({ user: null, isAuthenticated: false });
  },

  loadUser: async () => {
    const token = getToken();
    if (!token) {
      set({ isLoading: false });
      return;
    }
    try {
      const { data } = await authAPI.me();
      set({ user: data, isAuthenticated: true, isLoading: false });
    } catch {
      removeToken();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
