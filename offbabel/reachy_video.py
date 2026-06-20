"""Reachy Mini live camera -> browser MJPEG bridge.

The robot exposes no RTSP server, so we run `rpicam-vid` on the robot over SSH (MJPEG to stdout),
reparse the JPEG frames here, and hand them to the browser as multipart/x-mixed-replace — which a
plain <img> tag renders with no extra client code.

    Reachy camera -> rpicam-vid MJPEG over SSH -> this reader thread -> /reachy-media/video.mjpeg -> <img>

One shared SSH stream feeds all browser clients (a refcount starts it on the first viewer and stops
it when the last one leaves, so the robot isn't streaming to nobody). Best-effort throughout: a
missing tunnel/robot prints and degrades to "no frames" — it must never crash the server (the robot
is an enhancement, not a dependency).
"""
import subprocess
import threading
import time
import urllib.request

from . import config

JPEG_SOI = b"\xff\xd8"  # start-of-image marker
JPEG_EOI = b"\xff\xd9"  # end-of-image marker

_MAX_BUFFER = 4 * 1024 * 1024  # drop a runaway buffer if we never find a frame boundary (corrupt stream)


def _daemon_media(action):
    """POST to the Reachy daemon's media release/acquire. Best-effort: the daemon owns /dev/video0,
    so we 'release' before rpicam-vid grabs the camera and 'acquire' to hand it back afterward.
    Returns True on success. Never raises — a missing daemon must not break the stream path."""
    base = config.REACHY_DAEMON_URL
    if not base:
        return False
    try:
        req = urllib.request.Request(f"{base}/api/media/{action}", method="POST")
        with urllib.request.urlopen(req, timeout=5):  # noqa: S310 (localhost daemon, not arbitrary URL)
            return True
    except Exception as e:  # noqa: BLE001
        print(f"reachy video: daemon media/{action} failed (ignored):", e)
        return False


class ReachyVideoStreamer:
    """Owns the SSH/rpicam subprocess and the most-recent JPEG frame. Thread-safe."""

    def __init__(self):
        self._proc = None
        self._reader = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._clients = 0
        self.latest_frame = None
        self.last_frame_time = 0.0
        self.last_error = None  # last stderr line from ssh/rpicam, surfaced in status() for diagnosis

    def _command(self):
        remote = (
            "rpicam-vid -t 0 --codec mjpeg --inline "
            f"--width {config.REACHY_CAM_WIDTH} "
            f"--height {config.REACHY_CAM_HEIGHT} "
            f"--framerate {config.REACHY_CAM_FPS} "
            "-o -"
        )
        # BatchMode=yes: never block the server on a password/passphrase prompt — fail fast instead.
        # Keepalives detect a dropped LAN/tunnel so the reader thread exits and can be restarted.
        return [
            "ssh", "-T",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=5",
            "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=2",
            "-o", "StrictHostKeyChecking=accept-new",
            config.REACHY_SSH_HOST,
            remote,
        ]

    def start(self):
        """Spawn the SSH/rpicam stream if it isn't already running. Safe to call repeatedly."""
        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                return
            self._stop.clear()
            self.latest_frame = None
            self.last_frame_time = 0.0
            self.last_error = None
            _daemon_media("release")  # the daemon owns the camera; free it so rpicam-vid can acquire
            try:
                self._proc = subprocess.Popen(
                    self._command(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    bufsize=0,
                )
            except Exception as e:  # noqa: BLE001
                print("reachy video: failed to spawn ssh/rpicam (ignored):", e)
                self.last_error = str(e)
                self._proc = None
                return
            self._reader = threading.Thread(target=self._read_loop, args=(self._proc,), daemon=True)
            self._reader.start()
            # Drain stderr so an SSH/rpicam failure reason (e.g. "Permission denied") is captured
            # for status() instead of being lost — and so a full stderr pipe can't block the child.
            threading.Thread(target=self._drain_stderr, args=(self._proc,), daemon=True).start()

    def stop(self):
        """Terminate the stream and reader thread. Safe to call repeatedly."""
        with self._lock:
            self._stop.set()
            proc = self._proc
            self._proc = None
            self._reader = None
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
        if proc is not None:
            _daemon_media("acquire")  # hand the camera back to the daemon now that rpicam has stopped

    def add_client(self):
        """A browser connected: start the shared stream on the first viewer."""
        with self._lock:
            self._clients += 1
        self.start()

    def remove_client(self):
        """A browser disconnected: stop the shared stream when the last viewer leaves."""
        with self._lock:
            self._clients = max(0, self._clients - 1)
            idle = self._clients == 0
        if idle:
            self.stop()

    def get_latest_frame(self):
        with self._lock:
            return self.latest_frame

    def is_alive(self):
        with self._lock:
            return self._proc is not None and self._proc.poll() is None

    def status(self):
        with self._lock:
            return {
                "alive": self._proc is not None and self._proc.poll() is None,
                "has_frame": self.latest_frame is not None,
                "last_frame_time": self.last_frame_time,
                "clients": self._clients,
                "ssh_host": config.REACHY_SSH_HOST,
                "width": config.REACHY_CAM_WIDTH,
                "height": config.REACHY_CAM_HEIGHT,
                "framerate": config.REACHY_CAM_FPS,
                "last_error": self.last_error,
            }

    def _read_loop(self, proc):
        """Read rpicam's MJPEG stdout, split it on JPEG SOI/EOI markers, publish the latest frame."""
        buffer = b""
        if proc.stdout is None:
            return
        try:
            while not self._stop.is_set():
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break  # EOF: ssh/rpicam exited (tunnel dropped, camera busy, etc.)
                buffer += chunk
                while True:
                    start = buffer.find(JPEG_SOI)
                    if start < 0:
                        if len(buffer) > _MAX_BUFFER:
                            buffer = b""
                        break
                    end = buffer.find(JPEG_EOI, start + 2)
                    if end < 0:
                        if start > 0:
                            buffer = buffer[start:]  # discard pre-SOI garbage, keep the partial frame
                        break
                    frame = buffer[start:end + 2]
                    buffer = buffer[end + 2:]
                    with self._lock:
                        self.latest_frame = frame
                        self.last_frame_time = time.monotonic()
        except Exception as e:  # noqa: BLE001
            print("reachy video: reader stopped (ignored):", e)
        finally:
            with self._lock:
                if self._proc is proc:
                    self._proc = None

    def _drain_stderr(self, proc):
        """Capture ssh/rpicam stderr so the failure reason reaches status() (and isn't lost)."""
        if proc.stderr is None:
            return
        try:
            for raw in iter(proc.stderr.readline, b""):
                line = raw.decode("utf-8", "replace").strip()
                if line:
                    with self._lock:
                        self.last_error = line  # keep the most recent line (often the real reason)
                    print("reachy video [ssh]:", line)
        except Exception:  # noqa: BLE001
            pass


# Module-level singleton: one shared stream for the whole server.
streamer = ReachyVideoStreamer()