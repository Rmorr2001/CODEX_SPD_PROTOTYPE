import { useCallback, useEffect, useRef } from 'react';
import { useBeforeUnload, useBlocker } from 'react-router-dom';

/** Protect a form-local draft and pending operation; acknowledged saves can navigate directly. */
export function useUnsavedMark(dirty: boolean, busy: boolean) {
  const bypass = useRef(false);
  const blocker = useBlocker(() => !bypass.current && (dirty || busy));
  useEffect(() => {
    if (blocker.state !== 'blocked') return;
    if (!busy && window.confirm('Discard unsaved marks?')) {
      bypass.current = true;
      blocker.proceed();
    } else blocker.reset();
  }, [blocker, busy]);
  useBeforeUnload(
    useCallback(
      (event) => {
        if (!bypass.current && (dirty || busy)) {
          event.preventDefault();
          event.returnValue = '';
        }
      },
      [dirty, busy],
    ),
  );
  return () => {
    bypass.current = true;
  };
}
