import { describe, expect, it } from 'vitest'
import { caseClass, caseNodeSpecs } from '../caseKinds'

describe('case node materials from their names', () => {
  it.each([
    ['base_plate', 'satin'], ['shell', 'satin'], ['lid', 'satin'], ['post', 'soft'], ['glide_1', 'polymer'], ['pin_holder', 'polymer'], ['plunger_L', 'polymer'],
    ['magnet_base', 'metal'], ['magnet_lid', 'metal'], ['hinge_pivot', 'metal'],
    ['light_window', 'resin'], ['LED1', 'resin'], ['main_board', 'pcb'], ['pin_board_pcb2', 'pcb'],
    ['pin_P1_VBUS', 'gold'], ['hinge_pin', 'metal'], ['spring_R', 'metal'], ['cell_dnk852338', 'cell'], ['U1_esp32s3_mini1', 'chip'], ['J1_usb4105', 'chip'], ['unknown_thing', 'polymer'],
  ])('%s is %s', (name, cls) => expect(caseClass(name)).toBe(cls))
  it('every node gets a class, so the case is not one grey', () => {
    const specs = caseNodeSpecs([{ name: 'lid' }, { name: 'pin_P2_D-' }, { name: 'main_board' }])
    expect(new Set(specs.map((s) => s.materialClass)).size).toBe(3)
  })
  it('the shell and the lid are satin metal, the seat of the ring is not', () => {
    const specs = caseNodeSpecs([{ name: 'shell' }, { name: 'lid' }, { name: 'post' }])
    expect(specs.map((s) => s.kind)).toEqual(['satin', 'satin', 'matte'])
  })
})
