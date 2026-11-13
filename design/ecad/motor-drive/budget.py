"""Motor drive study: every current and capacitor figure of motor-drive.md, from named constants.
Run: design/.venv/bin/python -I design/ecad/motor-drive/budget.py > design/ecad/motor-drive/budget.log
Each printed line is KEY = value unit  [source of the inputs]. motor-drive.md cites the KEY."""

# ---- constants, each with its source ----
IBATLIM_MIN_MA = 100.0     # nPM1304 spec p29 Table 14, Min column (columns_p29.log), footnote p30 "Validated through simulation"
BUCK_IOUT_MAX_MA = 200.0   # nPM1304 spec p45 Table 19, IOUT Max column (columns_p45.log)
LS_ILS_MAX_MA = 100.0      # nPM1304 spec p69 Table 20, ILS Max column (columns_p69.log)
LDO_IOUT_MA = 50.0         # nPM1304 spec p70 Table 21, IOUTLDO VOUT > 1.2 V
LED_SINK_MA = 5.0          # nPM1304 spec p80 Table 22, ILED
VSYSPOF_DEFAULT_V = 2.7    # nPM1304 spec p109 Table 27, default falling threshold
ADC_IBAT_FULL_SCALE_MA = 140.0  # nPM1304 spec p99, discharge full scale

I_START_MA = 175.0         # W0525AB001D spec p6 3-1-5 "Below 175 mA", rotor held, at operating voltage
I_RUN_MA = 80.0            # W0525AB001D spec p6 3-1-4 "Below 80 mA"
V_RATED = 3.0              # W0525AB001D spec p6 3-1-1
V_OP_MIN, V_OP_MAX = 2.7, 3.3  # W0525AB001D spec p5 2-3-1
V_START_MAX = 2.5          # W0525AB001D spec p6 3-1-6 "Below DC 2.5V"
G_AVG = 0.25               # W0525AB001D spec p6 3-2-1, 100 g jig at 3.0 V

R_Q1_OHM = 0.7             # bom.csv line 45, DMN2450UFB4 RDS(on) max at 1.8 V gate
ETA = 0.90                 # [ESTIMATE] buck efficiency; Nordic Figure 2 p9 shows above 90 % from 10 uA to 200 mA at 3.8 V in, 3.3 V out; 90 % is the architecture 17.18 figure

V_FULL = 4.35              # architecture 17.13, charge voltage
V_B5 = 3.45                # firmware.md line 95, B5 average voltage
V_B2 = 3.30                # firmware.md line 96, B2 average voltage
V_CUTOFF = 3.10            # architecture section 3, power chip cut-off
V_LIST = [V_FULL, 3.70, V_B5, V_B2, V_CUTOFF, VSYSPOF_DEFAULT_V]

P_SCREEN_MW = 55.0         # architecture section 4, last bullet (screen on, full white, full brightness)
SCR_VCI_MA, SCR_VCI_V = 3.2, 2.8    # same bullet: VCI part (rail VDD_3V0 through the power chip)
SCR_IO_MA, SCR_IO_V = 1.0, 1.8      # same bullet: IOVCC part (VDD_1V8 through the power chip)
SCR_PANEL_MA = 7.0                  # same bullet: panel rails, from SGM38046 whose PVIN is on VBAT (make_netlist.py line 275)
I_REC_MA = 4.0             # architecture 17.5 and 17.15, recording from the cell
I_RADIO_MA = 5.0           # architecture section 2 line 40, radio TX 5.0 mA
V_RADIO = 3.0              # [ESTIMATE] supply voltage taken for the radio figure (above the chip's 1.8 V rail, so the power is not underestimated)
I_SD_WRITE_MA, V_SD = 25.0, 3.0    # slim2_cs-sdnand-20230403.pdf p8, IOP write max 25 mA (at 3.3 V); the rail is VDD_SD 3.0 V
I_SD_AVG_MA = 0.3          # architecture section 4, storage averaged (inside the 4.0 mA)
I_MIC_MA, V_MIC = 2.76, 1.8 # architecture section 4, microphones
I_MCU_MA, V_MCU = 3.0, 1.8  # architecture section 4, main chip (estimate there)
I_LIGHT_MA, V_LIGHT = 1.5, 3.0  # architecture section 4, recording light

MARGIN_TARGET = 0.20       # [CHOICE] 20 % under the 100 mA minimum, because Nordic states the limit is from simulation and not accurate

# option (a) storage capacitor
T_START_LOW_MS = 10.0      # [ESTIMATE] lower bound of the high-current start phase; the W0525 spec states no start time (src_w0525_text.txt search)
T_START_HIGH_MS = 190.0    # INEED C0620BLDCL27 (a 6 mm coin BLDC with drive IC) p4 4-6: response time <= 190 ms to 90 % amplitude
T_START_SUB_MS = 1.0       # shown for scale only
C_PART_NOM_UF = 22.0       # GRM155R60J226ME11D, 22 uF 6.3 V X5R 0402, p3_sgm38046.pdf p4 Table 1
C_PART_DERATE = 0.5        # [ESTIMATE] X5R 0402 at 3.0 V keeps about half its capacitance; Murata sheet not reached (fetch logs)
C_PART_AREA_MM2 = 1.0 * 0.5  # 0402 body; pads and spacing excluded, so the count is a lower bound
BOARD_AREA_MM2 = 27.2 * 12.6 # brief: board 27.2 x 12.6 mm

# recommended: LDO from VBAT
LDO_VDO_MAX_MV_500 = 325.0 # TLV755P p6, dropout max at 500 mA, 2.5 V <= VOUT < 3.3 V, -40 to 125 C
LDO_ACC = 0.012            # TLV755P p5, DQN package output accuracy +-1.2 %
LDO_ISHDN_MAX_UA = 1.0     # TLV755P p5, shutdown current max
LDO_RTHJA = 168.4          # TLV755P p5 Table 5.4, DQN RthetaJA (JEDEC)
LDO_ICL_MIN_MA = 560.0     # TLV755P p5, output current limit min
LDO_TSTR_US = 550.0        # TLV755P p6, start-up time
SHIP_IQ_UA = 0.4           # [ESTIMATE] nPM1304 ship mode current read off Figure 3 p9 at 25 to 40 C (about 0.35 to 0.45 uA)
CELL_MAH_MIN, CELL_MAH_MAX = 17.6, 27.1  # architecture 17.26: smallest cell (US 7) and the top of the US 9 range (before 17.26: 20.4 and 27.2)
PULSE_MS = {'M1': 80, 'M2': 160, 'M3': 240, 'MH': 40, 'MT': 25, 'MW': 60, 'MF': 600}  # firmware.md 3.1 table, ON time per pattern
PATTERNS_PER_DAY = 100     # [ESTIMATE] generous: 100 patterns a day, each taken as the longest (MF)

out = []
def p(key, val, unit, src):
    out.append(f"{key} = {val:.4g} {unit}  [{src}]")

def cell_ma_via_buck(p_mw, v):
    return p_mw / (ETA * v)

# ---- present design (option e): motor on VDD_3V0 through buck 2 ----
p_start_mw = I_START_MA * V_RATED
p_run_mw = I_RUN_MA * V_RATED
p('P_START_RAIL', p_start_mw, 'mW', '175 mA x 3.0 V')
p('P_RUN_RAIL', p_run_mw, 'mW', '80 mA x 3.0 V')
for v in V_LIST:
    p(f'E_START_CELL@{v}', cell_ma_via_buck(p_start_mw, v), 'mA', 'P_START / (ETA x V)')
    p(f'E_RUN_CELL@{v}', cell_ma_via_buck(p_run_mw, v), 'mA', 'P_RUN / (ETA x V)')

def others_chip_ma(v, screen_all=True, sd_write=False):
    """Current through the power chip's battery path for every load but the motor."""
    scr = P_SCREEN_MW if screen_all else (SCR_VCI_MA * SCR_VCI_V + SCR_IO_MA * SCR_IO_V)
    mw = scr + I_RADIO_MA * V_RADIO
    if sd_write:
        mw += (I_SD_WRITE_MA - I_SD_AVG_MA) * V_SD
    return cell_ma_via_buck(mw, v) + I_REC_MA

for v in V_LIST:
    o = others_chip_ma(v)
    p(f'OTHERS_BRIEF@{v}', o, 'mA', 'screen 55 mW + radio 15 mW via buck, + recording 4.0 mA')
    p(f'E_TOTAL_START@{v}', o + cell_ma_via_buck(p_start_mw, v), 'mA', 'present design, start + others')
    p(f'E_TOTAL_RUN@{v}', o + cell_ma_via_buck(p_run_mw, v), 'mA', 'present design, running + others')
    p(f'E_OVER_START_PCT@{v}', 100 * (o + cell_ma_via_buck(p_start_mw, v)) / IBATLIM_MIN_MA - 100, '%', 'over 100 mA')

# ---- fundamental check: power the motor needs to start, against what the limit allows ----
r_eff = V_RATED / (I_START_MA / 1000.0)
p('R_EFF_MIN', r_eff, 'ohm', '3.0 V / 175 mA; the motor at stall is at least this resistance')
i_stall_at_vstart = V_START_MAX / r_eff * 1000.0
p('I_STALL_AT_2V5', i_stall_at_vstart, 'mA', '[ESTIMATE] stall current scaled linearly to 2.5 V')
p('P_STALL_AT_2V5', V_START_MAX * i_stall_at_vstart, 'mW', '2.5 V x I_STALL_AT_2V5')
budget_ma = IBATLIM_MIN_MA * (1 - MARGIN_TARGET)
p('BUDGET_CHIP', budget_ma, 'mA', '100 mA x (1 - 0.20)')
for v in [V_FULL, V_B2]:
    p(f'P_AVAIL_ALONE@{v}', budget_ma * v * ETA, 'mW', 'BUDGET_CHIP x V x ETA, motor alone, no other load')

# ---- option (b): series resistor ----
r_max_run = (V_RATED - V_OP_MIN) / (I_RUN_MA / 1000.0) - R_Q1_OHM
p('B_RS_MAX_FOR_RUN', r_max_run, 'ohm', '(3.0 - 2.7) / 80 mA - Q1 0.7 ohm')
i_stall_with_rs = V_RATED / (r_eff + R_Q1_OHM + r_max_run) * 1000.0
p('B_STALL_RAIL_WITH_RS', i_stall_with_rs, 'mA', '3.0 V / (R_EFF + 0.7 + RS)')
p(f'B_STALL_CELL@{V_B2}', i_stall_with_rs * V_RATED / (ETA * V_B2), 'mA', 'rail current x 3.0 V / (ETA x 3.30 V)')
# resistor that would hold the stall current to the motor share of the budget at B2
share_rail = (budget_ma - others_chip_ma(V_B2)) * ETA * V_B2 / V_RATED
p(f'MOTOR_SHARE_RAIL@{V_B2}', share_rail, 'mA', '(BUDGET_CHIP - OTHERS_BRIEF) x ETA x 3.30 / 3.0')
rs_for_share = V_RATED / (share_rail / 1000.0) - r_eff - R_Q1_OHM
p('B_RS_FOR_SHARE', rs_for_share, 'ohm', '3.0 V / share - R_EFF - 0.7')
p('B_VRUN_WITH_RS_SHARE', V_RATED - (I_RUN_MA / 1000.0) * (rs_for_share + R_Q1_OHM), 'V', 'motor voltage if it drew 80 mA through that resistor')

# ---- option (a): storage capacitor, motor stays on VDD_3V0 ----
dv_allowed = V_RATED - (V_START_MAX + I_START_MA / 1000.0 * R_Q1_OHM)
p('A_DV_ALLOWED', dv_allowed, 'V', '3.0 - (2.5 + 175 mA x 0.7)')
i_excess = I_START_MA - share_rail
p('A_I_EXCESS', i_excess, 'mA', '175 - MOTOR_SHARE_RAIL@3.3')
p('A_R_REFILL', dv_allowed / (share_rail / 1000.0), 'ohm', 'A_DV_ALLOWED / MOTOR_SHARE_RAIL: the most a refill resistor may be')
c_eff_part = C_PART_NOM_UF * C_PART_DERATE
p('A_C_PART_EFF', c_eff_part, 'uF', '22 uF x 0.5 [ESTIMATE]')
for t in [T_START_SUB_MS, T_START_LOW_MS, T_START_HIGH_MS]:
    c_uf = (i_excess / 1000.0) * (t / 1000.0) / dv_allowed * 1e6
    n = c_uf / c_eff_part
    p(f'A_C_NEEDED@{t}ms', c_uf, 'uF', 'I_EXCESS x t / DV')
    p(f'A_PARTS@{t}ms', n, 'parts', 'C / A_C_PART_EFF')
    p(f'A_AREA@{t}ms', n * C_PART_AREA_MM2, 'mm2', 'parts x 0.5 mm2, bodies only')
    p(f'A_AREA_SHARE@{t}ms', 100 * n * C_PART_AREA_MM2 / BOARD_AREA_MM2, '%', 'of 27.2 x 12.6 mm (one face)')
p('A_T_CARRIED_BY_ONE_PART', c_eff_part * 1e-6 * dv_allowed / (i_excess / 1000.0) * 1000.0, 'ms', 'one 22 uF part: C x DV / I_EXCESS')
p('BOARD_AREA', BOARD_AREA_MM2, 'mm2', '27.2 x 12.6')

# ---- option (c): nPM1304 outputs ----
p('C_LDO_SHORT', I_RUN_MA - LDO_IOUT_MA, 'mA', 'running 80 mA - LDO 50 mA')
p('C_LED_SHORT', I_RUN_MA - LED_SINK_MA, 'mA', 'running 80 mA - LED 5 mA')

# ---- recommended: motor fed by its own LDO (TLV75530P) from VBAT ----
r_do = LDO_VDO_MAX_MV_500 / 500.0  # ohm, [ESTIMATE] dropout taken as resistive from the 500 mA point
p('R_LDO_DROPOUT', r_do, 'ohm', '325 mV / 500 mA [ESTIMATE resistive]')
p('LDO_VDO_START', r_do * I_START_MA, 'mV', 'R x 175 mA')
p('LDO_VDO_RUN', r_do * I_RUN_MA, 'mV', 'R x 80 mA')
p('VMOT_MIN', V_RATED * (1 - LDO_ACC), 'V', '3.0 x (1 - 1.2 %)')
p('VMOT_MAX', V_RATED * (1 + LDO_ACC), 'V', '3.0 x (1 + 1.2 %)')
p('VBAT_MIN_FULL_VOLT_RUN', V_RATED * (1 + LDO_ACC) + r_do * I_RUN_MA / 1000.0, 'V', 'VMOT_MAX + dropout at 80 mA')
p('VBAT_MIN_FULL_VOLT_START', V_RATED * (1 + LDO_ACC) + r_do * I_START_MA / 1000.0, 'V', 'VMOT_MAX + dropout at 175 mA')
for v in V_LIST:
    chip = others_chip_ma(v)
    p(f'R_CHIP_BRIEF@{v}', chip, 'mA', 'recommended: chip path = screen 55 mW + radio + recording; motor not in it')
    p(f'R_MARGIN_BRIEF@{v}', 100 * (1 - chip / IBATLIM_MIN_MA), '%', 'under 100 mA')
    chip_all = others_chip_ma(v, sd_write=True)
    p(f'R_CHIP_WITH_SD@{v}', chip_all, 'mA', 'as above + storage write 25 mA burst at 3.0 V')
    p(f'R_MARGIN_WITH_SD@{v}', 100 * (1 - chip_all / IBATLIM_MIN_MA), '%', 'under 100 mA')
    p(f'R_CELL_TOTAL_START@{v}', chip_all + I_START_MA, 'mA', 'whole cell current at a start: chip path + motor 175 mA through the LDO (for S12)')
    p(f'R_CHIP_AS_WIRED@{v}', others_chip_ma(v, screen_all=False, sd_write=True), 'mA', 'chip path with only VCI and IOVCC of the screen (panel is on VBAT)')
for v in [V_FULL, V_B2]:
    p(f'E_CELL_TOTAL_START_SAME_LOADS@{v}', others_chip_ma(v, sd_write=True) + cell_ma_via_buck(p_start_mw, v), 'mA',
      'present design, same loads as R_CELL_TOTAL_START: chip loads + start through the buck')
I_START_VC0720_MA = 120.0  # slim-2.md 1.3, VC0720B088L starting current 120 mA max
p('D_VC0720_START_RAIL', I_START_VC0720_MA * V_RATED, 'mW', '120 mA x 3.0 V')
p('BENCH_PATTERN_COUNT', 7 * 50 + 1000, 'patterns', '7 patterns x 50 + 1,000 x M2')
p('LDO_P_START_MAX', (V_FULL - V_RATED) * I_START_MA, 'mW', '(4.35 - 3.0) x 175 mA')
p('LDO_P_RUN_MAX', (V_FULL - V_RATED) * I_RUN_MA, 'mW', '(4.35 - 3.0) x 80 mA')
p('LDO_RISE_RUN_STEADY', (V_FULL - V_RATED) * I_RUN_MA / 1000.0 * LDO_RTHJA, 'C', 'LDO_P_RUN_MAX x 168.4 C/W, a bound (pulses are 800 ms at most)')
p('LDO_ICL_OVER_START', LDO_ICL_MIN_MA / I_START_MA, 'x', 'current limit min / start current')
# pattern charge the power chip's gauge does not see
mf_mc = I_START_MA * PULSE_MS['MF']  # mA x ms = uC
p('MF_CHARGE_BOUND', mf_mc / 3600.0 / 1000.0, 'mAh', 'MF on-time 600 ms at 175 mA (upper bound)')
day_mah = PATTERNS_PER_DAY * mf_mc / 3600.0 / 1000.0
p('MOTOR_MAH_PER_DAY_BOUND', day_mah, 'mAh', '100 MF patterns at 175 mA [ESTIMATE use]')
p('MOTOR_DAY_SHARE_SMALL_CELL', 100 * day_mah / CELL_MAH_MIN, '%', 'of 17.6 mAh')
p('SHIP_ADD_UA', LDO_ISHDN_MAX_UA, 'uA', 'TLV755P shutdown max')
p('SHIP_DAYS_ON_LDO_ALONE', CELL_MAH_MIN / (LDO_ISHDN_MAX_UA / 1000.0) / 24.0, 'days', '17.6 mAh / 1 uA')
p('SHIP_FACTOR', (SHIP_IQ_UA + LDO_ISHDN_MAX_UA) / SHIP_IQ_UA, 'x', '(0.4 + 1.0) / 0.4, worst case')
p('IBAT_ADC_FS', ADC_IBAT_FULL_SCALE_MA, 'mA', 'nPM1304 p99')

# ---- vibration patterns (firmware 3.1) ----
p('LONGEST_ON', max(PULSE_MS.values()), 'ms', 'MF 300 + 300 on')
p('SHORTEST_ON', min(PULSE_MS.values()), 'ms', 'MT 25 on')
p('LDO_START_SHARE_MT', 100 * LDO_TSTR_US / 1000.0 / PULSE_MS['MT'], '%', '0.55 ms of the 25 ms pulse')

# ---- other loads against the limit (no motor) ----
mw = (P_SCREEN_MW + I_SD_WRITE_MA * V_SD + I_RADIO_MA * V_RADIO + I_MIC_MA * V_MIC
      + I_MCU_MA * V_MCU + I_LIGHT_MA * V_LIGHT)
p('OTHER_LOADS_PEAK_MW', mw, 'mW', 'screen 55 + storage 75 + radio 15 + mics 4.97 + main chip 5.4 + light 4.5')
for v in [V_B2, V_CUTOFF, VSYSPOF_DEFAULT_V]:
    p(f'OTHER_LOADS_PEAK@{v}', cell_ma_via_buck(mw, v), 'mA', 'mW / (ETA x V)')
    p(f'OTHER_LOADS_MARGIN@{v}', 100 * (1 - cell_ma_via_buck(mw, v) / IBATLIM_MIN_MA), '%', 'under 100 mA')
p('OTHER_PLUS_PRESENT_START@3.3', cell_ma_via_buck(mw + p_start_mw, V_B2), 'mA', 'present design: all loads + motor start at 3.30 V')
rail2 = I_SD_WRITE_MA + SCR_VCI_MA + I_LIGHT_MA
p('BUCK2_LOAD_WITHOUT_MOTOR', rail2, 'mA', 'storage 25 + VCI 3.2 + light 1.5')
p('BUCK2_LOAD_PRESENT_START', rail2 + I_START_MA, 'mA', 'present design: + 175 mA')
p('BUCK2_LIMIT', BUCK_IOUT_MAX_MA, 'mA', 'nPM1304 p45')

for line in out:
    print(line)
print(f"COUNT figures = {len(out)}")
print("RESULT computed")
