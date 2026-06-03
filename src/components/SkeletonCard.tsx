export default function SkeletonCard() {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm animate-pulse">
      <div className="h-40 bg-gradient-to-br from-gray-100 to-gray-200" />
      <div className="p-4 space-y-3">
        <div className="space-y-2">
          <div className="h-3 bg-gray-200 rounded w-3/4" />
          <div className="h-2.5 bg-gray-100 rounded w-1/2" />
          <div className="h-2 bg-gray-100 rounded w-1/3" />
        </div>
        <div className="flex gap-1.5">
          <div className="h-4 w-14 bg-gray-100 rounded-full" />
          <div className="h-4 w-16 bg-gray-100 rounded-full" />
          <div className="h-4 w-12 bg-gray-100 rounded-full" />
        </div>
        <div className="space-y-1.5">
          <div className="h-2 bg-gray-100 rounded w-full" />
          <div className="h-2 bg-gray-100 rounded w-5/6" />
        </div>
        <div className="flex gap-1.5">
          <div className="h-5 w-20 bg-red-50 rounded-full" />
          <div className="h-5 w-16 bg-red-50 rounded-full" />
        </div>
        <div className="pt-3 border-t border-gray-50 flex justify-between">
          <div className="h-4 w-20 bg-gray-100 rounded" />
          <div className="h-4 w-12 bg-amber-50 rounded" />
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div className="h-8 bg-gray-100 rounded-lg" />
          <div className="h-8 bg-red-100 rounded-lg" />
        </div>
      </div>
    </div>
  );
}
