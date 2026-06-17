export const ACTIVE_ORDER_STATUSES = ['PENDING', 'PREPARING', 'ON_THE_WAY'];

export const isActiveOrder = (order) => ACTIVE_ORDER_STATUSES.includes(order.status);

export const isPastOrder = (order) => order.status === 'DELIVERED';

export const sortOrdersNewestFirst = (orders) =>
  [...orders].sort((a, b) => new Date(b.order_date) - new Date(a.order_date));
