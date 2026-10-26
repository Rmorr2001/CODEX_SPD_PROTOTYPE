import type { ComponentProps, ReactNode } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { cn } from '@/lib/utils';
import { Button } from './button';

export const Sheet = Dialog.Root;
export const SheetTrigger = Dialog.Trigger;
export const SheetTitle = Dialog.Title;

/** Modal Sheet built on the shadcn/Radix Dialog pattern; Radix owns focus and Escape. */
export function SheetContent({
  children,
  title,
  className,
  closeLabel = 'Close',
  busy = false,
  ...props
}: ComponentProps<typeof Dialog.Content> & {
  children: ReactNode;
  title: string;
  closeLabel?: string;
  busy?: boolean;
}) {
  return (
    <Dialog.Portal>
      <Dialog.Overlay className="fixed inset-0 z-40 bg-black/35" />
      <Dialog.Content
        aria-describedby={undefined}
        className={cn(
          'spd-ui fixed inset-y-0 right-0 z-50 flex w-full flex-col overflow-y-auto border-l border-border bg-white p-6 text-foreground shadow-xl outline-none sm:w-[min(38vw,560px)] sm:min-w-[420px] sm:p-8',
          className,
        )}
        {...props}
      >
        <div className="mb-8 flex items-center justify-between gap-4">
          <Dialog.Title className="m-0 text-2xl font-bold tracking-tight">{title}</Dialog.Title>
          <Dialog.Close asChild>
            <Button
              variant="ghost"
              disabled={busy}
              aria-label={closeLabel}
              className="h-11 w-11 px-0"
            >
              <span aria-hidden="true" className="text-2xl">
                ×
              </span>
            </Button>
          </Dialog.Close>
        </div>
        {children}
      </Dialog.Content>
    </Dialog.Portal>
  );
}
