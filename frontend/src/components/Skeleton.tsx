export function SkeletonCard() {
  return (
    <div className="card animate-pulse flex flex-col">
      <div className="bg-secondary-100 rounded-lg h-40 mb-4" />
      <div className="h-3 bg-secondary-100 rounded w-1/3 mb-2" />
      <div className="h-4 bg-secondary-100 rounded w-3/4 mb-3" />
      <div className="h-3 bg-secondary-100 rounded w-1/4 mb-3" />
      <div className="h-4 bg-secondary-100 rounded w-1/2 mb-2" />
      <div className="h-9 bg-secondary-100 rounded mt-auto" />
    </div>
  )
}

export function SkeletonLine({ width = '100%' }: { width?: string }) {
  return <div className="h-4 bg-secondary-100 rounded animate-pulse" style={{ width }} />
}

export function SkeletonPage() {
  return (
    <div className="max-w-content mx-auto px-margin-mobile lg:px-margin-desktop py-8 animate-pulse">
      <div className="h-8 bg-secondary-100 rounded w-1/3 mb-8" />
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    </div>
  )
}
