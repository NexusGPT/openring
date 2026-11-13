// The record registry (contract/schema/records.json) typed for the app: record id, schema name and
// the file the collector writes inside the bundle.
import registry from '../../contract/schema/records.json'
import type {
  AreaStates, BoardFiles, Case, Electronics, Files, FirmwareRules, KeyNumbers, LookOptions, OpenItems,
  PartPlacements, Parts, RingModel, SchematicPages,
} from './records'

/** record id -> its data type. The 13 collected records. */
export interface RecordTypes {
  'ring-model': RingModel
  'part-placements': PartPlacements
  parts: Parts
  'key-numbers': KeyNumbers
  'area-states': AreaStates
  'look-options': LookOptions
  electronics: Electronics
  'schematic-pages': SchematicPages
  'board-files': BoardFiles
  'firmware-rules': FirmwareRules
  case: Case
  'open-items': OpenItems
  files: Files
}
export type RecordId = keyof RecordTypes

export const RECORD_IDS = registry.records.map((r) => r.id) as RecordId[]
export const RECORD_FILE: Record<RecordId, string> = Object.fromEntries(
  registry.records.map((r) => [r.id, r.file]),
) as Record<RecordId, string>
export const RECORD_SCHEMA: Record<RecordId, string> = Object.fromEntries(
  registry.records.map((r) => [r.id, r.schema]),
) as Record<RecordId, string>
