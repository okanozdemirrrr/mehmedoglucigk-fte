import { create } from 'zustand';
import api from '../services/api';
import { registerFcmToken } from '../services/pushNotifications';

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('token') || null,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.post('accounts/login/', {
        email: email.trim().toLowerCase(),
        password,
      });
      const { token, user } = response.data;

      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));

      set({ user, token, isLoading: false });
      registerFcmToken().catch(() => {});
      return user;
    } catch (error) {
      set({ error: error.response?.data?.error || 'Giriş başarısız', isLoading: false });
      throw error;
    }
  },

  /** users tablosundan güncel kullanıcı bilgisini çeker */
  fetchCurrentUser: async () => {
    const token = get().token || localStorage.getItem('token');
    if (!token) return null;

    try {
      const response = await api.get('accounts/me/');
      const user = response.data;
      localStorage.setItem('user', JSON.stringify(user));
      set({ user });
      registerFcmToken().catch(() => {});
      return user;
    } catch {
      get().logout();
      return null;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ user: null, token: null });
  },

  registerPush: () => registerFcmToken().catch(() => {}),
}));

export default useAuthStore;
