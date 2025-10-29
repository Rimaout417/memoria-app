import { create } from 'zustand';
import { login as apiLogin, register as apiRegister, logout as apiLogout, isAuthenticated } from '../api/authApi';

interface AuthState {
  isAuthenticated: boolean;
  username: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: isAuthenticated(),
  username: localStorage.getItem('username'),
  isLoading: false,
  error: null,

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiLogin({ username, password });
      set({ 
        isAuthenticated: true, 
        username,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'ログインに失敗しました',
        isLoading: false 
      });
      throw error;
    }
  },

  register: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await apiRegister({ username, password });
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || '登録に失敗しました',
        isLoading: false 
      });
      throw error;
    }
  },

  logout: () => {
    apiLogout();
    set({ 
      isAuthenticated: false, 
      username: null 
    });
  },

  checkAuth: () => {
    const authenticated = isAuthenticated();
    const username = localStorage.getItem('username');
    set({ 
      isAuthenticated: authenticated,
      username 
    });
  },
}));
