# UI foundation

Reserved for reviewed shadcn primitives for the user's selected A/C direction, once its reference pixels are accessible.
No primitives or visual redesign have been installed yet. `components.json`
provides scaffold destinations; `src/lib/utils.ts` owns the normal class helper.

Tailwind4 scans only this directory; Preflight is omitted to protect existing
styles. New components must render beneath `.spd-ui` to use isolated semantic
red/black/neutral tokens. Follow the staged migration document before running a
component generator: inspect generated styles and dependencies, retain accessible
labels/keyboard behavior, and test real domain transactions. Avoid domain rules
or data fetching in this shared UI folder.
