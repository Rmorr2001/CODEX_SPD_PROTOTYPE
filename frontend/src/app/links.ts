// Development serves React on Vite; the legacy site stays on Django's origin.
export const chapterSite = import.meta.env.DEV ? 'http://127.0.0.1:8000/' : '/';
