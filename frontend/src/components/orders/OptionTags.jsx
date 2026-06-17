const OptionTags = ({ item }) => {
  const label = item.options_display
    || item.selected_options?.map((o) => o.option_name).filter(Boolean).join(', ');

  if (!label) return null;

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {label.split(', ').map((tag) => (
        <span
          key={tag}
          className="text-[10px] font-semibold uppercase px-1.5 py-0.5 border border-gray-300 bg-gray-50 text-gray-600 rounded-sm"
        >
          {tag}
        </span>
      ))}
    </div>
  );
};

export default OptionTags;
