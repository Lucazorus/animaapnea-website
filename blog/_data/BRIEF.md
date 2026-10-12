# Anima Apnea blog: writing brief (shared by all agents)

Site root: `/Users/lucasmassoni/Dev/animaapnea-website`. Blog: `blog/<lang>/<slug>`.
Languages (14): en fr es de it pt ja zh da nl hi id th vi.
Slug registry (source of truth for every URL): `blog/_data/slugs.json` (article id → lang → file name).

## The reference page

`blog/fr/comment-faire-table-co2-apnee-statique.html` is the finished, approved prototype.
**Read it in full before writing anything.** Every page must reuse its exact skeleton, class names,
scripts and stylesheet links (`../style.css`, `../article.css`, `../lang.js`, `../article.js`),
the brand nav, the hero (breadcrumb, kicker, h1, dek, byline), the 2-column layout with the sticky
TOC, and the closing blocks in the same order: CTA (`.cta-app`), sources (`.refs`), author box,
related articles (`.related`).

## Head requirements

- `<html lang="xx">`, `<title>` (≤ 65 chars, ends with ` | Anima Apnea`), `<meta name="description">` (140–160 chars).
- `<link rel="canonical" href="https://www.animaapnea.com/blog/<lang>/<slug>">`
- Then a single line `<!--ALTERNATES-->` (a build script inserts all hreflang links there; do NOT write hreflang links yourself).
- OG tags as in the prototype (og:locale in the right locale), favicon `/logo-256.png`.
- JSON-LD `@graph` with Article (datePublished: keep `2026-04-12` for the 7 existing articles, `2026-10-12` for new ones; dateModified `2026-10-12`; inLanguage), BreadcrumbList, and FAQPage whose questions/answers are **identical** to the visible FAQ.
- Same Google Fonts link and stylesheets as the prototype.

## Components available (see `blog/article.css`, `blog/article.js`)

- `.takeaways` (3–5 bullets), `.stats` (exactly 3 `.stat`), `blockquote.pull` (max 1 per article)
- `.callout.tip` (ic "i"), `.callout.science` (ic "✓"), `.callout.warning` (ic "!")
- `ol.steps` — only for content that really is a sequence
- `.data-table` with `<caption>`, optional `td.hl`, `tfoot`
- `.faq` with `<details><summary>` (4–6 questions)
- Figures: `<figure class="fig">` (or `fig bleed` for wide charts) with `.fig-head` (`.fig-title` + optional `.fig-legend`) and a `<figcaption><b>Figure N.</b> …</figcaption>`.
  - JS charts, labels passed as JSON in `data-labels` (translate them!):
    - `data-chart="timeline"` + `data-rounds='[[rest,hold],…]'` (seconds) + optional `data-kind="o2"` (green holds)
    - `data-chart="blood-gas"` labels: aria, urge, bp, easy, struggle, time, co2, o2
    - `data-chart="week"` + `data-days='[{"d":"Mon","t":"CO2","k":"co2|o2|rest","v":0..1},…]'`
  - Calculators: `<div class="calc" data-calc="co2|o2">` exactly like the prototype markup (range input, `.calc-pr`, 3 `.calc-out` cells, `.calc-chart`, `.calc-note`). The O2 calculator ends at ~80 % of the record: do NOT say it uses the app's formula.
  - Hand-drawn inline SVG diagrams are welcome (see Figure 1 in the prototype). Use ONLY the theme classes
    `c-grid c-axis c-tick c-lab c-lab-strong c-rest c-hold c-hold-o2 c-co2-line c-o2-line c-co2-area c-warn c-warn-t c-zone c-node c-node-accent c-arrow c-arrow-head c-dot`
    or `style="fill:var(--co2)"`-type CSS variables (`--co2 --o2 --warn --danger --rest --grid`). Never hard-code colours: the page has a dark and a sepia theme. Give each SVG a `viewBox`, `role="img"` and a translated `aria-label`. Unique marker ids per page.
- Every article needs **at least 2 figures**, and at least one must be a genuine diagram or chart that explains something (not decoration). Charts must show real protocol data or clearly-labelled schematic physiology ("Représentation schématique" / "Schematic"). Never invent survey numbers, user statistics or study results.

## Voice and content rules

- Expert, precise, calm, practical. Written for an intelligent beginner-to-intermediate freediver. Address the reader directly (FR: vouvoiement).
- 1 800–2 600 words of body text. Sentence-case headings. No ALL CAPS, no emoji, no section numbers, no exclamation marks, no hype ("ultimate", "secret", "game-changer").
- h2s get short ascii `id`s, and the TOC lists exactly those h2s (excluding FAQ is fine but keep `#faq`).
- Every factual physiology claim should be either common textbook knowledge or backed by a numbered source `<sup class="ref"><a href="#ref-N">N</a></sup>`.
- Sources: 3–6 **real** publications you are certain exist (authors, title in italics, journal, year; no DOIs or page numbers unless you are sure). Good, verified ones include:
  - Lindholm P, Lundgren CEG. The physiology and pathophysiology of human breath-hold diving. J Appl Physiol, 2009.
  - Bain AR, Drvis I, Dujic Z, MacLeod DB, Ainslie PN. Physiology of static breath holding in elite apneists. Exp Physiol, 2018.
  - Dujic Z et al. Involuntary breathing movements improve cerebral oxygenation during apnea struggle phase in elite divers. J Appl Physiol, 2009.
  - Craig AB Jr. Causes of loss of consciousness during underwater swimming. J Appl Physiol, 1961.
  - Schagatay E. Predicting performance in competitive apnoea diving. Part I: static apnoea. Diving Hyperb Med, 2009.
  - Gooden BA. Mechanism of the human diving response. Integr Physiol Behav Sci, 1994.
  - Foster GE, Sheel AW. The human diving response, its function, and its control. Scand J Med Sci Sports, 2005.
  - Engan H et al. Effects of two weeks of daily apnea training on diving response, spleen contraction, and erythropoiesis in novel apneists. Eur J Appl Physiol, 2013.
  - Ma X et al. The effect of diaphragmatic breathing on attention, negative affect and stress in healthy adults. Front Psychol, 2017.
  - Zaccaro A et al. How breath-control can change your life: a systematic review on psycho-physiological correlates of slow breathing. Front Hum Neurosci, 2018.
  If you are not sure a paper exists, do not cite it. If unsure of a number, do not give it.
- Safety is non-negotiable in every article: dry training alone only lying/sitting; never in water without a trained buddy watching; never hyperventilate; stop on warning signs; medical advice for heart/lung conditions, epilepsy, pregnancy. At least one `.callout.warning`.
- Depth topics (equalization, dive reflex): recommend a certified course (AIDA, Molchanovs, SSI, PADI Freediver…) for anything done in water.

## Verified facts about the Anima Apnea app (claim nothing else)

- iPhone app, free download; some customization is Premium. App Store: `https://apps.apple.com/app/anima-apnea/id6760680506`
- Static apnea timer; you tap to mark each contraction; records the first-contraction time; personal records; session history.
- CO2 table adapted to the record: hold ≈ 50 % of PR, first recovery ≈ 2/3 of PR but never under 2:00, rounded to 15 s, −15 s per round, never under 15 s, 8 rounds. O2 table: fixed 2:00 recovery, first hold ≈ 33 % of PR, +15 s per round, last hold capped at 85 % of PR. Both editable (holds, recovery, rounds).
- Sound and haptic cues during sessions.
- Guided breathing: diaphragmatic (4 s in / 8 s out), box breathing (4-4-4-4), 4-7-8, and custom patterns. Breathe-up before holds.
- 4-week training plans, 3 to 6 sessions a week, record attempts at the end of weeks 2 and 4.
- Stats/charts by day, week, month (holds, tables, contractions); streaks; daily reminders; home-screen widget.
- Optional sign-in with Apple or Google for cloud sync; works without an account.
- It does NOT measure heart rate or SpO2, does NOT use sensors, has NO Apple Watch app (do not mention a watch), NO Android version.

## Byline / author box (translate)

Byline: initials avatar "LM", "Lucas Massoni", "Founder of Anima Apnea", "Updated 12 October 2026" (localized date), "N min read".
Author box text: "Creator of Anima Apnea, the static apnea training app. He writes about method, physiology and safety in breath-hold training." Do not invent credentials.

## Related articles

4 links in `.related-grid`, to other articles in the SAME language, using file names from `slugs.json`. Each link: `<span class="k">Category</span><span class="h">Title</span>`.
Also link 2–4 times in the body to other articles of the series, naturally.

## Translations

Native-quality, idiomatic, culturally adapted (not literal). Translate everything: text, data-labels JSON, aria-labels, figcaptions, SVG text, FAQ JSON-LD, title/description, breadcrumb. Keep the same structure, figures, data, sources (source titles stay in English). Keep `<!--ALTERNATES-->`. Use the locale's date format and number conventions. For ja/zh/th/hi use natural typography for that script.

## Before finishing each page

Run `python3 blog/_data/check.py <file>` and fix every reported problem.

## Colours = the app's palette and meanings (mandatory)

Charts and diagrams use the Anima app's own colours (lib/theme/app_colors.dart) with the same meaning as in the app:
- `--co2` cyan #6F9CAF: CO₂ table, CO₂ curves, main accent
- `--o2` aqua #6FAFAC: O₂ table, O₂/SpO₂ curves
- `--teal` #70AAAF: box breathing / secondary accent
- `--breath` green #70AF84 and `--rest`: recovery, breathing, rest days
- `--apnea` / `--warn` yellow #FFCF56 (sepia #BF8705): apnea time, records, contractions, "urge / first contraction" markers
- `--danger` red #FF5252: blackout risk zones only
Helper classes: `c-apnea`, `c-breath`, `c-danger` (fills), `c-apnea-line`, `c-danger-line` (strokes) in addition to the ones listed above. Never use any other colour.
