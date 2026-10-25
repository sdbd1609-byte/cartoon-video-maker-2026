
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))

OUT = ROOT / "rabbit_magic_star.mp4"
W = int(DATA.get("width", 720))
H = int(DATA.get("height", 1280))
FPS = int(DATA.get("fps", 24))
SCENES = DATA["scenes"]
DURATION = int(DATA.get("duration", 30))


def draw_scene(scene, index):
    im = Image.new("RGB", (W, H), (15, 25, 55))
    d = ImageDraw.Draw(im)

    # Night sky
    for i in range(70):
        x = (i * 97 + 23) % W
        y = (i * 137 + 31) % (H // 2)
        d.ellipse((x, y, x + 4, y + 4), fill="white")

    # Moon
    d.ellipse((W - 145, 75, W - 65, 155), fill=(255, 240, 170))

    # Forest
    d.rectangle((0, H * 2 // 3, W, H), fill=(20, 90, 58))
    for x in range(-20, W + 60, 100):
        d.polygon(
            [(x, H * 2 // 3), (x + 50, H // 3), (x + 100, H * 2 // 3)],
            fill=(15, 65, 48),
        )

    # Glowing magic star changes position by scene
    sx = W // 2 + (index - 1) * 100
    sy = H // 2 - 100
    points = []
    for j in range(10):
        angle = -math.pi / 2 + j * math.pi / 5
        radius = 48 if j % 2 == 0 else 22
        points.append(
            (sx + int(math.cos(angle) * radius),
             sy + int(math.sin(angle) * radius))
        )
    d.polygon(points, fill=(255, 225, 70))

    # Cute rabbit
    cx, cy = W // 2, H * 2 // 3 - 15
    d.ellipse((cx - 48, cy - 45, cx + 48, cy + 45), fill=(245, 240, 230))
    d.ellipse((cx - 38, cy - 115, cx - 8, cy - 35), fill=(245, 240, 230))
    d.ellipse((cx + 8, cy - 115, cx + 38, cy - 35), fill=(245, 240, 230))
    d.ellipse((cx - 20, cy - 5, cx - 10, cy + 5), fill="black")
    d.ellipse((cx + 10, cy - 5, cx + 20, cy + 5), fill="black")
    d.ellipse((cx - 5, cy + 8, cx + 5, cy + 16), fill=(240, 120, 140))

    # Scene caption
    text = scene["text"]
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if len(test) > 34:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)

    y = H - 180
    for line in lines:
        d.text((35, y), line, fill="white", stroke_width=1, stroke_fill="black")
        y += 35

    return im


def main():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed.")

    per_scene = DURATION / len(SCENES)
    frames_dir = ROOT / "video_frames"
    frames_dir.mkdir(exist_ok=True)

    # Create frames at the target frame rate
    total_frames = DURATION * FPS
    for frame_no in range(total_frames):
        scene_index = min(int(frame_no / FPS / per_scene), len(SCENES) - 1)
        im = draw_scene(SCENES[scene_index], scene_index)
        im.save(frames_dir / f"frame_{frame_no:05d}.png")

    # Assemble frames into an MP4 video
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(frames_dir / "frame_%05d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", str(DURATION),
            str(OUT),
        ],
        check=True,
    )
    print(f"Video created: {OUT}")


if __name__ == "__main__":
    main()
