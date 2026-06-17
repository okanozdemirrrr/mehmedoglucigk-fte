import api from './api';

const unwrapList = (res) => (res.data.results ? res.data.results : res.data);

export { getDashboard as getAnalyticsDashboard } from './analyticsApi';

export const getDealers = () =>
  api.get('accounts/dealers/').then((res) => unwrapList(res));

export const getDealer = (id) =>
  api.get(`accounts/dealers/${id}/`).then((res) => res.data);

export const getDealerPrices = (dealerId) =>
  api.get(`products/dealer-prices/?dealer=${dealerId}`).then((res) => unwrapList(res));

export const createDealerPrice = (payload) =>
  api.post('products/dealer-prices/', payload).then((res) => res.data);

export const updateDealerPrice = (id, payload) =>
  api.patch(`products/dealer-prices/${id}/`, payload).then((res) => res.data);

export const deleteDealerPrice = (id) =>
  api.delete(`products/dealer-prices/${id}/`);

export const getCatalog = () =>
  api.get('products/products/catalog/').then((res) => unwrapList(res));

export const getProducts = () =>
  api.get('products/products/').then((res) => unwrapList(res));

export const getCariBalance = () =>
  api.get('finance/cari/balance/').then((res) => res.data);

export const getCariMovements = (dealerId) =>
  api
    .get(dealerId ? `finance/cari/?dealer=${dealerId}` : 'finance/cari/')
    .then((res) => unwrapList(res));

export const receiveDealerPayment = (dealerId, amount) =>
  api
    .post(`finance/dealers/${dealerId}/receive_payment/`, { amount })
    .then((res) => res.data);
