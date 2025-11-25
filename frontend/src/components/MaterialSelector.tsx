"use client";

interface MaterialSelectorProps {
  materials: string[];
  selectedMaterial: string;
  onMaterialChange: (material: string) => void;
  isLoading: boolean;
}

// Configuration for mapping raw IDs to friendly names, categories, and context
const MATERIAL_CONFIG: Record<
  string,
  {
    label: string;
    category: "Construction Materials" | "Economic Indicators" | "Other";
    description: string;
    impact: string;
  }
> = {
  PPI_STEEL: {
    label: "Steel (PPI)",
    category: "Construction Materials",
    description:
      "Producer Price Index for Steel Mill Products. Tracks selling prices received by domestic steel producers.",
    impact:
      "Rising steel prices directly increase costs for structural framing, reinforcement (rebar), and metal building systems.",
  },
  PPI_LUMBER: {
    label: "Lumber (PPI)",
    category: "Construction Materials",
    description:
      "Producer Price Index for Softwood Lumber. Measures price changes in lumber used for construction.",
    impact:
      "Highly volatile. Spikes in lumber prices significantly drive up the cost of residential framing and formwork.",
  },
  PPI_CONCRETE: {
    label: "Concrete (PPI)",
    category: "Construction Materials",
    description:
      "Producer Price Index for Cement and Concrete Products. Tracks prices for ready-mix concrete and block.",
    impact:
      "A baseline cost for foundations and superstructure. Typically less volatile than lumber but steadily increasing.",
  },
  HOUSING_STARTS: {
    label: "Housing Starts",
    category: "Economic Indicators",
    description:
      "New Privately Owned Housing Units Started. A leading indicator of construction activity.",
    impact:
      "High housing starts signal strong future demand for materials (especially lumber/copper), often preceding price hikes.",
  },
  CPI_ALL: {
    label: "Consumer Price Index (CPI)",
    category: "Economic Indicators",
    description:
      "A measure of the average change over time in prices paid by consumers for a market basket of consumer goods.",
    impact:
      "General inflation drives labor and transportation costs, indirectly pushing up the final installed cost of materials.",
  },
  FED_FUNDS_RATE: {
    label: "Federal Funds Rate",
    category: "Economic Indicators",
    description:
      "The interest rate at which depository institutions trade federal funds (balances held at Federal Reserve Banks) with each other overnight.",
    impact:
      "Higher rates increase borrowing costs for developers. This typically cools down construction demand, eventually lowering material prices.",
  },
};

export default function MaterialSelector({
  materials,
  selectedMaterial,
  onMaterialChange,
  isLoading,
}: MaterialSelectorProps) {
  // Helper to organize the raw list of materials into categories
  const groupedMaterials = materials.reduce((groups, materialId) => {
    const config = MATERIAL_CONFIG[materialId] || {
      label: materialId, // Fallback to ID if not configured
      category: "Other",
      description: "No description available.",
      impact: "",
    };

    if (!groups[config.category]) {
      groups[config.category] = [];
    }

    groups[config.category].push({ id: materialId, label: config.label });
    return groups;
  }, {} as Record<string, { id: string; label: string }[]>);

  // Define the order we want categories to appear
  const categoryOrder = [
    "Construction Materials",
    "Economic Indicators",
    "Other",
  ];

  // Get current config for the selected material (if any)
  const currentInfo = MATERIAL_CONFIG[selectedMaterial];

  return (
    <div className="w-full max-w-xs relative">
      {/* Selector Section */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label
            htmlFor="material-select"
            className="block text-sm font-medium text-gray-300"
          >
            Select Forecast Series
          </label>

          {/* Info Icon with Tooltip */}
          {currentInfo && (
            <div className="group relative flex items-center">
              <span className="text-xs text-gray-500 mr-1 group-hover:text-gray-300 transition-colors">
                What is this?
              </span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="w-5 h-5 text-gray-400 hover:text-blue-400 cursor-help transition-colors"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>

              {/* Floating Context Card (Tooltip) */}
              <div className="absolute right-0 top-6 w-72 z-50 hidden group-hover:block">
                <div className="bg-gray-800 border border-gray-600 rounded-md p-3 text-sm shadow-xl relative">
                  {/* Tooltip Arrow (Optional visual flourish) */}
                  <div className="absolute -top-2 right-1 w-4 h-4 bg-gray-800 border-t border-l border-gray-600 transform rotate-45"></div>

                  <h4 className="font-semibold text-blue-400 mb-1 relative z-10">
                    {currentInfo.label}
                  </h4>
                  <p className="text-gray-300 mb-3 leading-relaxed relative z-10">
                    {currentInfo.description}
                  </p>
                  <div className="border-t border-gray-600/50 pt-2 relative z-10">
                    <p className="text-gray-400 text-xs italic">
                      <span className="font-semibold text-gray-500 not-italic">
                        Impact:{" "}
                      </span>
                      {currentInfo.impact}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <select
          id="material-select"
          value={selectedMaterial}
          onChange={(e) => onMaterialChange(e.target.value)}
          disabled={isLoading || materials.length === 0}
          className="block w-full pl-3 pr-10 py-2 text-base border-gray-600 bg-gray-700 text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md disabled:opacity-50"
        >
          <option value="" disabled>
            {materials.length > 0 ? "Select a series..." : "Loading options..."}
          </option>

          {/* Render options grouped by category */}
          {categoryOrder.map((category) => {
            const items = groupedMaterials[category];
            if (!items || items.length === 0) return null;

            return (
              <optgroup key={category} label={category}>
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </optgroup>
            );
          })}
        </select>
      </div>
    </div>
  );
}
