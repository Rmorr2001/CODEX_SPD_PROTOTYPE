import { safePublicUrl } from '../../api/links';

export type RecruitmentSlide = { caption: string; image: string | null };
export type RecruitmentContent = { interest_url: string | null; slides: RecruitmentSlide[] };

function slide(value: unknown): value is RecruitmentSlide {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'caption' in value &&
    typeof value.caption === 'string' &&
    'image' in value &&
    safePublicUrl(value.image),
  );
}

/** Accept only the safe, ordered presentation contract from HOME. */
export async function fetchRecruitment(signal: AbortSignal): Promise<RecruitmentContent> {
  const response = await fetch('/api/v1/public/recruitment/', {
    headers: { Accept: 'application/json' },
    signal,
  });
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Recruitment content unavailable');
  const data: unknown = await response.json();
  if (
    !data ||
    typeof data !== 'object' ||
    !('interest_url' in data) ||
    !safePublicUrl(data.interest_url) ||
    !('slides' in data) ||
    !Array.isArray(data.slides) ||
    !data.slides.every(slide)
  )
    throw new Error('Invalid recruitment content');
  return { interest_url: data.interest_url, slides: data.slides };
}
