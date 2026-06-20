import { useEffect, useState } from "react"
import { Loader2, RefreshCw, VideoOff } from "lucide-react"
import { cn } from "@/lib/utils"

// Live Reachy Mini camera feed. The Python backend reparses the robot's rpicam MJPEG stream into a
// multipart/x-mixed-replace endpoint, so a plain <img> renders it with no extra client code.
// The MJPEG request returns 200 even when the robot is unreachable (frames simply never arrive), so
// <img> onError can't detect that. We poll the backend's /status to tell "connecting" from
// "offline" and surface the real reason (e.g. an SSH error), then auto-retry — robot = enhancement,
// not a dependency, so this must always degrade gracefully.
const STREAM_URL = "/reachy-media/video.mjpeg"
const STATUS_URL = "/reachy-media/video/status"

type StreamStatus = { alive: boolean; has_frame: boolean; last_error: string | null }

export function ReachyVideo({ className, children }: { className?: string; children?: React.ReactNode }) {
  const [attempt, setAttempt] = useState(0) // bump -> remount <img> -> backend (re)starts the stream
  const [imgError, setImgError] = useState(false) // the HTTP stream request itself failed
  const [status, setStatus] = useState<StreamStatus | null>(null)

  useEffect(() => {
    let cancelled = false
    const tick = async () => {
      try {
        const r = await fetch(STATUS_URL, { cache: "no-store" })
        const s = (await r.json()) as StreamStatus
        if (!cancelled) setStatus(s)
      } catch {
        if (!cancelled) setStatus(null) // backend unreachable
      }
    }
    tick()
    const id = setInterval(tick, 2000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  const live = !imgError && !!status?.alive && !!status?.has_frame
  const offline = imgError || (status != null && !status.alive)
  const reason = imgError ? "Stream unavailable" : status?.last_error || "Waiting for the robot…"

  const retry = () => {
    setImgError(false)
    setStatus(null) // optimistically drop to "connecting" so the <img> remounts immediately
    setAttempt((n) => n + 1)
  }

  // Gently auto-retry while offline so reconnecting the robot/tunnel recovers without a manual click.
  useEffect(() => {
    if (!offline) return
    const id = setTimeout(retry, 5000)
    return () => clearTimeout(id)
  }, [offline, attempt])

  return (
    <div
      className={cn(
        "relative grid flex-1 place-items-center overflow-hidden rounded-xl border bg-muted/40",
        className,
      )}
    >
      {!offline && (
        <img
          key={attempt}
          src={`${STREAM_URL}?v=${attempt}`}
          alt="Reachy Mini live camera"
          className={cn("h-full w-full object-cover transition-opacity", live ? "opacity-100" : "opacity-0")}
          onError={() => setImgError(true)}
        />
      )}

      {!live && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 px-6 text-center text-muted-foreground">
          {offline ? (
            <>
              <VideoOff className="size-10" strokeWidth={2} />
              <div className="text-sm font-medium">Robot camera offline</div>
              <div className="max-w-full break-words text-xs text-muted-foreground/80">{reason}</div>
              <button
                onClick={retry}
                className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-muted px-3 py-1 text-sm font-medium text-foreground transition hover:bg-foreground hover:text-background"
              >
                <RefreshCw className="size-4" strokeWidth={2} /> Retry
              </button>
            </>
          ) : (
            <>
              <Loader2 className="size-8 animate-spin" strokeWidth={2} />
              <div className="text-sm font-medium">Connecting to robot camera…</div>
            </>
          )}
        </div>
      )}

      {live && children}
    </div>
  )
}