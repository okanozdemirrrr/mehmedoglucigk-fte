import { create } from 'zustand';
import { getDashboard } from '../services/analyticsApi';

const EMPTY_ANALYTICS = {
  kpis: {
    total_revenue: '0',
    order_count: 0,
    pending_orders: 0,
    total_collection: '0',
    total_receivables: '0',
  },
  revenue_trend: [],
  recent_activity: [],
  date_from: '—',
  date_to: '—',
};

const useAnalyticsStore = create((set) => ({
  analytics: null,
  isLoading: false,
  error: null,

  fetchDashboard: async (dateFilter = 'this_month') => {
    set({ isLoading: true, error: null });
    try {
      const data = await getDashboard(dateFilter);
      set({ analytics: data, isLoading: false, error: null });
      return data;
    } catch (err) {
      set({
        analytics: EMPTY_ANALYTICS,
        isLoading: false,
        error: err.response?.data?.detail || 'Finansal özet verileri yüklenemedi.',
      });
      throw err;
    }
  },
}));

export default useAnalyticsStore;
