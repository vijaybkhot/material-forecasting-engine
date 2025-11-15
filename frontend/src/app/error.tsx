"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="min-h-[60vh] grid place-items-center p-8">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
        {error?.digest && (
          <p className="text-gray-600 mb-2">Digest: {error.digest}</p>
        )}
        <button
          onClick={() => reset()}
          className="mt-3 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-500"
        >
          Try again
        </button>
      </div>
    </main>
  );
}
