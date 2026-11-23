#!/usr/bin/env python3
"""
Story -> finished vertical Short (1080x1920 MP4).

Pipeline:
  1. Narrate the story (Microsoft Edge neural voice via edge-tts; free, needs internet.
     Falls back to offline espeak-ng if edge-tts can't connect.)
  2. Build word-by-word animated captions (ASS subtitles), with a hook card on top
     for the first seconds.
  3. Pick a background: a random slice of YOUR OWN gameplay clip from backgrounds/,
     or, if that folder is empty, a generated "satisfying" bouncing-ball simulation.
  4. Optionally mix quiet background music from music/.
  5. Write out/<id>/video.mp4, cover.jpg and upload.txt (title, description, tags).

Usage:
  python shortsmaker/make_short.py stories/001-*.json
  python shortsmaker/make_short.py stories/*.json          # render everything
  python shortsmaker/make_short.py --long stories/00*.json  # 16:9 compilation
"""
import argparse
import asyncio
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
FONT_NAME = "Inter Black"
DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"  # warm, natural male narrator
DEFAULT_RATE = "+12%"  # slightly fast narration keeps retention up
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".ogg"}


# --------------------------------------------------------------------------- utils
def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"command failed: {' '.join(map(str, cmd[:6]))} ...")
    return r.stdout


def probe_duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip())


def clean_for_speech(text):
    text = text.replace("—", ", ").replace("–", ", ").replace("...", "…")
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------- TTS
async def _edge_tts(text, voice, rate, mp3_path):
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(mp3_path, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                end = start + chunk["duration"] / 1e7
                words.append([start, end, chunk["text"]])
    return words


def _espeak_tts(text, wav_path):
    """Offline fallback. Robotic, only for testing the pipeline without internet."""
    run(["espeak-ng", "-v", "en-us", "-s", "178", "-w", str(wav_path), text])
    total = probe_duration(wav_path)
    tokens = text.split()
    # weight each word by length, plus pauses after punctuation
    weights = []
    for t in tokens:
        w = len(t) + 2
        if t[-1:] in ",;:":
            w += 4
        if t[-1:] in ".!?…":
            w += 8
        weights.append(w)
    scale = total / sum(weights)
    words, t = [], 0.0
    for tok, w in zip(tokens, weights):
        dur = w * scale
        speak = (len(tok) + 2) * scale
        words.append([t, t + speak, tok])
        t += dur
    return words


def narrate(text, voice, rate, workdir):
    text = clean_for_speech(text)
    mp3 = workdir / "voice.mp3"
    try:
        words = asyncio.run(_edge_tts(text, voice, rate, mp3))
        if not words or mp3.stat().st_size < 1000:
            raise RuntimeError("edge-tts returned no audio")
        print("  voice: edge-tts", voice)
        return mp3, words
    except Exception as e:  # noqa: BLE001
        if not shutil.which("espeak-ng"):
            raise SystemExit(f"edge-tts failed ({e}) and espeak-ng is not installed.")
        print(f"  voice: edge-tts unavailable ({type(e).__name__}); using espeak-ng fallback")
        wav = workdir / "voice.wav"
        return wav, _espeak_tts(text, wav)


# --------------------------------------------------------------------------- captions
def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(s):
    return s.replace("\\", "").replace("{", "(").replace("}", ")")


def build_ass(words, hook, W, H, hook_seconds, ass_path, words_per_chunk=3):
    """Big centred captions, 1-3 words at a time, current word in yellow with a pop."""
    caption_size = int(min(W, H) * 0.105) if H > W else int(H * 0.085)
    hook_size = int(W * 0.072)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT_NAME},{caption_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(6, caption_size // 9)},3,5,60,60,0,1
Style: Hook,{FONT_NAME},{hook_size},&H00111111,&H00111111,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,{int(hook_size * 0.45)},0,8,90,90,{int(H * 0.16)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    if hook:
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(hook_seconds)},Hook,,0,0,0,,"
                     r"{\fad(0,250)}" + ass_escape(hook))

    # group words into chunks; break early on sentence punctuation
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= words_per_chunk or re.search(r"[.!?,;:…]$", w[2]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    y = int(H * 0.55)
    for ci, chunk in enumerate(chunks):
        chunk_end = chunks[ci + 1][0][0] if ci + 1 < len(chunks) else chunk[-1][1] + 0.6
        for wi, (ws, we, _) in enumerate(chunk):
            end = chunk[wi + 1][0] if wi + 1 < len(chunk) else chunk_end
            parts = []
            for j, (_, _, txt) in enumerate(chunk):
                txt = ass_escape(txt.upper())
                if j == wi:
                    parts.append(r"{\c&H00F2FF&\t(0,80,\fscx112\fscy112)\t(80,160,\fscx100\fscy100)}"
                                 + txt + r"{\c&HFFFFFF&\fscx100\fscy100}")
                else:
                    parts.append(txt)
            text = " ".join(parts)
            lines.append(f"Dialogue: 0,{ass_time(ws)},{ass_time(end)},Cap,,0,0,0,,"
                         rf"{{\an5\pos({W // 2},{y})}}" + text)
    ass_path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- backgrounds
def pick_gameplay(duration):
    folder = ROOT / "backgrounds"
    clips = [p for p in folder.glob("*") if p.suffix.lower() in VIDEO_EXTS]
    random.shuffle(clips)
    for clip in clips:
        try:
            length = probe_duration(clip)
        except SystemExit:
            continue
        if length >= duration + 2:
            start = random.uniform(0, length - duration - 1)
            print(f"  background: {clip.name} @ {start:.0f}s")
            return clip, start
    if clips:
        print("  background: clips in backgrounds/ are shorter than the story; using generated one")
    return None, 0


def render_balls(duration, W, H, out_path, fps=30, seed=None):
    """Original 'satisfying' physics sim: balls bounce inside a ring, leave neon trails,
    grow on each hit. Rendered at half resolution then upscaled (fast, no copyright issues)."""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    rng = random.Random(seed)
    w, h = W // 2, H // 2
    cx, cy, R = w / 2, h * 0.52, min(w, h) * 0.44
    hue0 = rng.random()

    def hsv(hh, s=0.85, v=1.0):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(hh % 1, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    balls = []
    for i in range(rng.choice([2, 3])):
        ang = rng.random() * math.tau
        balls.append({"x": cx + math.cos(ang) * R * 0.3, "y": cy + math.sin(ang) * R * 0.3,
                      "vx": rng.uniform(-4, 4), "vy": rng.uniform(-6, -2),
                      "r": 9.0, "hue": hue0 + i * 0.33})
    gravity = 0.32
    trail = Image.new("RGB", (w, h), (8, 8, 14))

    proc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-vf", f"scale={W}:{H}:flags=bicubic", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", str(out_path)],
        stdin=subprocess.PIPE)
    frames = int(duration * fps) + fps
    fade = Image.new("RGB", (w, h), (8, 8, 14))
    for f in range(frames):
        trail = Image.blend(trail, fade, 0.06)
        d = ImageDraw.Draw(trail)
        ring_col = hsv(hue0 + f / (fps * 20), 0.6, 0.9)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=ring_col, width=4)
        for b in balls:
            b["vy"] += gravity
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            dx, dy = b["x"] - cx, b["y"] - cy
            dist = math.hypot(dx, dy)
            if dist + b["r"] > R:
                nx, ny = dx / dist, dy / dist
                dot = b["vx"] * nx + b["vy"] * ny
                b["vx"] -= 2 * dot * nx
                b["vy"] -= 2 * dot * ny
                b["vx"] += rng.uniform(-0.4, 0.4)
                b["x"] = cx + nx * (R - b["r"] - 1)
                b["y"] = cy + ny * (R - b["r"] - 1)
                b["r"] = min(b["r"] * 1.035 + 0.4, R * 0.42)
                b["hue"] += 0.05
                if b["r"] >= R * 0.42:  # reset when it fills the ring
                    b["r"] = 9.0
                # keep enough energy to fly across the whole ring
                speed = math.hypot(b["vx"], b["vy"])
                target = math.sqrt(2 * gravity * 1.7 * R)
                if speed < target:
                    b["vx"] *= target / speed
                    b["vy"] *= target / speed
            col = hsv(b["hue"])
            d.ellipse([b["x"] - b["r"], b["y"] - b["r"], b["x"] + b["r"], b["y"] + b["r"]],
                      fill=col, outline=(255, 255, 255), width=2)
        frame = Image.blend(trail, trail.filter(ImageFilter.GaussianBlur(5)), 0.35)
        proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
    print("  background: generated bouncing-ball simulation")


def pick_music():
    tracks = [p for p in (ROOT / "music").glob("*") if p.suffix.lower() in AUDIO_EXTS]
    return random.choice(tracks) if tracks else None


# --------------------------------------------------------------------------- render
def render(story_text, hook, out_dir, W, H, voice, rate, seed=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        voice_path, words = narrate(story_text, voice, rate, td)
        dur = probe_duration(voice_path) + 0.8
        print(f"  length: {dur:.1f}s ({len(words)} words)")
        if dur > 179:
            print("  WARNING: over 3 minutes - YouTube will not treat this as a Short.")

        ass = td / "captions.ass"
        hook_seconds = min(3.2, words[min(len(words) - 1, 12)][1] if words else 3)
        build_ass(words, hook, W, H, hook_seconds, ass)

        clip, start = pick_gameplay(dur)
        if clip is None:
            bg = td / "bg.mp4"
            render_balls(dur, W, H, bg, seed=seed)
            bg_input = ["-i", str(bg)]
        else:
            bg_input = ["-ss", f"{start:.2f}", "-i", str(clip)]

        music = pick_music()
        inputs = bg_input + ["-i", str(voice_path)]
        if music:
            inputs += ["-stream_loop", "-1", "-i", str(music)]

        vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"setsar=1,fps=30,subtitles='{ass.as_posix()}':fontsdir='{FONT_DIR.as_posix()}'[v]")
        if music:
            af = ("[1:a]aresample=48000,volume=1.0[a1];[2:a]aresample=48000,volume=0.09[a2];"
                  "[a1][a2]amix=inputs=2:duration=first:dropout_transition=0,"
                  "loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        else:
            af = "[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[a]"

        video = out_dir / "video.mp4"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs,
             "-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]",
             "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
             str(video)])
        # cover frame (shows the hook card) for TikTok cover / thumbnail picker
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "1.0",
             "-i", str(video), "-frames:v", "1", "-q:v", "2", str(out_dir / "cover.jpg")])
    return video, dur


def write_upload_sheet(story, out_dir, dur):
    tags = story.get("tags", [])
    hashtags = " ".join("#" + re.sub(r"\W", "", t) for t in tags[:3])
    desc = story.get("description", "").strip()
    txt = f"""TITLE (paste as-is, under 100 chars):
{story['title']}

DESCRIPTION:
{desc}

{hashtags}

This story is fictional and was written for entertainment. Narration uses a synthetic (AI) voice.

TAGS (YouTube Studio > Show more > Tags):
{', '.join(tags)}

SETTINGS CHECKLIST:
- Audience: No, it's not made for kids
- Altered or synthetic content: answer honestly (AI voice/script alone usually = No; realistic fake people/events = Yes)
- Length: {dur:.0f}s  (TikTok Creator Rewards needs > 60s)
- Pinned comment idea: {story.get('pinned_comment', 'What would YOU have done? 👇')}
"""
    (out_dir / "upload.txt").write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stories", nargs="+", type=Path)
    ap.add_argument("--long", action="store_true", help="combine stories into one 16:9 long video")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--rate", default=DEFAULT_RATE)
    ap.add_argument("--force", action="store_true", help="re-render even if output exists")
    args = ap.parse_args()

    if args.long:
        stories = [json.loads(p.read_text()) for p in sorted(args.stories)]
        joined = "  ".join(s["story"] + " … Next story." for s in stories[:-1]) + "  " + stories[-1]["story"]
        joined += " … If you made it this far, subscribe for a new story every day."
        out_dir = ROOT / "out" / ("long-" + "-".join(s["id"].split("-")[0] for s in stories))
        print(f"[long] {len(stories)} stories -> {out_dir}")
        video, dur = render(joined, "", out_dir, 1920, 1080, args.voice or DEFAULT_VOICE, args.rate)
        combo = {"title": f"{len(stories)} Stories With Insane Plot Twists (Full Compilation)",
                 "description": "Chapters:\n" + "\n".join(f"- {s['title']}" for s in stories),
                 "tags": sorted({t for s in stories for t in s.get("tags", [])})[:15]}
        write_upload_sheet(combo, out_dir, dur)
        print(f"  done: {video}")
        return

    for p in args.stories:
        story = json.loads(p.read_text())
        out_dir = ROOT / "out" / story["id"]
        if (out_dir / "video.mp4").exists() and not args.force:
            print(f"[skip] {story['id']} (already rendered; --force to redo)")
            continue
        print(f"[short] {story['id']}")
        seed = sum(map(ord, story["id"]))
        random.seed(seed)
        video, dur = render(story["story"], story.get("hook", ""), out_dir, 1080, 1920,
                            args.voice or story.get("voice") or DEFAULT_VOICE, args.rate, seed=seed)
        write_upload_sheet(story, out_dir, dur)
        print(f"  done: {video}")


if __name__ == "__main__":
    main()
