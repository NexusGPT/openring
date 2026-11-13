# Standing rules for every helper on this build

| # | Rule | Source |
|---|---|---|
| 1 | Tests run headless only. Never open a visible browser window. | Cue, the owner's standing rule recorded before this project: "Headless tests only" |
| 2 | During the build the app is shown on localhost only (http://localhost:8790). No helper publishes or hosts anything: putting it online is a later step the lead runs with the owner. The build must still work from a plain static host under a sub-path. | rule docs/PRD.md:21 |
| 3 | No ring fact (part name, number, size, state name) is written in app source. Every value comes from the data bundle built by `npm run collect`. | Cue, the build plan the owner approved in plan mode on 2026-11-10 says "A guard against stale facts" |
| 4 | The app is read-only. It never writes to the design files. | rule docs/PRD.md:27 |
| 5 | The quality bar is the owner's word "slick", in the style S1 Gallery; never "A cluttered dashboard, A wall of text, A toy". | rule docs/DESIGN.md:22 |
| 6 | The disk has under 5 GB free. One `npm install` in the explorer folder, by the contract piece only. No second copy of node_modules, no worktree, no file over 20 MB. | Cue, measured 4.6 GB free on 2026-11-10; the owner approved the plan's "Risks: Disk space" |
| 7 | Helpers work in one shared copy of the repository. A helper writes only the files its row in docs/lane-dag.json owns, and never runs git commit, stash, reset or checkout: the lead commits. | Cue, the build plan the owner approved on 2026-11-10 says "Helpers work in one shared copy, each on its own files" |
| 8 | A screen whose source is missing, unreadable or made for an older design says so in words and still shows its content. | Cue, the build plan the owner approved on 2026-11-10 says "Honest screens during the redesign" |
| 9 | No file loads from the internet when the app runs. | rule docs/PRD.md:30 |
