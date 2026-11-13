// Parse, never cast: every record that crosses the file boundary is checked against its schema.
import Ajv2020 from 'ajv/dist/2020'

const schemas = import.meta.glob('../../contract/schema/**/*.schema.json', { eager: true, import: 'default' }) as Record<
  string,
  { $id: string }
>

const ajv = new Ajv2020({ strict: false, validateFormats: false, allErrors: false })
for (const s of Object.values(schemas)) ajv.addSchema(s)

/** Problems of `data` against schema `name` ('parts', 'manifest', 'content/part-notes'); [] when valid. */
export function schemaProblems(name: string, data: unknown): string[] {
  const validate = ajv.getSchema(`${name}.schema.json`)
  if (!validate) throw new Error(`no schema named ${name}`)
  if (validate(data)) return []
  return (validate.errors ?? []).map((e) => `${e.instancePath || '$'} ${e.message ?? 'is invalid'}`)
}
