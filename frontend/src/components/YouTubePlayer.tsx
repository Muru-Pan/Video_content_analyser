import { forwardRef, useImperativeHandle, useMemo, useState } from "react";

export type YouTubePlayerHandle = {
  seekTo: (seconds: number) => void;
};

function getYouTubeId(url: string): string {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtu.be")) {
      return parsed.pathname.replace("/", "");
    }
    return parsed.searchParams.get("v") ?? "";
  } catch {
    return "";
  }
}

export const YouTubePlayer = forwardRef<YouTubePlayerHandle, { url: string }>(function YouTubePlayer({ url }, ref) {
  const [startSeconds, setStartSeconds] = useState(0);
  const videoId = useMemo(() => getYouTubeId(url), [url]);

  useImperativeHandle(ref, () => ({
    seekTo(seconds: number) {
      setStartSeconds(Math.max(0, Math.floor(seconds)));
    },
  }));

  if (!videoId) {
    return null;
  }

  const embedUrl = `https://www.youtube.com/embed/${videoId}?start=${startSeconds}&autoplay=1&enablejsapi=1`;
  return (
    <div className="panel player-panel">
      <h2>Video Player</h2>
      <div className="player-shell">
        <iframe
          key={`${videoId}-${startSeconds}`}
          src={embedUrl}
          title="YouTube video player"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
});
