export function totalsForOrders(orders, options) {
  const result = { count: 0, total: 0, skipped: [] };
  if (!orders || orders.length === 0) {
    return result;
  }
  for (const order of orders) {
    if (order.cancelled) {
      result.skipped.push(order.id);
      continue;
    }
    const lines = order.lines.filter((line) => line.quantity > 0);
    let subtotal = 0;
    for (const line of lines) {
      subtotal += line.price * line.quantity;
    }
    if (options.tax && subtotal > 0) {
      subtotal = subtotal * (1 + options.tax);
    }
    result.total += subtotal;
    result.count += lines.length > 0 ? 1 : 0;
  }
  return result;
}

export const prefix = (value) => `order-${value}`;
