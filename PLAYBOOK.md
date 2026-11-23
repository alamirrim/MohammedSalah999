# The Playbook: Faceless Story Shorts → Real Money

A step-by-step plan for a faceless channel that posts short, addictive story videos
(narration + big captions + gameplay or "satisfying" background) on YouTube Shorts,
TikTok, Instagram Reels and Facebook Reels, and earns from all four.

---

## 0. Reality check (read this first)

| Fact | What it means for you |
|---|---|
| YouTube Shorts pays about **$0.03–$0.10 per 1,000 views**. | 1 million views ≈ $30–$100. An iPhone (~$1,000) takes roughly **10–20 million monetized views**. |
| YouTube monetization needs **1,000 subscribers + 10M Shorts views in 90 days** (or 4,000 long-form watch hours). | You earn **$0** until you qualify. Expect 2–6 months of daily posting. |
| TikTok Creator Rewards pays about **$0.40–$1.00 per 1,000** views, but only on videos **over 60 seconds**, and needs 10k followers + 100k views/30 days, age 18+, and a supported country. | That's why every story here runs 60–75 seconds. Check that your country is eligible. |
| Long-form YouTube (8+ min) pays **$2–$5 per 1,000** in this niche. | Once a few Shorts pop, post **story compilations** (`--long`). This is where the real money is. |
| Since **July 2025/2026, YouTube refuses to monetize "inauthentic" content**: mass-produced, template-identical, low-effort AI videos. Review happens **channel-wide**. | Don't spam 20 identical videos a day. Original stories, varied backgrounds, real editing choices. Details in section 5. |

**Honest timeline:** month 1 = learning, mostly small views. Month 2–3 = one video pops
(100k–1M+), subs jump. Month 3–6 = monetization. The people who make money are the ones
who post every day for 90 days. Most quit in week 3.

---

## 1. The format (why these videos are addictive)

1. **Hook in the first second.** The first spoken line and the white hook card say the
   most shocking part of the story. No intros, no "hey guys".
2. **Big word-by-word captions**, current word in yellow. People watch on mute and read along.
3. **Hypnotic background** (gameplay or the generated bouncing-ball sim) keeps eyes busy so
   the brain stays for the story.
4. **Twist ending**, and where possible a **loop**: the last line flows back into the first
   (see `001-sister-wedding`), so viewers re-watch without noticing. Replays boost reach.
5. **60–75 seconds**: long enough for TikTok rewards, short enough to finish.
6. **"Part 2" bait.** End some stories with an open door (`008-basement-door`). Comments
   asking for part 2 = a guaranteed audience for the next video.

---

## 2. Set up the accounts (≈30 minutes, you have to do this part)

I can't create accounts for you. Google requires phone verification, and automated account
creation breaks their terms (it gets channels banned). Do this yourself:

1. **New Gmail** just for the channel (keeps it separate, and it's sellable later).
2. Go to youtube.com → profile → **Create a channel**. Use a custom name (this makes a
   Brand Account, so you can add helpers later).
3. **Name:** `Midnight Twist`. If it's taken, try `Twist Theory Stories`,
   `One Minute Twists`, or `Plot Twist Hour`. Make the **@handle** match.
4. **Profile picture:** `branding/profile_picture.png`. **Banner:** `branding/banner.png`.
   To make them for another name: `python branding/make_branding.py "Your Name"`.
5. **Channel description:**
   > A new story with a twist, every single day. Wholesome, creepy, petty revenge: you
   > won't see the ending coming. All stories are fictional and written for entertainment.
6. **Verify the channel** (YouTube Studio → Settings → Channel → Feature eligibility →
   phone). This unlocks custom thumbnails and longer videos.
7. Make the **same name on TikTok, Instagram and Facebook** with the same picture.
   Same videos, four platforms, four times the chances to go viral.

---

## 3. Make the videos

### Option A: run it on your own computer (Windows/Mac)
```bash
# one-time: install Python 3.12 + ffmpeg, then:
pip install -r requirements.txt
python shortsmaker/make_short.py stories/*.json      # makes all 12 videos into out/
```
Each `out/<story>/` folder has `video.mp4`, `cover.jpg` and `upload.txt`
(title, description, tags and settings, ready to copy and paste).

### Option B: let GitHub make them for free (works from a phone)
Repo → **Actions** → **Render videos** → **Run workflow**. When it finishes, download the
`videos` zip at the bottom of the run page. It also runs automatically when you add a story.

### Use Roblox / Minecraft gameplay (recommended after the first week)
Record **your own** 20–30 minutes of a parkour/obby game with OBS (free). No talking,
1080p. Drop the file in `backgrounds/`. The script picks a random slice for each video.
**Never download someone else's gameplay from YouTube**: that's "reused content" and gets
you demonetized and copyright-struck. Roblox's terms allow you to monetize videos of your
own gameplay. Mix it up: some videos on gameplay, some on the ball sim.

### Music (optional)
Put royalty-free tracks in `music/` (YouTube Studio → Audio Library is free and safe).
They're mixed in quietly under the voice. On TikTok you can add a trending sound in the app
instead, at 3–5% volume.

---

## 4. The automated weekly cycle

| Who | What | When |
|---|---|---|
| Claude (scheduled task) | Writes 7 new original stories, checks them, pushes them to the repo | Every Friday evening |
| GitHub Actions | Renders only the new stories with natural voices | Automatically, ~15 min after |
| **You (~20 min)** | Download the `videos` zip → schedule all 7 in YouTube Studio, TikTok (desktop scheduler), Meta Business Suite (Instagram + Facebook) | Once a week |

**Why you still press "schedule":** YouTube and TikTok lock videos uploaded by unapproved
apps to *private*. Once the channel has real traction, we apply for API approval, and then
uploading can be fully automatic too.

## 4b. Daily routine

| Time | Do |
|---|---|
| Once a week | Write or generate 7–14 new stories (section 6) and render them. |
| Every day | Post **1–2 Shorts** on YouTube, the same video on TikTok/Reels/FB. |
| Right after posting | Pin the comment from `upload.txt`. Reply to the first 10–20 comments in the first hour. |
| When a video pops | Make a part 2 / a similar story **within 48 hours**. Reply to the top comment with a video. |

**Best posting times:** when your audience is awake. Start with US evenings, about
6–9 pm Eastern (that's 3–6 am in the Gulf; use YouTube's *Schedule* button). After 2 weeks,
check Studio → Analytics → *When your viewers are on YouTube*.

**Upload settings (YouTube):** paste title/description/tags from `upload.txt` →
"Not made for kids" → under *Altered content*, answer honestly (AI voice or script alone is
usually "No"; realistic fake footage of real-looking people or events is "Yes") → Publish.

---

## 5. Rules that keep you monetized (don't skip)

- **Original stories only.** Don't copy Reddit posts word for word or re-upload other
  channels' videos. Use the stories here, write your own, or have AI draft them and then
  **edit them yourself**.
- **Vary things.** Rotate voices (`--voice`), backgrounds, story types. Never post 50
  near-identical videos. YouTube judges the **whole channel**.
- **1–3 posts a day, max.** Spamming gets you flagged as mass-produced.
- **No fake "true story" claims.** Description says it's fiction. Never use real people's names.
- **No buying views/subs, no sub4sub groups.** Fake engagement kills the algorithm and can
  get the channel terminated.
- **Don't pay for "faceless YouTube" courses.** Everything you need is in this repo.

---

## 6. Writing new stories (the real skill)

Copy any file in `stories/`, change the `id` (e.g. `013-...`), title, hook, story, tags.

**Formula:** Hook (most shocking line) → context in 2 sentences → escalation → twist →
one-line ending that loops or teases a part 2. **200–230 words** = 62–72 seconds (over 60s so TikTok Creator Rewards counts it).

**Prompt to give Claude (or any AI) for a batch, then edit what comes back:**
> Write 7 original, fictional short stories for 60–75 second narrated YouTube Shorts.
> 200–230 words each. First person, simple spoken English, short sentences. The first
> sentence must be the most shocking part of the story. Each needs a twist ending nobody
> sees coming, and the final line should loop back into the first line or tease a part 2.
> Mix the genres: 2 wholesome, 2 creepy (no gore), 2 petty revenge/karma, 1 workplace.
> No real people or brands. For each, also give: a YouTube title under 70 characters with
> a curiosity gap, a 10-word on-screen hook, 5 tags, and a pinned-comment question.
> Output as JSON matching this example: <paste one file from stories/>

**Titles that work:** a curiosity gap plus stakes. "My Landlord Had ONE Rule… I Broke It
on Night One." Use CAPS on 1–2 words, an ellipsis, and at most one emoji.

---

## 7. Reading the numbers (YouTube Studio → Analytics → each Short)

| Metric | Goal | If it's low |
|---|---|---|
| **Viewed vs. swiped away** | > 70% viewed | The hook is weak. Make the first line more shocking. |
| **Average % viewed** | > 80% (loops push it over 100%) | Cut the boring middle and get to the twist faster. |
| **Subs per 1,000 views** | > 2 | Add more part 2s and a series feel. |

Find your **best-performing genre after 20 videos** and make half your videos that genre.

---

## 8. Money roadmap

1. **0 → 1k subs:** post daily. Don't look at the money.
2. **YPP (Shorts revenue) + TikTok Creator Rewards:** first small checks.
3. **Long-form compilations:** `python shortsmaker/make_short.py --long stories/00*.json`
   makes a 16:9 compilation. Post 1–2 a week; long-form pays 30–50× more per view.
4. **Extra:** once you hit 10k+ followers, story-app and mobile-game brands pay for
   sponsored integrations. Put a business email in your channel description.

Rough math once it's working: 1 viral Short a week at ~1M views, plus steady compilations,
puts you in the **few hundred dollars a month** range. That's an iPhone in a few months and
a Mac a few months later. Treat these as rough numbers, not promises.
