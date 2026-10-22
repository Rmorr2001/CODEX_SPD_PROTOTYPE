import { useState } from 'react';
import { chapterSite } from '../../app/links';

/** Initials represent missing/broken images without suggesting a real portrait exists. */
export function MemberAvatar({
  name,
  image,
  large = false,
}: {
  name: string;
  image: string | null;
  large?: boolean;
}) {
  const [failedImage, setFailedImage] = useState<string | null>(null);
  const src = image?.startsWith('/') ? `${chapterSite}${image.slice(1)}` : image;
  return (
    <div className={`directory-avatar${large ? ' large' : ''}`}>
      {src && failedImage !== src ? (
        <img src={src} alt={name} onError={() => setFailedImage(src ?? null)} />
      ) : (
        <span aria-hidden="true">
          {name
            .split(' ')
            .map((part) => part[0])
            .slice(0, 2)
            .join('')}
        </span>
      )}
    </div>
  );
}
