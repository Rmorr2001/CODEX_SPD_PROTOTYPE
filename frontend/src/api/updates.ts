/** Invalidate records across mounted views/tabs without broadcasting member data. */
export type Resource = 'polls' | 'service' | 'marks';
const eventName = 'spd-records-changed';
const channelName = 'spd-records';

export function notifySaved(resource: Resource) {
  window.dispatchEvent(new CustomEvent(eventName, { detail: resource }));
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const channel = new BroadcastChannel(channelName);
      channel.postMessage(resource);
      channel.close();
    }
  } catch {
    /* Polling still reconciles browsers that disable cross-tab messaging. */
  }
}

export function watchSaved(resource: Resource | undefined, refresh: () => void) {
  if (!resource) return () => {};
  const local = (event: Event) => {
    if ((event as CustomEvent).detail === resource) refresh();
  };
  let channel: BroadcastChannel | null = null;
  try {
    channel = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel(channelName) : null;
  } catch {
    /* Polling remains available. */
  }
  if (channel)
    channel.onmessage = (event) => {
      if (event.data === resource) refresh();
    };
  window.addEventListener(eventName, local);
  return () => {
    window.removeEventListener(eventName, local);
    channel?.close();
  };
}
