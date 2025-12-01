import { ImageResponse } from "next/og";

// Image metadata
export const size = {
  width: 32,
  height: 32,
};
export const contentType = "image/png";

// Image generation
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 24,
          background: "#111827", // Dark gray background
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "center",
          color: "white",
          borderRadius: "20%",
          padding: "4px",
          gap: "2px",
        }}
      >
        {/* Bar 1 (Short) */}
        <div
          style={{
            width: "6px",
            height: "40%",
            background: "#60a5fa", // Blue-400
            borderRadius: "1px",
          }}
        />
        {/* Bar 2 (Medium) */}
        <div
          style={{
            width: "6px",
            height: "65%",
            background: "#3b82f6", // Blue-500
            borderRadius: "1px",
          }}
        />
        {/* Bar 3 (Tall) */}
        <div
          style={{
            width: "6px",
            height: "85%",
            background: "#2563eb", // Blue-600
            borderRadius: "1px",
          }}
        />
      </div>
    ),
    {
      ...size,
    }
  );
}
