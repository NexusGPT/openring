// The two hand-off sets: what a manufacturer needs and what a 3D printer needs. Read from the files
// list by path rules (filesModel.ts). A set with nothing yet says "Not made yet" and what is coming.
import { testId } from '../../contract'
import { Disclosure } from './Disclosure'
import { FileLine } from './FileLine'
import { manufacturerKinds, printParts, type FileRow } from './filesModel'

const NOT_YET = 'Not made yet'

function Empty({ set, coming }: { set: string; coming: string }) {
  return (
    <p className="set-empty" data-testid={testId('open', 'file-set-empty')} data-set={set}>
      <strong>{NOT_YET}.</strong> {coming}
    </p>
  )
}

function ManufacturerSet({ files }: { files: FileRow[] }) {
  const kinds = manufacturerKinds(files)
  const have = kinds.filter((k) => k.files.length > 0)
  const missing = kinds.filter((k) => k.files.length === 0)
  const coming = `Coming: ${missing.map((k) => k.coming).join(', ')}.`
  if (have.length === 0) return <Empty set="manufacturer" coming={coming} />
  return (
    <>
      {have.map((k) => (
        <div key={k.id} className="kind" data-kind-id={k.id}>
          <p className="label kind-title">{k.label}</p>
          <ul className="fl-list">{k.files.map((f) => <FileLine key={f.path} file={f} scope="set-row" />)}</ul>
        </div>
      ))}
      {missing.length ? <p className="set-more">{NOT_YET}: {missing.map((k) => k.label).join(', ')}.</p> : null}
    </>
  )
}

function PrinterSet({ files }: { files: FileRow[] }) {
  const parts = printParts(files)
  if (parts.length === 0) return <Empty set="printer" coming="Coming: an STL file for each part, and the body in every ring size." />
  return (
    <>
      {parts.map((p) => (
        <div key={p.key} className="kind" data-part={p.key}>
          <p className="label kind-title">{p.label}</p>
          <ul className="fl-list">
            {p.files.map((r) => <FileLine key={r.file.path} file={r.file} scope="set-row" title={r.size ? `Ring size ${r.size}` : undefined} />)}
          </ul>
        </div>
      ))}
    </>
  )
}

export function HandOff({ files }: { files: FileRow[] }) {
  const count = (set: 'manufacturer' | 'printer'): number =>
    set === 'manufacturer' ? manufacturerKinds(files).reduce((n, k) => n + k.files.length, 0) : printParts(files).reduce((n, p) => n + p.files.length, 0)
  return (
    <div className="handoff">
      <Disclosure head="For a manufacturer" meta={`${count('manufacturer')} files`} defaultOpen testId={testId('open', 'file-set')} data-set="manufacturer">
        <ManufacturerSet files={files} />
      </Disclosure>
      <Disclosure head="For a 3D printer" meta={`${count('printer')} files`} defaultOpen testId={testId('open', 'file-set')} data-set="printer">
        <PrinterSet files={files} />
      </Disclosure>
    </div>
  )
}
