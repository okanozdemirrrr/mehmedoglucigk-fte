import { create } from 'zustand';

const useCartStore = create((set, get) => ({
  lines: [],

  addLine: ({ product, quantity, selectedOptions, unitPrice }) => {
    const line = {
      id: `${product.id}-${Date.now()}`,
      productId: product.id,
      productName: product.name,
      productCode: product.code,
      unit: product.unit,
      quantity,
      selectedOptions,
      unitPrice,
      lineTotal: quantity * unitPrice,
    };
    set((state) => ({ lines: [...state.lines, line] }));
  },

  removeLine: (lineId) => {
    set((state) => ({ lines: state.lines.filter((l) => l.id !== lineId) }));
  },

  clearCart: () => set({ lines: [] }),

  getGrandTotal: () => get().lines.reduce((sum, l) => sum + l.lineTotal, 0),

  toOrderItems: () =>
    get().lines.map((line) => ({
      product: line.productId,
      product_name: line.productName,
      quantity: line.quantity,
      unit_price: String(line.unitPrice),
      selected_options: line.selectedOptions.map((opt) => ({
        option_id: opt.option_id,
      })),
    })),
}));

export default useCartStore;
