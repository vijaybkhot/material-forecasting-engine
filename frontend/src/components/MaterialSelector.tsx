"use client";

interface MaterialSelectorProps {
  materials: string[];
  selectedMaterial: string;
  onMaterialChange: (material: string) => void;
  isLoading: boolean;
}

export default function MaterialSelector({
  materials,
  selectedMaterial,
  onMaterialChange,
  isLoading,
}: MaterialSelectorProps) {
  return (
    <div className="w-full max-w-xs">
      <label
        htmlFor="material-select"
        className="block text-sm font-medium text-gray-300 mb-1"
      >
        Select Material
      </label>
      <select
        id="material-select"
        value={selectedMaterial}
        onChange={(e) => onMaterialChange(e.target.value)}
        disabled={isLoading || materials.length === 0}
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-600 bg-gray-700 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md disabled:opacity-50"
      >
        <option value="">
          {materials.length > 0
            ? "Select a material..."
            : "Loading materials..."}
        </option>
        {materials.map((material) => (
          <option key={material} value={material}>
            {material}
          </option>
        ))}
      </select>
    </div>
  );
}
