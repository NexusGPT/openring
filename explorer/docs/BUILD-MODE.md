# BUILD-MODE — ring-explorer
| Row | Value |
|---|---|
| Build | `build-started: 2026-11-10T14:51:58.791Z` (the owner's ask: "I want in my browser a full app that allows me to go and see the design, internal, PCB, etc. and have EVERYTHING so I know what I'm building myself") · `seed: none (new app); code seed: the 3D look viewer design/look/viewer at commit 99dfb85` |
| Archetype | 3 (a person opens it in a browser), local only |
| Path | ENGINE |
| Authority | ENGINE: first `app-architect` dispatch this session (explorer-architect, 2026-11-10); plan approved by the owner in plan mode 2026-11-10 |
| Solo exception | Three changes written by the lead with no crew, on the owner's go of 2026-11-10 (card answer): "Yes, do them yourself (Recommended)". Scope of that go, nothing more: (1) the case drawn with real materials, (2) the Behaviour screen without the separate record button, (3) the Files screen saying what the public copy leaves out. Checked without a browser: type check, generated-types check, guard, unit tests, reader tests. |
| Lanes + models | `lanes: architect=1 · contracts=1 · executor=1 · tests=1 · tester=1 · reviewer=7 · assessor=20 · taste=1` plus 30 build pieces from docs/lane-dag.json run by builder seats (at most 6 at a time, one shared copy: disk has 4.6 GB free) · `models: executor=sonnet · contracts=sonnet · reviewer=sonnet · assessor=sonnet · director=opus · architect=pinned · taste=opus · tester=sonnet` (owner's standing rule: helpers never run on the lead's model; implementation and tests on opus or sonnet) |
| Units + artifacts | `units: 52 · artifacts: 30` (30 pieces with pairwise-disjoint files; 22 units merged into a piece, each with its written reason in docs/plan.json) |
| Bar | `bar: 9/10` — the owner's words on the ring apply to the app: "slick", "like the ring design I gave" |
| Disclosure given | "This is a multi-hour build. SPAN: no comparable build measured in this project; expect hours. CREW: 30 build pieces, at most 6 at a time, then review seats per screen; step 1 (about 10 pieces) runs alone first and its measured usage is reported before steps 2 to 8. CADENCE: http://localhost:8790 from step 1, re-shared at each step; a status line in chat at each wave. YOUR PART: interrupt for a scope change or a wrong direction; otherwise it runs unattended." |
| Preview owner | the lead serves and re-shares http://localhost:8790 |
| Verified by | `verified: journeys=INDEPENDENT · captures=SELF · deploy=OWNER · gate=INDEPENDENT` (deploy = the owner opens localhost; nothing is hosted) |
| Repo | inside the project repository . (git from creation) ✓ |
| Test engine | `test-engine: playwright · reason: owner chose hand tests "Approve the spec (Recommended)" on the spec whose test plan reads "End-to-end: one test per journey with headless Playwright"` |
| Contract deltas since PRD sign-off | listed, all approved by the owner in plan mode 2026-11-10 ("My readings, used unless you change them", plan approved): (1) JOURNEYS J7.1 transfer figure 6.4 → 6.3 minutes per recorded hour; (2) DATA-MAP blocks come from the 7 schematic sheets; (3) DATA-MAP part-notes gain model_names; (4) a top-bar entry "Files" on the Open items and files route; (5) journeys run on a frozen copy of design A3 (commit 99dfb85 plus look C) |

## Fates (declared-vs-fired, reconciled at every wave boundary)

| Lane class | Declared | Fired | Fate | Evidence / user's quoted drop |
|---|---|---|---|---|
| architect | 1 | 1 | done | docs/plan.json, docs/plan-notes.md |
| contracts | 1 | 0 | next | |
| executor / build pieces | 30 | 0 | after the contract | |
| tests | 1 | 0 | with step 1 | |
| tester | 1 | 0 | step 1 close | |
| reviewer | 7 | 0 | step 1 close | |
| assessor | 20 | 0 | step 1 close | |
| taste | 1 | 0 | after the review loop | |
