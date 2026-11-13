// Headless harness. ?mode=real (KiCad microphone page) | real-u5 (jumped to U5) | missing | broken | hostile (a page that carries script)
import '@fontsource/geist-sans/400.css'
import '@fontsource/geist-sans/600.css'
import '@fontsource/geist-mono/400.css'
import '../../../../styles/tokens.css'
import '../../../../styles/primitives.css'
import { createRoot } from 'react-dom/client'
import { SvgViewer } from '../..'
import mics from '../../../../../_captures/svg-viewer/ring_mics.svg?url'
import page from './../fixtures/page.svg?url'
import hostile from './../fixtures/hostile.svg?url'

const mode = new URLSearchParams(location.search).get('mode') ?? 'real'
const MICS_VB = [0, 0, 297.0022, 210.0072] as const
const SMALL_VB = [0, 0, 100, 60] as const
// U5's body on the real page, in the page's own units (mm), as the readers will supply it.
const U5 = { x: 37.5, y: 32.5, w: 22, h: 13, id: 'U5' }

function App() {
  switch (mode) {
    case 'real-u5': return <SvgViewer route="electronics" src={mics} label="Microphones, schematic page" viewBox={MICS_VB} focus={U5} />
    case 'missing': return <SvgViewer route="board" src={null} label="Board plan" />
    case 'broken': return <SvgViewer route="board" src="/data/board/not-there.svg" label="Board plan" />
    case 'hostile': return <SvgViewer route="electronics" src={hostile} label="Hostile test page" viewBox={SMALL_VB} />
    case 'small': return <SvgViewer route="electronics" src={page} label="Test page" viewBox={SMALL_VB} focus={{ x: 40, y: 20, w: 12, h: 10, id: 'U5' }} />
    default: return <SvgViewer route="electronics" src={mics} label="Microphones, schematic page" viewBox={MICS_VB} />
  }
}
createRoot(document.getElementById('root')!).render(<App />)
