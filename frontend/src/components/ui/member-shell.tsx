import { useState, type ReactNode } from 'react';
import { Sheet, SheetContent, SheetTrigger } from './sheet';
import { Button } from './button';

/** Shared presentation frame; route permissions and data stay with the identity domain. */
export function MemberShell({
  brand,
  navigation,
  footer,
  toolbar,
  children,
}: {
  brand: ReactNode;
  navigation: (close: () => void) => ReactNode;
  footer: ReactNode;
  toolbar: ReactNode;
  children: ReactNode;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="spd-ui m-0 min-h-screen overflow-clip border-border bg-[#f6f6f8] sm:m-5 sm:min-h-[calc(100vh-40px)] sm:rounded-2xl sm:border lg:grid lg:grid-cols-[260px_minmax(0,1fr)]">
      <a className="skip-link" href="#member-content">
        Skip to content
      </a>
      <aside className="hidden flex-col bg-[#17171c] px-5 py-8 text-white lg:flex">
        {brand}
        {navigation(() => {})}
        <div className="mt-auto border-t border-white/15 pt-6">{footer}</div>
      </aside>
      <div className="min-w-0">
        <header className="member-topbar flex min-h-20 items-center justify-between gap-3 border-b border-border bg-white px-5 py-4 sm:px-10">
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" className="lg:hidden" aria-label="Open navigation">
                ☰
              </Button>
            </SheetTrigger>
            <SheetContent
              title="Menu"
              closeLabel="Close navigation"
              className="left-0 right-auto max-w-[320px] border-0 bg-[#17171c] text-white sm:w-[320px] sm:min-w-0"
            >
              {brand}
              {navigation(() => setMenuOpen(false))}
              <div className="mt-auto border-t border-white/15 pt-6">{footer}</div>
            </SheetContent>
          </Sheet>
          {toolbar}
        </header>
        <main
          className="member-main mx-auto w-full max-w-[1400px] px-5 py-8 sm:px-10 sm:py-10 xl:px-14"
          id="main"
        >
          <div id="member-content">{children}</div>
        </main>
      </div>
    </div>
  );
}
