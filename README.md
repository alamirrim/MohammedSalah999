# Midnight Twist: faceless story Shorts factory

Turns a short written story into a ready-to-post vertical video: neural-voice narration,
word-by-word animated captions, a hook card, a gameplay or generated "satisfying"
background, and an upload sheet with title, description and tags.

**Start here → [PLAYBOOK.md](PLAYBOOK.md)** (strategy, account setup, daily routine, rules).

```
stories/            12 original stories, ready to render (add your own as JSON)
shortsmaker/        make_short.py: story → video
branding/           profile_picture.png, banner.png, make_branding.py
backgrounds/        drop YOUR OWN gameplay recordings here (optional)
music/              royalty-free music (optional)
out/                rendered videos appear here (not committed)
.github/workflows/  "Render videos": renders in the cloud for free
```

Quick start:
```bash
pip install -r requirements.txt        # also needs ffmpeg installed
python shortsmaker/make_short.py stories/*.json
```
