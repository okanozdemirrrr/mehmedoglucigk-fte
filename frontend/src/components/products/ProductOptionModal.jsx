import { useMemo, useState } from 'react';
import Modal from '../ui/Modal';
import { formatCurrency } from '../../utils/format';

const ProductOptionModal = ({ product, open, onClose, onAddToCart }) => {
  const [quantity, setQuantity] = useState(1);
  const [selectedByGroup, setSelectedByGroup] = useState({});

  const groups = product?.option_groups || [];

  const unitPrice = useMemo(() => {
    if (!product) return 0;
    const base = parseFloat(product.effective_price || product.base_price || 0);
    let delta = 0;
    groups.forEach((group) => {
      const selected = selectedByGroup[group.id] || [];
      group.items?.forEach((item) => {
        if (selected.includes(item.id)) {
          delta += parseFloat(item.price_delta || 0);
        }
      });
    });
    return base + delta;
  }, [product, groups, selectedByGroup]);

  const requiredMet = useMemo(() => {
    return groups
      .filter((g) => g.is_required)
      .every((g) => (selectedByGroup[g.id] || []).length > 0);
  }, [groups, selectedByGroup]);

  const toggleOption = (group, optionId) => {
    setSelectedByGroup((prev) => {
      const current = prev[group.id] || [];
      if (group.allow_multiple) {
        const next = current.includes(optionId)
          ? current.filter((id) => id !== optionId)
          : [...current, optionId];
        return { ...prev, [group.id]: next };
      }
      return { ...prev, [group.id]: [optionId] };
    });
  };

  const buildSelectedOptions = () => {
    const result = [];
    groups.forEach((group) => {
      const selectedIds = selectedByGroup[group.id] || [];
      group.items?.forEach((item) => {
        if (selectedIds.includes(item.id)) {
          result.push({
            option_id: item.id,
            group_id: group.id,
            group_name: group.name,
            option_name: item.name,
            price_delta: item.price_delta,
          });
        }
      });
    });
    return result;
  };

  const handleAdd = () => {
    if (!requiredMet || quantity < 1) return;
    onAddToCart({
      product,
      quantity,
      selectedOptions: buildSelectedOptions(),
      unitPrice,
    });
    setQuantity(1);
    setSelectedByGroup({});
    onClose();
  };

  const handleClose = () => {
    setQuantity(1);
    setSelectedByGroup({});
    onClose();
  };

  if (!product) return null;

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={product.name}
      footer={
        <>
          <button type="button" onClick={handleClose} className="erp-btn-secondary">
            İptal
          </button>
          <button
            type="button"
            onClick={handleAdd}
            disabled={!requiredMet || quantity < 1}
            className="erp-btn-primary"
          >
            Sepete Ekle
          </button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="flex justify-between text-sm border-b border-gray-200 pb-3">
          <span className="text-gray-600">Birim Fiyat</span>
          <span className="font-bold tabular-nums">{formatCurrency(unitPrice)}</span>
        </div>

        {groups.map((group) => (
          <div key={group.id}>
            <p className="text-xs font-semibold uppercase text-gray-700 mb-2">
              {group.name}
              {group.is_required && <span className="text-red-600 ml-1">*</span>}
            </p>
            <div className="space-y-1">
              {group.items?.map((item) => {
                const selected = (selectedByGroup[group.id] || []).includes(item.id);
                const inputType = group.allow_multiple ? 'checkbox' : 'radio';
                return (
                  <label
                    key={item.id}
                    className={`flex items-center gap-2 px-3 py-2 border rounded-sm cursor-pointer text-sm ${
                      selected ? 'border-bordo-800 bg-bordo-50' : 'border-gray-300 bg-white'
                    }`}
                  >
                    <input
                      type={inputType}
                      name={`group-${group.id}`}
                      checked={selected}
                      onChange={() => toggleOption(group, item.id)}
                      className="text-bordo-800"
                    />
                    <span className="flex-1">{item.name}</span>
                    {parseFloat(item.price_delta) > 0 && (
                      <span className="text-xs text-gray-500 tabular-nums">
                        +{formatCurrency(item.price_delta)}
                      </span>
                    )}
                  </label>
                );
              })}
            </div>
          </div>
        ))}

        <div>
          <p className="text-xs font-semibold uppercase text-gray-700 mb-2">Miktar</p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              className="w-8 h-8 border border-gray-300 rounded-sm hover:bg-gray-50"
            >
              −
            </button>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value, 10) || 1))}
              className="w-16 erp-input py-1 text-center tabular-nums"
            />
            <button
              type="button"
              onClick={() => setQuantity((q) => q + 1)}
              className="w-8 h-8 border border-gray-300 rounded-sm hover:bg-gray-50"
            >
              +
            </button>
            <span className="text-xs text-gray-500 uppercase ml-2">{product.unit || 'ADET'}</span>
          </div>
        </div>

        {!requiredMet && (
          <p className="text-xs text-red-700 bg-red-50 border border-red-200 px-2 py-1 rounded-sm">
            Zorunlu seçenekleri işaretleyin.
          </p>
        )}
      </div>
    </Modal>
  );
};

export default ProductOptionModal;
