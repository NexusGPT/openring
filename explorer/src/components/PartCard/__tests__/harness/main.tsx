// Headless harness: three card states side by side on a white page. Made-up data only.
import '@fontsource/geist-sans/400.css'
import '@fontsource/geist-sans/600.css'
import '@fontsource/geist-mono/400.css'
import '@fontsource/libre-caslon-text/400.css'
import '../../../../styles/tokens.css'
import '../../../../styles/primitives.css'
import { createRoot } from 'react-dom/client'
import { PartCard } from '../..'
import { files, legend, notes, ordered, waiting } from '../sample'

const open = new URLSearchParams(location.search).get('open') === '1'
createRoot(document.getElementById('root')!).render(
  <div className="row" data-open={open}>
    <div className="cell"><PartCard route="inside" partId="ring:ZZ9" line={ordered} note={notes['ring:ZZ9']} legend={legend} files={files} /></div>
    <div className="cell"><PartCard route="parts" partId="ring:BT1" line={waiting} note={notes['ring:BT1']} legend={legend} files={files} areaState="waiting on a supplier" /></div>
    <div className="cell"><PartCard route="board" partId="ring:BT1" line={waiting} note={notes['ring:BT1']} legend={legend} files={files} banner={{ kind: 'stale', basis: 'ZV1', current: 'ZV2' }} /></div>
  </div>,
)
