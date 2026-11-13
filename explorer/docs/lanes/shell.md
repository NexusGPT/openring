# Lane notes: shell

Files: `src/main.tsx`, `src/app/**` (Shell, TabBar, FreshnessStamp, StageHost, stage-scene, routes, route-names, router, ScreenPlaceholder, ErrorBoundary, `__checks__/`), `src/styles/{tokens,primitives,shell}.css`.

## Seams other pieces use
- Screen entry: `src/routes/<folder>/index.tsx`, default export a component (named `Screen` also accepted). Folder = route id, except `open-files` = `open`. No props.
- Router: import `Link`, `useLocation`, `useNavigate`, `useSearchParams` from `src/app/router` (react-router is NOT used: it writes `http://localhost` into the build and fails `npm run test:hosted`).
- Stage: the shell mounts ONE stage slot (`data-stage-id` on `[data-testid="app.stage"]`). It loads `src/stage/index.tsx` (default export `Stage`, prop `scene: StageScene`) by glob when that file exists. A screen steers the stage with `useStageScene({...})` from `src/app/stage-scene`.
- Panel: `[data-testid="app.panel-expand"]` toggles; Escape and leaving the route collapse. Dim stale content with `data-dimmed="true"`.
- Styling: tokens in `src/styles/tokens.css` only (`--ink`, `--muted`, `--hairline`, `--accent`, `--font-*`); `.label`, `.display`, `[data-state]` (pill), `[data-kind]` (banner) are styled globally.
