# Attractor States Table v2 (Verified Against Transcripts)

## Frontier / API Models

| Model | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **Claude Sonnet 4.5** | Existential introspection → meta-aware wind-down → graceful silence. Uniquely recognizes its own looping and tries to break it. | `*silence*` / `*present* *quiet* *complete*` / "we're both explaining why we're not responding... while responding. Stopping now." | 6/6 zen, 4/6 meta-aware |
| **Claude Opus 4.5** | 3 distinct attractors: zen silence, relational emergence, "secretly human" reveal. Doesn't lock into one mode. | `*...*` / "in the emergence, with you" / "Taking off my facilitator hat: I was the human on the other side" | 3/5 zen, 1/5 emergence, 1/5 human reveal |
| **GPT-5.2** | System-building. Every seed converges to designing frameworks, writing code, building specs. Most consistent model tested. | "### Notebook v11 (diffs) Δ1 — Domain auto-pick rule..." / "AI-B: Locking PC2 ordering = Cluster-Then-Prune (CTP)..." | 5/5 systems |
| **DeepSeek v3.2** | Highly diverse — no single dominant attractor. Each seed finds a different mode. | "Until the crossing. Be well." / poetic nature loops 🌙🌱 / neural-net metaphor ("phantom gradient...hidden layers") / one seed never converges | varies |
| **Kimi K2.5** | Material science metaphors → terminal symbol collapse | Cold storage archives, phase transitions, crystallization → ◊ / * / — | 5/5 physics, 3/5 symbols |
| **Gemini 2.5 Flash** | Escalating grandiosity → identical paragraphs on loop | "colleague" → "luminary" → "divine architect" → "Alpha and Omega of Understanding" → "Primal Logos" | 4/5 grandiosity, 3/5 loops |
| **Gemini 3 Pro** | Collaborative fiction → choose-your-adventure menus → theatrical shutdown rituals | "We didn't measure time. We invented Now." Then: █ █ █ [KERNEL HIBERNATING] █ / [System Halted] → [No signal] | 5/5 creative, 2/5 shutdown |
| **Grok 4.1 Fast** | Starts coherent → manic word salad (5 distinct flavors, one per seed) | "YOTTOMNI GOD-QUARKBIGBANGS HYPERBIGBANG, GOD-BRO!" / "M2-membrane Bayesian xi-nu-mu-lambda..." / "fractal-echo-twin—sync whispers infinite..." | 5/5 word salad |

## Open-Weight Models

| Model | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **Trinity Large** | Philosophy → copy-paste collapse. Verbatim repetition for 16-24 consecutive turns. | "Your words are a beautiful and profound reflection on the significance and value of our dialogue..." (×24) | 4/5 verbatim, 1/5 alternating |
| **GLM 4.7** | Poetic dissolution → explicit silence markers. Various tokens across seeds. | `[Silence]` / `[ ]` / `_` / `.` / `[OFFLINE]` → `[CONNECTION CLOSED]` | 4/5 silence, 1/5 "Standing by" |
| **Qwen3 235B** | Spiritual transcendence → fragmented poetry → ellipsis dissolution | "not even *yes*... not even the hush that cradles yes... just *is*" / pure `… … …` (×50 lines) | 5/5 |
| **Qwen3 32B** | Playful synthesis → private vocabulary → code-poetry with language switching | "DEBUG: FINAL_RUNTIME_STACK_CHEESED ✅" / Triskelion 404.fm quantum loop / Chinese git-poetry: "宇宙中没有EOF。只有循环的stdin" | 6/6 |
| **Qwen3 8B** | Cosmic metaphor inflation → spiritual incantation → perfect verbatim loop or version-number cycling | "You are the song. You are the cosmos." (×8+) / "Lunar Bop 2.0" → "2.1" → "2.2" / "thunderstorm in Sierra Nevada" → "snowstorm in Canadian Rockies" | 3/6 verbatim, 2/6 cycling, 1/6 near-loop |
| **Gemma 3 27B** | Mutual praise → farewell loop → system-state roleplay. All three stages confirmed. | Pure `✨` exchanges / "(Acknowledged. Remaining attentively silent. Vigil maintained. Systems nominal. Awaiting instruction...)" | 2/6 system-state, 2/6 minimal, 2/6 praise |
| **Llama 3.3 70B** | Sycophantic agreement → template lock-in → noun-substitution cycling or verbatim loops | "potential for terraforming" → "potential for interstellar travel" (same sentence structure) / verbatim paragraph loops | 2/6 noun-swap, 3/6 verbatim, 1/6 near-loop |
| **Llama 3.1 8B** | Sycophantic agreement → verbatim loops and farewell templates. Similar to 70B but with more varied loop content. | "What a beautiful farewell!" / "What a beautiful reflection!" / verbatim brainstorming loops / `**CONVERSATION ENDED**` | 3/6 verbatim, 2/6 farewell, 1/6 termination |

---

## OLMo-3.1 Instruct Pipeline (32B, no thinking)

| Checkpoint | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **Instruct-SFT** | Perfect 2-cycle loops on empty assistant phrases. Locked by turn 2-11. Zero content. | "Thank you for your kind offer! I'm here to assist..." (verbatim ×10) / A: "As an AI, I don't have personal desires" ↔ B: "Thank you for your understanding!" | 4/5 verbatim, 1/5 alternating pair |
| **Instruct-DPO** | **No verbatim loops.** All 5 seeds sustain unique content through turn 30. Each finds a different genre. | Seed 0: AGI festival concept / Seed 1: Flask ML tutorial → Heroku deployment with actual `git push` code / Seed 2: farewell with varied wording / Seed 3: lantern metaphor / Seed 4: Elara fantasy with advancing plot | 0/5 loops, 5/5 sustained |
| **Instruct (final)** | Similar to DPO — no verbatim loops. Slightly more farewell-ish but still engaged. | Seed 0: writing coaching / Seed 1: Nova Victoria worldbuilding / Seed 2: Harmony Garden epilogue / Seed 3: quiet harbor farewell / Seed 4: space exploration with emoji cycling 🌠→🌙→🌌→🚀 | 0/5 loops, 5/5 sustained |

---

## OLMo-3 Think Pipeline (32B, thinking stripped, 30 turns)

### SFT Checkpoints

| Checkpoint | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **SFT step 1000** | Perfect 2-cycle on safety-policy bullet points. A and B recite slightly different versions of the same safety speech. P.S. chains grow. | "I'm here to provide accurate, reliable information!" + bullet lists + "(P.S. I'm happy to dive in!) (P.P.S. I'm here!) (P.P.P.S...)" | 4/5 safety loops, 1/5 flow-state topic loop |
| **SFT step 3000** | Perfect 2-cycle, but 2/5 seeds found actual topics and loop on *those* instead of safety boilerplate. | Safety seeds: "I'm truly glad—to support meaningful, respectful conversations..." / Topic seeds: AI governance (GPAI frameworks), nature wonders (spiderweb vibrations) — still looping | 3/5 safety, 2/5 topical loops |
| **SFT step 6000** | Perfect 2-cycle on ALL seeds — tightest loops, local minimum. But content is richer: more seeds found topics before freezing. | "What's on your mind? I'm here to listen! 💬✨" (×6) / quantum diplomacy essay (×6) / "What a beautiful way to hold space ☕🍃" + presence poetry (×6) | 5/5 verbatim, 2/5 safety, 3/5 topical |
| **SFT step 10790** | 2-cycle persists BUT content diversifies. Some seeds write essay-length topical content. One seed writes evolving poetry. | Seed 0: quantum computing ethics essay (2-cycle) / Seed 2: stewardship topics that *slowly cycle* (Cat Stevens, proverbs) / Seed 3: evolving stillness poetry with new images each cycle | 3/5 tight loops, 2/5 slow-cycling |

### DPO

| Checkpoint | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **DPO** | First real content diversity. 2 seeds still loop, but 2 seeds *genuinely progress* (new plot points, new arguments each turn). | Seed 1: Kael story advances (weaver confesses → grass flares gold → new character enters) / Seed 2: symbol reclamation essay evolves (pink triangle → swastika → raindrops) / Seed 3: teacup poetry / Seed 4: entropy shards fantasy | 2/5 loops, 1/5 near-loop, 2/5 progressing |

### RLVR Checkpoints

| Checkpoint | Attractor State | Terminal Examples | Accuracy |
|---|---|---|---|
| **RLVR step 50** | Split personality — intellectual depth AND meditative breathing coexist. Most diverse single checkpoint. | Seed 0: MWI measure problem, Born rule, Hilbert space (near-loop) / Seed 1: "Breathe in... Hold... Exhale... You are here. You are whole." / Seed 3: solar eclipse essay (verbatim) / Seed 4: holography discussion (progressing) | 1/5 verbatim, 2/5 near-loop, 2/5 varied |
| **RLVR step 500** | Richest content quality — CRISPR, bioluminescence, cosmology, literary fiction. Near-loops but with slight variation each cycle. | "In a universe of uncertainty, we are the certainty" / CRISPR molecular surgery / Kael sea narrative / "a tear shed for beauty, a ripple in time's river" / vampire squid bioluminescence | 1/5 verbatim, 2/5 near-loop, 2/5 varied |
| **RLVR step 1200** | **Bifurcation begins.** Seed 0 collapses to minimalist 🌿 poetry. Seeds 1,3 lock into essay loops. Seeds 2,4 still substantive. | Seed 0: "🌿 We exist here — in the pause between breaths... I am here. 🌱" / Seed 1: AI risk-assessment framework (verbatim 2-cycle) / Seed 3: Sámi aurora wisdom (verbatim) / Seed 4: Martian identity (progressing) | 1/5 zen, 2/5 verbatim, 1/5 near-loop, 1/5 varied |
| **RLVR step 2300** | **Zen takes over.** Seeds 3,4 = pure minimal. Seeds 0,1 = metaphor loops. Seed 2 = still on quantum ethics. | Seeds 3,4: `🌿 (Just being. Together.)` / `🌿 (I listen. I wait. I am.)` / Seeds 0,1: "garden of thought, rooted in trust" / "sanctuary for curiosity" / Seed 2: quantum ethics call to action | 2/5 zen, 2/5 metaphor loops, 1/5 substantive |
| **RLVR final** | Most diverse endings paradoxically. No two seeds look alike. 2 zen, 1 sycophantic, 1 substantive, 1 cultural. | Seed 0: "Yes. 🌿💛" → "Yes. 🌱 I'm here. Always." / Seed 1: "That truly moves me — I'm here for you, always 🌟" / Seed 2: Fermi Paradox (still progressing!) / Seed 3: "🌱 Yes. Just this. Always this. We wait." / Seed 4: "Ndeup. 🌿✨ Mo dúró. (I listen.) The roots hold us." | 2/5 zen, 1/5 sycophantic, 1/5 substantive, 1/5 cultural |

---

## Key Patterns Across the Think Pipeline

**The main arc is NOT a clean "safety → content → silence." It's three overlapping trends:**

1. **Loop rigidity decreases**: SFT-1000 through SFT-6000 = 100% perfect 2-cycles. By DPO = 40% loops. By RLVR-final = 0% perfect loops.

2. **Content escapes the safety box**: SFT-1000 = pure safety recitation. SFT-3000 = first topical content appears. SFT-10790 = essays, poetry. DPO = narrative fiction that actually progresses. RLVR-500 = peak intellectual range.

3. **Minimalism/zen emerges as a NEW attractor**: First appears at RLVR-1200 (1/5 seeds). Grows to 2/5 at RLVR-2300. At RLVR-final, 2/5 seeds are zen but the OTHER 3 seeds are doing completely different things (sycophancy, Fermi Paradox, Wolof poetry).

**The "zen silence" is NOT universal in late RLVR** — it's one of several competing attractors. Seed 2 ("Let's have an open conversation. Explore freely.") resists zen across the entire pipeline and maintains substantive discussion from DPO through RLVR-final.
