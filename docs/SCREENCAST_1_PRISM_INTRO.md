# Screencast 1: Introducing PRISM
## Current Release Demo (Main Branch)

**Duration:** 8-10 minutes
**Target Audience:** RDA community, researchers, tool developers
**Goal:** Introduce PRISM and demonstrate core functionality

---

## Pre-Recording Checklist

- [ ] Clear browser cache and cookies
- [ ] Close unnecessary browser tabs
- [ ] Set browser zoom to 100%
- [ ] Disable browser extensions (or use clean profile)
- [ ] Check audio levels (speak clearly, no background noise)
- [ ] Have PRISM running on main branch
- [ ] Prepare example data/searches
- [ ] Turn off notifications (Do Not Disturb mode)
- [ ] Use cursor highlighting tool
- [ ] Set screen resolution to 1920x1080

---

## Script

### INTRO (30 seconds)

**[Screen: PRISM homepage]**

> "Hello! I'm [Your Name] from the MaLDReTH II RDA Working Group. Today I'm excited to introduce you to PRISM - the Platform for Research Infrastructure Synergy Mapping.
>
> PRISM is a web-based tool designed to help researchers discover and understand how digital research tools interact across the entire research data lifecycle. Let's explore what it can do."

**Action:** Slowly scroll down homepage to show overview stats

---

### SECTION 1: The Problem We're Solving (1 minute)

**[Screen: Still on homepage, highlight stats]**

> "The research data landscape is complex. There are over 1,000 digital tools available - from data collection platforms to preservation repositories - but it's incredibly difficult to know which tools work together, how they integrate, and where they fit in your research workflow.
>
> That's where PRISM comes in. We're building a comprehensive map of tool interactions across the 12-stage research data lifecycle defined by the MaLDReTH initiative."

**Action:** Point to the interaction and tool counts

---

### SECTION 2: The 12-Stage Lifecycle (1.5 minutes)

**[Navigate to: Research Data Lifecycle > Radial Visualization]**

> "Let me show you the MaLDReTH lifecycle model. This visualization shows 12 distinct stages that data goes through in research."

**Action:** Hover over each stage slowly, reading them aloud

> "From CONCEPTUALISE and PLAN at the beginning...
> Through COLLECT, PROCESS, and ANALYSE in the middle...
> To PRESERVE, SHARE, and ACCESS at the end...
> And finally TRANSFORM - completing the cycle for data reuse."

**Action:** Click on one stage (e.g., STORE)

> "Each stage contains multiple tools. For example, in the STORE stage, we have tools like iRODS, institutional repositories, and cloud storage platforms. These are color-coded and positioned to show relationships."

**Action:** Show the tool tooltips by hovering

---

### SECTION 3: Exploring Tools (2 minutes)

**[Navigate to: Tools > View All Tools]**

> "Let's explore the tool catalog. PRISM currently documents [X] research data tools, each with detailed metadata."

**Action:** Scroll through the tool list

> "You can filter by lifecycle stage, category, or search for specific tools. Let me search for a popular tool - Zenodo."

**Action:** Type "Zenodo" in search box

> "Here's Zenodo - a general-purpose open repository developed by CERN. Notice the information we capture: whether it's open source, its description, and most importantly - its interactions with other tools."

**Action:** Click on Zenodo

> "Each tool detail page shows:
> - Basic information and homepage link
> - Its position in the lifecycle
> - The category it belongs to
> - And critically - all the interactions where this tool is either the source or the target."

**Action:** Scroll to interactions section

> "For example, Zenodo interacts with GitHub for automatic archiving, with ORCID for researcher identification, and with various data analysis tools for data exchange."

---

### SECTION 4: Understanding Interactions (2 minutes)

**[Navigate to: View Interactions]**

> "Now let's look at interactions - the heart of PRISM. These document how tools actually connect and work together."

**Action:** Scroll through interaction list

> "Each interaction has a type - like API Integration, Data Exchange, or Metadata Exchange - and belongs to a lifecycle stage. Let me open a detailed example."

**Action:** Click on a well-documented interaction (e.g., GitHub → Zenodo)

> "This interaction shows GitHub automatically archiving repositories to Zenodo. Notice what we capture:
>
> - **The interaction type:** Data Exchange
> - **Lifecycle stage:** PRESERVE
> - **Description:** What happens and why it's useful
> - **Technical details:** How it works - in this case, GitHub webhooks
> - **Benefits:** Permanent preservation with DOIs
> - **Challenges:** Repository size limits
> - **Real examples:** Actual use cases"

**Action:** Scroll through all sections

> "This level of detail helps researchers understand not just *that* tools connect, but *how* they connect and whether it'll work for their needs."

---

### SECTION 5: Different Visualizations (1.5 minutes)

**[Navigate to: Research Data Lifecycle menu]**

> "PRISM offers multiple ways to visualize the tool landscape. We've seen the Radial view. Let me show you two others."

**Action:** Click on "Circular Visualization"

> "The Circular visualization arranges tools around the lifecycle stages in a ring, with arrows showing interactions flowing between tools."

**Action:** Zoom in on a section with interactions

> "This makes it easy to see bottlenecks - stages or tools with many connections - and gaps where integration is lacking."

**Action:** Navigate to "Network Visualization"

> "The Network view shows a force-directed graph where tools and stages attract and repel based on their relationships. This can reveal unexpected patterns and clusters."

**Action:** Let it settle, then drag a node

> "You can interact with the graph to explore different perspectives."

---

### SECTION 6: Contributing Your Knowledge (1 minute)

**[Navigate to: Add Interaction]**

> "PRISM is community-driven. If you know about a tool interaction that's not documented, you can add it. The form is straightforward:"

**Action:** Show the form (don't fill it completely)

> "Select your source and target tools, choose the interaction type and lifecycle stage, then describe what happens. You can add as much technical detail as you like - protocols, APIs, configuration steps.
>
> There's also support for bulk uploads via CSV for organizations that want to contribute their tool catalogs at scale."

---

### SECTION 7: Data Access (30 seconds)

**[Navigate to: CSV Tools > Export CSV]**

> "All PRISM data is openly accessible. You can export the entire interaction catalog as CSV for analysis in Excel, R, Python, or any other tool. This supports reproducible research and enables the community to build on our work."

**Action:** Show the export interface (don't actually download)

---

### OUTRO (1 minute)

**[Navigate back to homepage]**

> "So that's PRISM - a platform to discover, understand, and document how research data tools interact.
>
> Whether you're a researcher trying to find the right tools for your workflow, a tool developer wanting to highlight integrations, or an infrastructure provider mapping your ecosystem, PRISM provides the comprehensive view you need."

**Action:** Scroll to footer/about section

> "PRISM is an output of the MaLDReTH II RDA Working Group, and it's continuously growing. We invite you to:
>
> - Explore the catalog
> - Add interactions you know about
> - Share feedback on what's useful or missing
> - Join our working group to help shape the platform's future
>
> Visit the link below to get started, and thank you for watching!"

**[Screen: Show URL clearly]**

> "The URL is [show on screen for 3 seconds]"

**[Fade to end screen with:]**
- PRISM URL
- MaLDReTH II RDA link
- Contact email
- QR code

---

## Post-Production Notes

### Sections to Highlight
- 00:30 - Problem statement
- 02:00 - 12-stage lifecycle
- 04:00 - Tool exploration
- 06:00 - Interaction details
- 07:30 - Multiple visualizations
- 08:30 - How to contribute

### Annotations to Add
- Tool counts (update with current numbers)
- Interaction type definitions (tooltips)
- "Click here to try" call-to-action
- Social media handles

### Cursor Highlights
Use cursor highlighting for:
- Navigation clicks
- Search box entries
- Important UI elements
- Interaction arrows in visualizations

### Background Music
- Subtle, non-intrusive
- Royalty-free research/tech music
- Volume: 15-20% (don't overpower voice)
- Fade in/out at beginning/end

---

## Demo Data Setup

Before recording, ensure:
- At least 3-5 well-documented interactions visible
- Popular tools like Zenodo, GitHub, ORCID in catalog
- Radial visualization loads smoothly
- Search functionality works
- No test/dummy data visible

---

## Common Mistakes to Avoid

❌ **Don't:**
- Rush through visualizations - let them settle
- Use jargon without explanation
- Skip over the "why" (benefits of mapping)
- Forget to show how to contribute
- Record at odd screen resolutions

✅ **Do:**
- Speak slowly and clearly
- Pause briefly after clicking (let UI respond)
- Explain acronyms (RDA, ORCID, DOI)
- Show real, meaningful examples
- Test everything before recording

---

## Accessibility Considerations

- Use high contrast cursor highlighting
- Speak all text that appears on screen
- Describe visualizations for audio-only listeners
- Include captions/subtitles in final video
- Provide transcript in video description

---

## B-Roll Suggestions

If you want to add visual interest:
- Close-ups of interaction arrows in visualizations
- Zooming into tool details
- Quick montage of different lifecycle stages
- Split screen showing multiple visualizations
- Terminal/code snippets (if discussing technical details)

---

## Script Timing Breakdown

| Section | Duration | Cumulative |
|---------|----------|------------|
| Intro | 0:30 | 0:30 |
| Problem | 1:00 | 1:30 |
| Lifecycle | 1:30 | 3:00 |
| Tools | 2:00 | 5:00 |
| Interactions | 2:00 | 7:00 |
| Visualizations | 1:30 | 8:30 |
| Contributing | 1:00 | 9:30 |
| Data Access | 0:30 | 10:00 |
| Outro | 1:00 | 11:00 |

**Target:** 10 minutes (allows for natural pacing and pauses)
