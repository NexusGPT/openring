// Electronics: how the ring is wired. The circuit as blocks; a click opens that block's page of the wiring
// diagram beside it; the parts on the page, the chip's pin plan and the power budget are one tab away.
import './electronics.css'
import { useMemo, useState } from 'react'
import { StateBanner, parsePartId, testId } from '../../contract'
import { useSearchParams } from '../../app/router'
import { useStageScene } from '../../app/stage-scene'
import { BlockDiagram } from './BlockDiagram'
import { MetaPane, PicturePane } from './PagePane'
import { useWidePanel } from './useWide'
import { PartsOnPage } from './PartsOnPage'
import { TableView } from './TableView'
import { WiringSection, type WiringView } from './WiringSection'
import { blockOfPage, fallbackPdf, hubOf, pageOfBlock, partIdsOf, type Block, type Page } from './model'
import { useElectronics } from './useElectronics'

const TABS = [
  { id: 'wiring', label: 'Wiring' },
  { id: 'pins', label: 'Pin plan' },
  { id: 'power', label: 'Power budget' },
] as const
type Tab = (typeof TABS)[number]['id']

export default function Electronics() {
  const d = useElectronics()
  useWidePanel()
  const [params, setParams] = useSearchParams()
  useStageScene({ show: 'internals' })

  const tabParam = params.get('tab')
  const tab: Tab = TABS.some((t) => t.id === tabParam) ? (tabParam as Tab) : 'wiring'
  const blocks = d.electronics?.blocks ?? []
  const links = d.electronics?.links ?? []
  const pages = d.pages?.pages ?? []
  const hub = useMemo(() => hubOf(blocks, links), [blocks, links])
  const chosen = blocks.find((b) => b.id === params.get('block')) ?? hub
  const pageOf = (b: Block) => pageOfBlock(b, d.pages)
  const pageParam = pages.find((p) => p.id === params.get('page'))
  const page = pageParam ?? (chosen ? pageOf(chosen) : null)
  const block = pageParam ? blockOfPage(pageParam, blocks, d.pages) : chosen
  const rawPart = params.get('part')
  const selectedPart = rawPart && parsePartId(rawPart) ? rawPart : null

  const write = (edit: (n: URLSearchParams) => void) => {
    const n = new URLSearchParams(params)
    edit(n)
    setParams(n)
  }
  const setTab = (t: Tab) => write((n) => (t === 'wiring' ? n.delete('tab') : n.set('tab', t)))
  const [picks, setPicks] = useState(0) // counts the owner's own clicks on a block or page; the pane scrolls into view for those only
  const pickBlock = (id: string) => { setPicks((n) => n + 1); write((n) => { n.set('block', id); n.delete('page') }) }
  const pickPage = (p: Page) => {
    setPicks((n) => n + 1)
    const b = blockOfPage(p, blocks, d.pages)
    write((n) => { if (b) { n.set('block', b.id); n.delete('page') } else n.set('page', p.id) })
  }
  const pickPart = (id: string | null) => write((n) => (id ? n.set('part', id) : n.delete('part')))
  const connParam = params.get('conn')
  const rawCpart = params.get('cpart')
  const connPart = rawCpart && parsePartId(rawCpart) ? rawCpart : null
  const connView: WiringView = params.get('cview') === 'list' ? 'list' : 'map'
  const pickConn = (id: string | null) => write((n) => { n.delete('cpart'); if (id && id !== connParam) n.set('conn', id); else n.delete('conn') })
  const pickConnPart = (id: string | null) => write((n) => (id ? n.set('cpart', id) : n.delete('cpart')))
  const setConnView = (v: WiringView) => write((n) => (v === 'list' ? n.set('cview', 'list') : n.delete('cview')))

  const empty = !d.loading && !d.electronics && !d.pages
  const stamp = [d.version ? `Design ${d.version}` : null, d.updated ? `updated ${d.updated}` : null].filter(Boolean).join(' · ')

  return (
    <div className="el" data-testid={testId('electronics', 'panel')} data-dimmed={d.stale ? 'true' : undefined} aria-busy={d.loading}>
      <div className="el-top">
      <header className="el-head">
        <h1 className="display">How it is wired</h1>
        {stamp ? <p className="label">{stamp}</p> : null}
      </header>
      {empty ? null : (
          <div className="el-tabs" role="tablist" aria-label="Electronics views">
            {TABS.map((t) => (
              <button
                key={t.id} type="button" role="tab" id={`el-tab-${t.id}`} aria-selected={tab === t.id} aria-controls="el-body"
                data-testid={testId('electronics', `tab-${t.id}`)} onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>
      )}
      </div>
      {d.banners.map((b) => <StateBanner key={JSON.stringify(b)} route="electronics" spec={b} />)}

      {empty ? (
        <p className="el-none muted" data-testid={testId('electronics', 'nothing')}>Nothing to show yet.</p>
      ) : (
        <>
          <div className="el-body" id="el-body" role="tabpanel" aria-labelledby={`el-tab-${tab}`} key={tab}>
            {tab === 'wiring' && (
              <div className="el-wiring">
                <div className="el-left">
                  <p className="label">Click a block to open its page</p>
                  {blocks.length > 0 ? (
                    <BlockDiagram blocks={blocks} links={links} selected={block?.id ?? null} pageOf={pageOf} onSelect={pickBlock} />
                  ) : (
                    <p className="el-none muted">The blocks of the circuit are not available yet.</p>
                  )}
                </div>
                <PicturePane
                  block={block} page={page} pages={pages} files={d.files} pdfFallback={fallbackPdf(d.files)}
                  part={selectedPart} scrollKey={String(picks)}
                />
                <MetaPane block={block} page={page} pages={pages} blocks={blocks} links={links} onBlock={pickBlock} onPage={pickPage} />
                {(block || page) && (
                  <PartsOnPage
                    ids={partIdsOf(block, page)} selected={selectedPart} parts={d.parts} notes={d.notes}
                    files={d.files} areaState={d.area?.state ?? null} onSelect={pickPart}
                  />
                )}
              </div>
            )}
            {tab === 'wiring' && (
              <WiringSection
                map={d.electronics?.connection_map ?? null} view={connView} selected={connParam} part={connPart}
                parts={d.parts} notes={d.notes} files={d.files} areaState={d.area?.state ?? null} boardGroups={d.boardGroups}
                loading={d.loading} onView={setConnView} onSelect={pickConn} onPart={pickConnPart}
              />
            )}
            {tab === 'pins' && (d.electronics
              ? <TableView name="pin-plan" title="Pin plan" table={d.electronics.pin_plan} files={d.files} searchable />
              : <p className="el-none muted">The pin plan is not available yet.</p>)}
            {tab === 'power' && (d.electronics
              ? <TableView name="power-budget" title="Power budget" table={d.electronics.power_budget} files={d.files} />
              : <p className="el-none muted">The power budget is not available yet.</p>)}
          </div>
        </>
      )}
    </div>
  )
}
