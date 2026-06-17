import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { formatCurrency } from '../../utils/format';

const RevenueChart = ({ data }) => {
  const chartData = data.map((row) => ({
    date: row.date?.slice(5) || row.date,
    amount: Number(row.amount),
  }));

  if (chartData.length === 0) {
    return (
      <div className="erp-card p-8 text-center text-sm text-gray-500">
        Seçilen dönemde ciro verisi yok.
      </div>
    );
  }

  return (
    <div className="erp-card p-4">
      <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700 mb-4">
        Ciro Trendi
      </h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#6B7280" />
            <YAxis
              tick={{ fontSize: 11 }}
              stroke="#6B7280"
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip
              formatter={(value) => [formatCurrency(value), 'Ciro']}
              contentStyle={{ borderRadius: 2, border: '1px solid #D1D5DB' }}
            />
            <Line
              type="monotone"
              dataKey="amount"
              stroke="#580F1C"
              strokeWidth={2}
              dot={{ r: 3, fill: '#580F1C' }}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default RevenueChart;
