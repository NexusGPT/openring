import { testId, type SupplierRequest } from '../../contract'

export function Supplier({ items }: { items: readonly SupplierRequest[] }) {
  return (
    <ul className="cs-asks" data-testid={testId('case', 'supplier-items')}>
      {items.map((s) => (
        <li key={s.id} data-testid={testId('case', 'supplier-item')}>
          <span className="cs-ask-item">{s.item}</span>
          <span className="cs-ask-who label">{s.who}</span>
          <span className="cs-ask-text">{s.ask}</span>
        </li>
      ))}
    </ul>
  )
}
