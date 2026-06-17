import api from './api';

export const getDashboard = (dateFilter = 'this_month') =>
  api.get(`finance/analytics/dashboard/?date_filter=${dateFilter}`).then((res) => res.data);
