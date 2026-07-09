import { create } from 'zustand';

interface User {
  email: string;
  name: string;
  role: string;
  orgId: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('autiguard_token') || null,
  user: JSON.parse(localStorage.getItem('autiguard_user') || 'null'),
  isAuthenticated: !!localStorage.getItem('autiguard_token'),
  login: (token, user) => {
    localStorage.setItem('autiguard_token', token);
    localStorage.setItem('autiguard_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('autiguard_token');
    localStorage.removeItem('autiguard_user');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
