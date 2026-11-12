"""Render frames of index.html with Playwright.
usage: shoot.py stills t1 t2 ...      -> out/still_<t>.jpg
       shoot.py range t0 t1 name      -> out/<name>.mp4 (30 fps, silent)
"""
import sys, os, subprocess, threading, http.server, socketserver, functools, json
from playwright.sync_api import sync_playwright

APP = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR", os.path.join(os.path.dirname(APP), "out"))
FPS = 30


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP)
    h.log_message = lambda *a, **k: None
    s = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s.server_address[1]


def main():
    port = serve()
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--force-color-profile=srgb"])
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.goto(f"http://127.0.0.1:{port}/index.html")
        pg.wait_for_function("window.ready===true")
        if sys.argv[1] == "stills":
            for t in sys.argv[2:]:
                pg.evaluate(f"setTime({float(t)})")
                pg.screenshot(path=f"{OUT}/still_{t}.jpg", type="jpeg", quality=90)
        else:
            t0, t1, name = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
            tmp = f"{OUT}/{name}.part.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
            f0, f1 = round(t0 * FPS), round(t1 * FPS)
            for f in range(f0, f1):
                pg.evaluate(f"setTime({f / FPS})")
                ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close()
            if ff.wait() == 0:
                os.replace(tmp, f"{OUT}/{name}.mp4")
                print("ok", name, f1 - f0, "frames")
            else:
                sys.exit("ffmpeg failed")
        b.close()


main()
