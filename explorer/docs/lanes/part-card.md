# Digest: part-card lane

Files: `src/components/PartCard/` (PartCard.tsx, ExactData.tsx, model.ts, PartCard.css, index.ts, `__tests__/` with 10 checks part-card-C01..C10, sample data, headless harness).
Use: `<PartCard route partId line note legend files areaState banner />`; test id `<route>.part-card`. Pure props, no fetch; the host reads parts, part-notes, files via `useRecord`.
Proofs in `_captures/part-card/`: MUTATION-LOG.md (6 mutations, each seen red, restored), cards-closed.png, cards-open.png, s1-board.png.
Choices: (1) the maker part number is under Exact data only (brief), so the Order row says "Order code is under Exact data" when a code exists, "Open: <action>" when an action is open, else "No order code yet". (2) Disclosure is hand-rolled (button + aria-expanded, closed = absent from DOM), not the kit accordion: the S1 card needs exact tokens and a closed panel that holds no text. (3) A path is linked only when on_disk and listed in files.json. (4) docs/DIGEST.md is in the brief's must-not-touch list, so this section lives here.
