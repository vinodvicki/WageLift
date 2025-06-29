// Simple className merger
function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn('animate-pulse rounded-md bg-gray-200', className)}
      {...props}
    />
  );
}

// Common skeleton patterns
export function SkeletonCard() {
  return (
    <div className="rounded-lg border bg-white p-6">
      <div className="space-y-3">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-20 w-full" />
        <div className="flex justify-end space-x-2">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-20" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="rounded-lg border bg-white">
      <div className="border-b p-4">
        <Skeleton className="h-6 w-40" />
      </div>
      <div className="p-4">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="pb-2 text-left">
                <Skeleton className="h-4 w-24" />
              </th>
              <th className="pb-2 text-left">
                <Skeleton className="h-4 w-32" />
              </th>
              <th className="pb-2 text-left">
                <Skeleton className="h-4 w-20" />
              </th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: rows }).map((_, i) => (
              <tr key={i} className="border-b">
                <td className="py-3">
                  <Skeleton className="h-4 w-32" />
                </td>
                <td className="py-3">
                  <Skeleton className="h-4 w-40" />
                </td>
                <td className="py-3">
                  <Skeleton className="h-4 w-16" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function SkeletonForm() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-4 w-24 mb-2" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div>
        <Skeleton className="h-4 w-32 mb-2" />
        <Skeleton className="h-10 w-full" />
      </div>
      <div>
        <Skeleton className="h-4 w-28 mb-2" />
        <Skeleton className="h-24 w-full" />
      </div>
      <Skeleton className="h-10 w-32" />
    </div>
  );
}