import type { ButtonHTMLAttributes } from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const variants = cva(
  'inline-flex min-h-11 items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'border-primary bg-primary text-primary-foreground hover:bg-[#a91729]',
        outline: 'border-border bg-white text-foreground hover:bg-secondary',
        ghost: 'border-transparent bg-transparent text-inherit hover:bg-black/5',
      },
    },
    defaultVariants: { variant: 'primary' },
  },
);

/** shadcn-style button: native semantics, composable links and explicit disabled/focus states. */
export function Button({
  asChild = false,
  className,
  variant,
  type = 'button',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof variants> & { asChild?: boolean }) {
  const Component = asChild ? Slot : 'button';
  return (
    <Component
      data-ui="button"
      type={asChild ? undefined : type}
      className={cn(variants({ variant }), className)}
      {...props}
    />
  );
}
