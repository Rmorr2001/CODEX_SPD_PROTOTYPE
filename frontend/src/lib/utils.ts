import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Compose conditional classes and resolve competing Tailwind utilities for new UI primitives. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
