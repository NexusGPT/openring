// The wiring-diagram page of the chosen block, large and zoomable (PicturePane), and beside it the page list
// and what the block shares with the others (MetaPane).
import { useEffect, useRef } from 'react'
import { SvgViewer, type SvgViewerHandle } from '../../components/SvgViewer'
import { Link } from '../../app/router'
import { dataUrl, fileUrl } from '../../data'
import { testId, type Files } from '../../contract'
import { findRefRect, useRefit, useSvgText, viewBoxOfText } from './focus'
import { isListed, linksOf, refOf, type Block, type Link as BlockLink, type Page } from './model'

interface PicProps {
  block: Block | null
  page: Page | null
  pages: readonly Page[]
  files: Files | null
  pdfFallback: string | null
  /** the part chosen in the list: the picture jumps to it */
  part: string | null
  /** changes when the owner picks a block or page: the pane then scrolls into view when it is below the fold */
  scrollKey: string
}

function Picture({ page, files, fallbackPdf, part }: { page: Page | null; files: Files | null; fallbackPdf: string | null; part: string | null }) {
  const pdf = page?.pdf ?? fallbackPdf
  const url = page?.svg ? dataUrl(page.svg) : null
  const text = useSvgText(url)
  const vb = viewBoxOfText(text)
  const rect = part ? findRefRect(text, refOf(part)) : null
  const box = useRef<HTMLDivElement>(null)
  const handle = useRef<SvgViewerHandle>(null)
  useRefit(box, handle)
  if (page?.svg && url) {
    return (
      <div className="el-viewbox" ref={box}>
      <SvgViewer
        ref={handle} route="electronics" src={url} label={`Wiring diagram, page ${page.number}: ${page.title}`}
        viewBox={vb ?? undefined} focus={rect ? { ...rect, id: part ?? undefined } : null}
      />
      </div>
    )
  }
  return (
    <div className="el-nopic" data-testid={testId('electronics', 'pdf-fallback')}>
      <p>{page ? 'This page is only available as a PDF.' : 'The wiring pictures are not built yet.'}</p>
      {pdf && isListed(files, pdf) ? (
        <a href={fileUrl(pdf)} target="_blank" rel="noreferrer" data-testid={testId('electronics', 'pdf-link')}>Open the wiring diagram as a PDF</a>
      ) : pdf ? (
        <span className="muted">{`${pdf} (not in the files list)`}</span>
      ) : null}
    </div>
  )
}

export function PicturePane({ block, page, pages, files, pdfFallback, part, scrollKey }: PicProps) {
  const ref = useRef<HTMLDivElement>(null)
  const seen = useRef(scrollKey)
  useEffect(() => {
    if (seen.current === scrollKey) return
    seen.current = scrollKey
    const el = ref.current
    const before = el?.previousElementSibling?.getBoundingClientRect()
    const mine = el?.getBoundingClientRect()
    // side by side (wide panel): nothing to scroll to
    if (!el || !before || !mine || before.left >= mine.right - 1 || before.right <= mine.left + 1) return
    el.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })
  }, [scrollKey])
  const sheet = page?.id ?? block?.sheet ?? null
  return (
    <div className="el-pane" ref={ref} key={block?.id ?? 'none'} data-testid={testId('electronics', 'page-pane')}>
      <header className="el-pane-head">
        <div>
          <p className="label">{page ? `Wiring diagram · page ${page.number} of ${pages.length}` : 'Wiring diagram'}</p>
          <h2 className="display">{block?.label ?? page?.title ?? 'Pick a block'}</h2>
        </div>
        {sheet && (
          <Link to={`/parts?page=${encodeURIComponent(sheet)}`} className="el-parts-link" data-testid={testId('electronics', 'parts-of-page')}>
            Parts of this page<span aria-hidden="true"> →</span>
          </Link>
        )}
      </header>
      <Picture page={page} files={files} fallbackPdf={pdfFallback} part={part} />
    </div>
  )
}

interface MetaProps {
  block: Block | null
  page: Page | null
  pages: readonly Page[]
  blocks: readonly Block[]
  links: readonly BlockLink[]
  onBlock: (id: string) => void
  onPage: (p: Page) => void
}

export function MetaPane({ block, page, pages, blocks, links, onBlock, onPage }: MetaProps) {
  const near = block ? linksOf(block.id, links) : []
  const labelOf = (id: string) => blocks.find((b) => b.id === id)?.label ?? id
  return (
    <div className="el-meta">
      {pages.length > 0 && (
        <nav className="el-pages" aria-label="Pages of the wiring diagram" data-testid={testId('electronics', 'page-list')}>
          {pages.map((p) => (
            <button
              key={p.id} type="button" aria-pressed={p.id === page?.id} title={p.title}
              data-testid={testId('electronics', 'page-tab')} data-page={p.id} onClick={() => onPage(p)}
            >
              <span className="label">{String(p.number).padStart(2, '0')}</span>
              <span className="el-page-title">{p.title}</span>
            </button>
          ))}
        </nav>
      )}
      {near.length > 0 && (
        <div className="el-near" data-testid={testId('electronics', 'near')}>
          <span className="label">Shares signals with</span>
          <ul>
            {near.map((n) => (
              <li key={n.other}>
                <button type="button" onClick={() => onBlock(n.other)} title={n.nets.join(', ')}>
                  {labelOf(n.other)}<span className="muted">{` · ${n.nets.length}`}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
