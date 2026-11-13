// The filter chips: one model, written to the address. A chip is a toggle (aria-pressed); "clear all" appears
// only when something is on.
import { testId } from '../../contract'
import { NO_FILTER, isFiltered, type FilterModel, type Has } from './model'

export const CHIP_WORDS = {
  code: 'has an order code',
  drawing: 'made to drawing',
  supplier: "needs a supplier's answer",
  clear: 'clear all',
} as const

function Chip({ id, on, onClick, children }: { id: string; on: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button type="button" className="pt-chip" aria-pressed={on} data-filter={id} data-testid={testId('parts', 'filter-chip')} onClick={onClick}>
      {children}
    </button>
  )
}

export function FilterBar({ model, onChange, pageTitle, disabled }: { model: FilterModel; onChange: (m: FilterModel) => void; pageTitle: string | null; disabled: boolean }) {
  const toggleHas = (h: Has) => onChange({ ...model, has: model.has === h ? null : h })
  return (
    <div className="pt-chips" role="group" aria-label="Filter the list" data-disabled={disabled || undefined}>
      <Chip id="code" on={model.has === 'code'} onClick={() => toggleHas('code')}>{CHIP_WORDS.code}</Chip>
      <Chip id="drawing" on={model.has === 'drawing'} onClick={() => toggleHas('drawing')}>{CHIP_WORDS.drawing}</Chip>
      <Chip id="supplier" on={model.supplier} onClick={() => onChange({ ...model, supplier: !model.supplier })}>{CHIP_WORDS.supplier}</Chip>
      {model.page ? (
        <Chip id="page" on onClick={() => onChange({ ...model, page: null })}>
          {`page: ${pageTitle ?? model.page}`}
          <span aria-hidden="true" className="pt-chip-x">×</span>
        </Chip>
      ) : null}
      {isFiltered(model) ? (
        <button type="button" className="pt-clear" data-testid={testId('parts', 'filter-clear')} onClick={() => onChange(NO_FILTER)}>
          {CHIP_WORDS.clear}
        </button>
      ) : null}
    </div>
  )
}
