# Lane notes: svg-viewer

Files: `src/components/SvgViewer/` (SvgViewer.tsx, SvgViewer.css, model.ts, index.ts, `__checks__/` with `SvgViewer.test.tsx` = svg-viewer-C01, C03..C11; `svg-viewer.pw.ts` = C02, C12..C21; `harness/`; `fixtures/`). Proofs in `_captures/svg-viewer/`: MUTATION-LOG.md, real-fit.png, real-u5.png, missing.png, broken.png, hostile-zoom4.png, ring_mics.svg (a real KiCad export of the microphone page).

## Use (three screens: Electronics, Board, Inside)
```tsx
import { SvgViewer, type SvgViewerHandle } from '../../components/SvgViewer'
<SvgViewer
  route="electronics"                 // host route: ids are electronics.svg-viewer, .svg-viewer-zoom-in, -zoom-out, -fit, -scale, -image, -focus
  src={page.svg ? dataUrl(page.svg) : null}   // null or '' = picture missing
  label="Microphones, schematic page" // alt text and the viewer's name
  viewBox={[0, 0, 297.0022, 210.0072]}        // the SVG's own viewBox; the unit of `focus`
  focus={{ x: 37.5, y: 32.5, w: 22, h: 13, id: 'U5' }}  // jump + outline; null = none; a new id jumps again
  onScaleChange={(z) => ...}          // optional; 1 = fit
  ref={handleRef}                     // optional: fit(), focusRect(rect), zoomIn(), zoomOut()
/>
```
- Fills its parent (`width/height: 100%`, min height 240 px): the host gives it a sized box.
- `viewBox` is required for `focus` to land: the readers supply the rectangle in the SVG's own units (KiCad pages: mm). Without `viewBox` the image's natural pixel size is the unit, which is wrong for KiCad files. `parseViewBox(text)` is exported if a host has the attribute text.
- The component never fetches, never reads the picture's text, never searches it.
- `missing` (optional BannerSpec, default `{kind:'missing'}`): the honest-state banner shown when `src` is empty; a picture that fails to load shows `{kind:'unparsed', file}`. Both render through `StateBanner` (`<route>.state-banner`), the buttons are disabled.
- A stale picture: dim the host wrapper with `data-dimmed="true"`; the viewer does not do it.

## Behaviour
- Scale is relative to fit: 1.0 = fit (the picture fills 94 % of the box), displayed "100 %". One step is x sqrt(2), so four presses read exactly 4.0 (400 %). Range 0.5 to 40.
- Buttons, keys (`+` `=` `-` `0`, arrows pan 60 px, shift = 180 px), mouse wheel and trackpad pinch (ctrl + wheel) zoom about the pointer; drag pans; two-finger touch pinches. The picture cannot be flung out of the box (48 px stay visible).
- Jump to an item: fills 55 % of the box, never beyond 12x fit; the item is centred and outlined (2 px accent line, constant at any zoom).
- Easing: `--t-slow` and `--ease-settle` for button, key, fit and jump; none while dragging or wheeling; none under `prefers-reduced-motion`.
- Output encoding (CONTRACT 1): the picture is only an `<img src>`; check C11 greps the component for innerHTML, literal colours and addresses.

## Choices
1. Kit: the vendored kit has no zoomable picture component; the viewer is hand-built on tokens only.
2. The root carries `data-picture="ready|absent"`, not `data-state`, because `[data-state]` is the global pill style.
3. docs/CONTRACT.md is frozen (not owned), so the viewer's ids are documented here: `<route>.svg-viewer*`.
4. Run the browser checks: dev server `npx vite --host 127.0.0.1 --port 8808`, then `npx tsx src/components/SvgViewer/__checks__/svg-viewer.pw.ts` (its last line: `svg-viewer pw: 13/13 passed`). The playwright config's testDirs do not include this folder, so `npm run checks` does not run it.
