import '@fontsource/libre-caslon-text/latin-400.css'
import '@fontsource/geist-sans/latin-400.css'
import '@fontsource/geist-sans/latin-500.css'
import '@fontsource/geist-sans/latin-600.css'
import '@fontsource/geist-mono/latin-400.css'
import './styles/tokens.css'
import './styles/primitives.css'
import './styles/shell.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { DataProvider, createQueryClient, routerBasename } from './data'
import { Router } from './app/router'
import { Shell } from './app/Shell'

const client = createQueryClient()
const rootEl = document.getElementById('root')
if (!rootEl) throw new Error('index.html has no #root')

createRoot(rootEl).render(
  <StrictMode>
    <DataProvider client={client}>
      <Router basename={routerBasename()}>
        <Shell />
      </Router>
    </DataProvider>
  </StrictMode>,
)
