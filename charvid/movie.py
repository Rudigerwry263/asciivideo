"""Movie / Scene authoring API + deterministic frame loop -> MP4 (ffmpeg)."""
import os
import shutil
import subprocess
import sys
import time

from .canvas import CharCanvas
from . import elements as E


class Scene:
    def __init__(self, movie, duration, bg="#000000"):
        self.movie = movie
        self.duration = duration
        self.bg = bg
        self.elements = []

    def add(self, element):
        if getattr(element, "seed", 0) == 0:
            element.seed = self.movie._next_seed()
        self.elements.append(element)
        return element

    # convenience builders (all return the element for further tweaking) -----
    def text(self, text, **kw):
        return self.add(E.Text(text, **kw))

    def banner(self, text, **kw):
        return self.add(E.Banner(text, **kw))

    def sprite(self, name, **kw):
        return self.add(E.Sprite(name, **kw))

    def custom_sprite(self, art, **kw):
        return self.add(E.CustomSprite(art, **kw))

    def loadbar(self, **kw):
        return self.add(E.LoadBar(**kw))

    def particles(self, **kw):
        return self.add(E.Particles(**kw))

    def border(self, **kw):
        return self.add(E.Border(**kw))

    def symgrid(self, **kw):
        return self.add(E.SymbolGrid(**kw))

    def clock(self, **kw):
        return self.add(E.Clock(**kw))

    def timer(self, **kw):
        return self.add(E.Timer(**kw))


class Movie:
    def __init__(self, width=1080, height=1440, fps=30, font_size=40,
                 line_spacing=1.12, font=None, cjk_font=None, glow_radius=10,
                 glow_gain=0.9, seed=7):
        self.width = width - (width % 2)
        self.height = height - (height % 2)
        self.fps = fps
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.font = font
        self.cjk_font = cjk_font
        self.glow_radius = glow_radius
        self.glow_gain = glow_gain
        self.seed = seed
        self.scenes = []
        self._seed_counter = seed * 1000 + 1

    def _next_seed(self):
        self._seed_counter += 1
        return self._seed_counter

    def scene(self, duration, bg="#000000"):
        s = Scene(self, duration, bg)
        self.scenes.append(s)
        return s

    @property
    def total_duration(self):
        return sum(s.duration for s in self.scenes)

    def _make_canvas(self):
        return CharCanvas(self.width, self.height, font_size=self.font_size,
                          line_spacing=self.line_spacing, font_path=self.font,
                          cjk_font_path=self.cjk_font,
                          glow_radius=self.glow_radius, glow_gain=self.glow_gain)

    def snap(self, out_png, t):
        """Render a single frame at global time t (debugging)."""
        canvas = self._make_canvas()
        scene, local = self._scene_at(t)
        canvas.new_frame()
        for el in scene.elements:
            el.draw(canvas, local)
        canvas.render_rgb(scene.bg).save(out_png)
        return out_png

    def _scene_at(self, t):
        acc = 0.0
        for s in self.scenes:
            if t < acc + s.duration or s is self.scenes[-1]:
                return s, t - acc
            acc += s.duration
        return self.scenes[-1], t - (acc - self.scenes[-1].duration)

    def to_html(self, path, title="char-cli-video", loop=True, controls=True,
                autoplay=True):
        """Export a self-contained, animated HTML file (Canvas 2D, no video)."""
        from . import webexport
        return webexport.to_html(self, path, title=title, loop=loop,
                                 controls=controls, autoplay=autoplay)

    def render(self, out, fps=None, crf=18, preset="medium", quiet=False):
        if not self.scenes:
            raise RuntimeError("Movie has no scenes")
        fps = fps or self.fps
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("ffmpeg not found on PATH")
        canvas = self._make_canvas()
        total_frames = max(1, int(round(self.total_duration * fps)))

        cmd = [
            ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{self.width}x{self.height}", "-r", str(fps), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", str(crf), "-preset", preset, out,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        t0 = time.time()
        # precompute scene boundaries
        bounds = []
        acc = 0.0
        for s in self.scenes:
            bounds.append((acc, acc + s.duration, s))
            acc += s.duration

        si = 0
        for f in range(total_frames):
            t = f / fps
            while si < len(bounds) - 1 and t >= bounds[si][1]:
                si += 1
            start, end, scene = bounds[si]
            local = t - start
            canvas.new_frame()
            for el in scene.elements:
                el.draw(canvas, local)
            img = canvas.render_rgb(scene.bg)
            proc.stdin.write(img.tobytes())
            if not quiet and (f % 30 == 0 or f == total_frames - 1):
                pct = 100.0 * (f + 1) / total_frames
                sys.stdout.write(f"\r[charvid] {f + 1}/{total_frames} frames ({pct:4.1f}%)")
                sys.stdout.flush()
        proc.stdin.close()
        proc.wait()
        if not quiet:
            dt = time.time() - t0
            print(f"\n[charvid] wrote {out}  ({total_frames} frames, {dt:.1f}s)")
        return out
