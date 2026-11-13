#!/usr/bin/env node
// Fails when docs/CONTRACT.md lacks a required statement, disagrees with constants.json, or when
// docs/CONSTANTS.md and constants.json name different constants.
import { readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const read = (p) => readFileSync(join(root, p), 'utf8')
const constants = JSON.parse(read('contract/schema/constants.json'))
const contract = read('docs/CONTRACT.md')
const constDoc = read('docs/CONSTANTS.md')
const lanes = JSON.parse(read('docs/lane-dag.json')).lanes.map((l) => l.id)

const problems = []
const need = (re, what) => re.test(contract) || problems.push(`CONTRACT.md lacks: ${what}`)

need(/React text/i, 'output encoding: React text')
need(/<img/, 'output encoding: SVG via <img>')
need(/dangerouslySetInnerHTML/, 'no dangerouslySetInnerHTML')
need(/LINE is one row/, 'line count definition')
need(/PARTS = the sum of `quantity`/, 'part count definition')
need(/Hosted-ready/, 'hosted-ready rules')
need(/fileUrl\(/, 'relative file url rule')
need(/Component-to-shape map/i, 'component-to-shape map')
need(/Honest-state vocabulary/i, 'honest-state vocabulary')
need(/<route>\.<element>/, "test id grammar '<route>.<element>'")
need(/<bom>:<ref>/, "part id grammar '<bom>:<ref>'")
need(/<lane>-C01\.\.C99/, "check id ranges '<lane>-C01..C99'")
need(/Where a brief and this file disagree, this file wins: follow it and report the conflict/, 'precedence line')
need(new RegExp(`port ${constants.APP_PORT}\\b`), `app port ${constants.APP_PORT}`)
need(new RegExp(`port ${constants.JOURNEY_PORT}\\b`), `journey port ${constants.JOURNEY_PORT}`)
for (const lane of [...lanes, 'contract'].filter((v, i, a) => a.indexOf(v) === i)) {
  need(new RegExp(`${lane}-C01\\.\\.C99`), `check id range for lane ${lane}`)
}

const named = new Set([...constDoc.matchAll(/^\| ([A-Z][A-Z0-9_]+) \|/gm)].map((m) => m[1]))
for (const k of Object.keys(constants)) named.has(k) || problems.push(`CONSTANTS.md does not name ${k}`)
for (const k of named) k in constants || problems.push(`CONSTANTS.md names ${k}, which constants.json lacks`)

if (problems.length) {
  console.error(problems.map((p) => '  ' + p).join('\n'))
  process.exit(1)
}
console.log(`check-contract-doc: ok (${lanes.length} lane check ranges, ${Object.keys(constants).length} constants)`)
