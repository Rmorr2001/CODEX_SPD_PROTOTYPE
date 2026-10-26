import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export function Card({ className, ...props }: HTMLAttributes<HTMLElement>) {
  return (
    <article
      data-ui="card"
      className={cn('rounded-xl border border-border bg-white text-foreground', className)}
      {...props}
    />
  );
}
