#!/usr/bin/env python3
"""Check design/firmware.md against its own rules and design/architecture.md.

Usage: firmware-check.py [firmware.md] [--arch architecture.md]
Exit 0 when every check passes, 1 when any fails, 2 when a file cannot be read.

Checks:
  1. Numbered sections "## 1." to "## 10." are all present.
  2. Every state named (in backticks) in the From and To columns of the
     transition table (section 1.2) is in the state list (section 1.1), and
     every listed state appears in at least one transition.
  3. Every pin (Pn.nn) and every signal name used in firmware.md is in the
     pin plan of architecture.md section 7; a "SIGNAL Pn.nn" pair in
     firmware.md matches the pin the architecture gives that signal.
  4. The RAM budget lines (section 4.6) sum to the stated total, and the
     total is at most 512 KB (524,288 bytes).
  5. A "questions_for_owner" section exists and the last line starts with
     "RESULT: done," or "RESULT: blocked,".
  Added in F2:
  6. A pin used in firmware.md is not a spare pin of architecture section 7,
     and a signal-like name (prefixes of section 7 plus LED and MOTOR) is a
     signal of section 7 (so a light pin, which A2 removed, fails).
  7. Charge voltage and current in section 8.1 equal architecture section 3.
  8. Each "<clock>, prescaler N, ratio R" line: 32 MHz / N = clock, N in 4..126,
     R in the chip's ratios, clock / R = 16,000 or 8,000 Hz, and the clock
     inside the microphone mode range (normal 1.2-1.65 MHz, low power
     450-850 kHz, IM73D122V01 datasheet table 5).
  9. Section 6.1 sets 64-byte bulk packets for full speed.
 10. Section 4.7 marks motor pulses up to 50 ms after them.
 11. The schematic rules: mic clocks low while VDD_MIC is off (section 4.5),
     no storage line high while VDD_SD is off (section 5.1), screen sequence
     names OLED_PWR_EN and SWIRE (section 3.3).
 12. Thermistor: ohms in the binding's values, cold < cool < warm < hot.
  Added for the owner's decision (record only on a long press):
 13. None of the removed names (DAY_LISTEN, DAY_REC, VOICE_NOTE, MEETING_REC,
     speech detector, pre-roll, day mode, voice note, listening) appears
     outside the change list at the top.
 14. VDD_MIC is "on" for exactly one state in the state list (1.1) and in
     exactly one row of the power table (8.2), the same recording state.
 15. Every transition into the recording state from another state, and every
     button transition out of it, is a "long press"; a "short press" or
     "double press" transition never changes state; section 2.1 gives the
     long press as 1,000 ms for start and stop.
  Changed and added for F3 (architecture A5-draft section 17):
  2b. Every state has a transition out; every state except SHIP and BOOT has
      one in; the number of rows equals "The table has N transitions." under
      the table (a removed row fails).
  7.  (changed) The charge voltage equals the cell's type in architecture
      section 2 (4.35 V); the charge current is BLOCKED on S12, S12 is an open
      item of architecture 17.6, and the current is not a number.
  11. (changed) Only MIC_A_CLK is the microphone clock to hold low.
  13. (changed) The change lists run from "Changes from F2 to F3" to
      "Peripheral instances"; F2 values that F3 replaced (4 microphones,
      4 channels, 66,048, 129 sectors, Zetta, 135 mAh, T-SKEW, T-MIC3,
      T-MIC4, the F2 skew field) must not appear outside them.
  16. F3 rules: header version F3 and basis A5; audio format against
      architecture 16.6; chunk arithmetic; one PDM instance; joystick switches
      against architecture 17.3 and the 40 ms rule against 16.5; unused pins
      only on lines that say unused; motor part against 17.4; battery minutes
      and recording hours recomputed; four pads in order.
  Changed and added for F4 (architecture A5-draft sections 17.11 and 17.12):
  16. (changed) header version F4, basis A5, sections 17.11 and 17.12 named;
      the change list "Changes from F3 to F4" exists.
  13. (changed) the change lists run from "Changes from F3 to F4"; "record
      button" is a removed name outside them, the section 10.6 text and the
      hardware issues table.
  17. F4 rules. Record gesture: read from the transition table (1.2), the
      gesture table (2.1) and the joystick table (2.2): exactly one row enters
      the recording state and it is a long press of the joystick centre from
      STANDBY; the long press row in the recording state goes to STANDBY and
      closes; short press and double press rows in the recording state stay
      in it (highlight, nothing); no event naming a direction touches the
      recording state or changes any state; no gesture row but the long press
      starts or stops a recording; double press does nothing; no direction
      column of 2.2 starts or stops a recording. Centre source: both cases
      (`SW2`, `PAIR`) have an input and a debounce; warning pulse MW exists;
      short-press ceiling < warning time < long press; release hold-off between
      the debounce and the double-press gap; collisions C1 to C4 listed.
      Charging: every row into CHARGING, and the two rows that leave ship
      mode, say "charge on"; `charging-enable` is on whenever VBUS is present;
      CHARGE_CURRENT is named, BLOCKED, with the 1 C limit (15 to 20 mA) and
      the 32 mA minimum; R-CHG stated; section 8.6 says VBUS is an input only
      and nothing is driven onto the pads; architecture 17.11 and 17.12 still
      say what F4 relies on.
"""
import os
import re
import sys

RAM_LIMIT = 512 * 1024


def follows(text):
    m = re.search(r"\bfollows\b[\s\S]{0,200}?\bversion\s+([A-Z]{1,2}\d+)", text, re.I)
    return m.group(1) if m else None


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        print(f"ERROR cannot read {path}: {exc}")
        sys.exit(2)


def section(text, start_pat, end_pat):
    m = re.search(start_pat, text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    e = re.search(end_pat, rest, re.M)
    return rest[: e.start()] if e else rest


def table_rows(block):
    rows = []
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.match(r"^\|[\s\-|:]+\|$", s):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        rows.append(cells)
    return rows


def arch_pins(arch):
    sec = section(arch, r"^## 7\. ", r"^## \d+\. ")
    if sec is None:
        print("ERROR architecture.md has no section 7")
        sys.exit(2)
    signals, pins, pairs, spares = set(), set(), {}, set()
    for cells in table_rows(sec):
        if len(cells) < 2 or cells[0] in ("Signal",):
            continue
        sig_cell, pin_cell = cells[0], cells[1]
        cell_pins = re.findall(r"P\d\.\d{2}", pin_cell)
        pins.update(cell_pins)
        if sig_cell.lower().startswith("spare"):
            spares.update(cell_pins)
            continue
        names = [n.strip() for n in sig_cell.split("/")]
        for n in names:
            if n:
                signals.add(n)
        if len(names) == len(cell_pins):
            for n, p in zip(names, cell_pins):
                pairs[n] = p
    return signals, pins, pairs, spares


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__))
    fw_path = os.path.join(here, "firmware.md")
    arch_path = os.path.join(here, "architecture.md")
    args = list(argv)
    if "--arch" in args:
        i = args.index("--arch")
        arch_path = args[i + 1]
        del args[i : i + 2]
    if args:
        fw_path = args[0]
    fw = read(fw_path)
    arch = read(arch_path)
    errors = []
    print(f"firmware: {fw_path}")
    print(f"architecture: {arch_path}")

    # 1. sections
    found = {int(n) for n in re.findall(r"^## (\d+)\. ", fw, re.M)}
    missing = [n for n in range(1, 11) if n not in found]
    for n in missing:
        errors.append(f"section {n} missing")
    print(f"check 1 sections: found {sorted(n for n in found if 1 <= n <= 10)}, missing {missing}")

    # 2. states
    states_block = section(fw, r"^### 1\.1 ", r"^### ")
    trans_block = section(fw, r"^### 1\.2 ", r"^### |^## ")
    states, transitions = [], []
    if states_block is None:
        errors.append("state list (### 1.1) missing")
    else:
        for cells in table_rows(states_block):
            m = re.fullmatch(r"`([A-Z][A-Z0-9_]*)`", cells[0])
            if m:
                states.append(m.group(1))
    if trans_block is None:
        errors.append("transition table (### 1.2) missing")
    else:
        for cells in table_rows(trans_block):
            if len(cells) < 4 or cells[0] == "From":
                continue
            frm = re.findall(r"`([A-Z][A-Z0-9_]*)`", cells[0])
            to = re.findall(r"`([A-Z][A-Z0-9_]*)`", cells[2])
            if frm or to:
                transitions.append((frm, cells[1], to))
    state_set = set(states)
    used = set()
    for frm, ev, to in transitions:
        if len(frm) != 1 or len(to) != 1:
            errors.append(f"transition needs one From and one To state: {frm} / {ev} / {to}")
        for s in frm + to:
            used.add(s)
            if s not in state_set:
                errors.append(f"state `{s}` used in transition '{ev}' is not in the state list")
    for s in states:
        if s not in used:
            errors.append(f"state `{s}` is in the list but in no transition")
    if not transitions:
        errors.append("no transitions found")
    outs = {f for frm, ev, to in transitions for f in frm}
    ins = {t for frm, ev, to in transitions for t in to}
    for s_ in states:
        if s_ not in outs:
            errors.append(f"state `{s_}` has no transition out")
        if s_ not in ins and s_ not in ("SHIP", "BOOT"):
            errors.append(f"state `{s_}` has no transition in")
    mcount = re.search(r"^The table has (\d+) transitions\.$", fw, re.M)
    if not mcount:
        errors.append("the sentence 'The table has N transitions.' is missing under the transition table")
    elif int(mcount.group(1)) != len(transitions):
        errors.append(f"transition table has {len(transitions)} rows, the text says {mcount.group(1)}")
    print(f"check 2 states: {len(states)} listed, {len(transitions)} transitions, {len(used)} states used")

    # 3. pins and signals
    signals, pins, pairs, spares = arch_pins(arch)
    prefixes = sorted({s.split("_")[0] for s in signals if "_" in s} | {"LED", "MOTOR"})
    fw_pins = set(re.findall(r"P\d\.\d{2}", fw))
    for p in sorted(fw_pins - pins):
        errors.append(f"pin {p} is not in architecture section 7")
    for p in sorted(fw_pins & spares):
        errors.append(f"pin {p} is a spare pin in architecture section 7 but firmware.md uses it")
    sig_re = re.compile(r"(?<![A-Za-z0-9_])((?:" + "|".join(map(re.escape, prefixes)) + r")_[A-Z0-9_]+)(?![A-Za-z0-9_])")
    fw_sigs = set(sig_re.findall(fw))
    for s in sorted(fw_sigs - signals):
        errors.append(f"signal {s} is not in architecture section 7")
    pair_count = 0
    for sig, pin in re.findall(r"(?<![A-Za-z0-9_])([A-Z][A-Z0-9_]+) (P\d\.\d{2})", fw):
        if sig in pairs:
            pair_count += 1
            if pairs[sig] != pin:
                errors.append(f"{sig} is {pin} in firmware.md but {pairs[sig]} in architecture section 7")
    print(f"check 3 pins: {len(fw_pins)} pins, {len(fw_sigs)} signal names, {pair_count} signal-pin pairs checked against {len(signals)} architecture signals")

    # 4. RAM budget
    ram_block = section(fw, r"^### 4\.6 ", r"^### |^## ")
    total = None
    items = []
    if ram_block is None:
        errors.append("RAM budget (### 4.6) missing")
    else:
        for cells in table_rows(ram_block):
            if len(cells) < 2 or cells[0] in ("Item",):
                continue
            num = re.fullmatch(r"\**([\d,]+)\**", cells[1])
            if not num:
                continue
            val = int(num.group(1).replace(",", ""))
            if "total" in cells[0].lower():
                total = val
            else:
                items.append(val)
        if total is None:
            errors.append("RAM budget has no Total line")
        else:
            s = sum(items)
            if s != total:
                errors.append(f"RAM lines sum to {s}, stated total is {total}")
            if total > RAM_LIMIT:
                errors.append(f"RAM total {total} exceeds 512 KB ({RAM_LIMIT})")
            print(f"check 4 RAM: {len(items)} lines sum {s}, stated total {total}, limit {RAM_LIMIT}")

    # 7. charger (F3): voltage = the cell's type, current blocked on S12
    a2 = section(arch, r"^## 2\. ", r"^## \d+\. ") or ""
    cellrow = next((ln for ln in a2.splitlines() if ln.startswith("| Cell |")), "")
    mv = re.search(r"([\d.]+) V type", cellrow)
    a176 = section(arch, r"^### 17\.6 ", r"^### |^## ") or ""
    s81 = section(fw, r"^### 8\.1 ", r"^### |^## ") or ""
    tv = re.search(r"`term-microvolt` \| ([\d,]+)", s81)
    cu = re.search(r"`current-microamp` \| ([^\n]*)", s81)
    if not (mv and tv and cu):
        errors.append("cell charge voltage (architecture section 2) or the charger rows of firmware 8.1 not found")
    else:
        fv = int(tv.group(1).replace(",", ""))
        if fv != round(float(mv.group(1)) * 1e6):
            errors.append(f"charge voltage {fv} uV differs from the cell type {mv.group(1)} V of architecture section 2")
        cur = cu.group(1)
        if not (cur.startswith("BLOCKED") and "S12" in cur):
            errors.append("current-microamp is not marked BLOCKED on S12 (a number must not be invented)")
        if re.match(r"[\d,]+ ", cur) or re.match(r"[\d,]+\s*\|", cur):
            errors.append("current-microamp holds a number")
        if not re.search(r"^\| S12 \|", a176, re.M):
            errors.append("open item S12 is not in architecture 17.6")
        if "BLOCKED" not in (re.search(r"\| 0x70 \| T-CHARGE[^\n]*", fw) or re.search("", "")).group(0):
            errors.append("T-CHARGE (section 9.3) is not marked BLOCKED")
        print(f"check 7 charger: {fv} uV against the cell type {mv.group(1)} V; current marked BLOCKED on S12: {cur.startswith('BLOCKED')}")

    # 8. PDM clock arithmetic
    ratios = {48, 50, 64, 80, 96, 150, 192}
    pdm = re.findall(r"([\d.]+) (MHz|kHz), prescaler (\d+), ratio (\d+)", fw)
    if not pdm:
        errors.append("no '<clock>, prescaler N, ratio R' line found")
    for val, unit, presc, ratio in pdm:
        clk = round(float(val) * (1e6 if unit == "MHz" else 1e3))
        n, r = int(presc), int(ratio)
        rate = clk / r
        mode_ok = 1_200_000 <= clk <= 1_650_000 or 450_000 <= clk <= 850_000
        if 32_000_000 / n != clk or not 4 <= n <= 126 or r not in ratios or rate not in (16000, 8000) or not mode_ok:
            errors.append(f"PDM line {val} {unit}, prescaler {n}, ratio {r}: 32 MHz / {n} = {32e6 / n:.0f}, rate {rate:.1f} Hz, mode range ok {mode_ok}")
    print(f"check 8 PDM: {len(pdm)} clock lines checked")

    # 9 to 11. rules stated
    rules = [
        (r"^### 6\.1 ", r"full speed, `wMaxPacketSize` = 64 bytes", "section 6.1 does not set 64-byte bulk packets for full speed"),
        (r"^### 4\.7 ", r"50 ms after", "section 4.7 does not mark motor pulses up to 50 ms after them"),
        (r"^### 4\.5 ", r"MIC_A_CLK is driven low whenever VDD_MIC is off", "section 4.5 lacks the rule: the mic clock low while VDD_MIC is off"),
        (r"^### 5\.1 ", r"no storage line is driven high while VDD_SD is off", "section 5.1 lacks the rule: no storage line high while VDD_SD is off"),
        (r"^### 3\.3 ", r"OLED_PWR_EN[\s\S]*SWIRE", "section 3.3 screen sequence does not name OLED_PWR_EN and SWIRE"),
    ]
    for start, pat, msg in rules:
        block = section(fw, start, r"^### |^## ")
        if block is None or not re.search(pat, block):
            errors.append(msg)
    print(f"check 9-11 rules: {len(rules)} stated rules checked")

    # 12. thermistor
    th = re.search(r"`thermistor-ohms`, `thermistor-beta` \| ([\d,]+)", s81)
    temps = [re.search(rf"`thermistor-{k}-millidegrees` \| ([\d,-]+)", s81) for k in ("cold", "cool", "warm", "hot")]
    if not th or not all(temps):
        errors.append("thermistor ohms or the four temperature limits missing in section 8.1")
    else:
        ohms = int(th.group(1).replace(",", ""))
        tv4 = [int(t.group(1).replace(",", "")) for t in temps]
        if ohms not in (0, 10000, 47000, 100000):
            errors.append(f"thermistor-ohms {ohms} not in the binding's values")
        if not tv4[0] < tv4[1] < tv4[2] < tv4[3]:
            errors.append(f"thermistor limits not ordered cold < cool < warm < hot: {tv4}")
        print(f"check 12 thermistor: {ohms} ohm, limits {tv4} m°C")

    # 13. removed names
    body = fw
    cstart = fw.find("Changes from F3 to F4")
    if cstart == -1:
        cstart = fw.find("Changes from F2 to F3")
    cend = fw.find("Peripheral instances")
    if cstart != -1 and cend > cstart:
        body = fw[:cstart] + fw[cend:]
    banned = ["DAY_LISTEN", "DAY_REC", "VOICE_NOTE", "MEETING_REC", "speech detector",
              "pre-roll", "day mode", "voice note", "voice-note", "listening",
              "4 microphones", "4-channel", "4 channels", "66,048", "129 sectors", "129-sector",
              "Zetta", "135 mAh", "T-SKEW", "T-MIC3", "T-MIC4", "pdm_skew", "record button", "T-BTN"]
    hits = 0
    exempt_from = body.find("\nRun: `design/.venv")
    exempt_to = body.find("\n", exempt_from + 1) if exempt_from != -1 else -1
    for word in banned:
        for m in re.finditer(re.escape(word), body, re.I):
            if word in ("record button", "T-BTN"):
                ls = body.rfind("\n", 0, m.start()) + 1
                if body.startswith("| H1", ls) or ls == exempt_from + 1:
                    continue
            hits += 1
            line_no = body[: m.start()].count("\n") + 1
            errors.append(f"removed name '{word}' still used (line {line_no} outside the change list)")
    print(f"check 13 removed names: {len(banned)} names, {hits} uses outside the change list")

    # 14. microphone rail on in one state only
    mic_on = []
    if states_block is not None:
        for cells in table_rows(states_block):
            m = re.fullmatch(r"`([A-Z][A-Z0-9_]*)`", cells[0])
            if m and len(cells) > 2 and cells[2].lower().startswith("on"):
                mic_on.append(m.group(1))
    s82 = section(fw, r"^### 8\.2 ", r"^### |^## ")
    rows_on = []
    if s82 is None:
        errors.append("power table (### 8.2) missing")
    else:
        for cells in table_rows(s82):
            if len(cells) > 3 and cells[0] != "State" and cells[3].lower().startswith("on"):
                rows_on.append(cells[0])
    rec = mic_on[0] if len(mic_on) == 1 else None
    if len(mic_on) != 1:
        errors.append(f"VDD_MIC is on in {len(mic_on)} states of 1.1 (must be exactly 1): {mic_on}")
    if len(rows_on) != 1 or (rec and rows_on[0] != f"`{rec}`"):
        errors.append(f"VDD_MIC is on in 8.2 rows {rows_on}, expected only `{rec}`")
    print(f"check 14 microphone rail: on in 1.1 for {mic_on}, in 8.2 for {rows_on}")

    # 15. long press only
    lp_count = 0
    if rec:
        for frm, ev, to in transitions:
            if len(frm) != 1 or len(to) != 1:
                continue
            f0, t0, evl = frm[0], to[0], ev.lower()
            if t0 == rec and f0 != rec:
                lp_count += 1
                if not evl.startswith("long press"):
                    errors.append(f"transition {f0} -> {rec} on '{ev}': only a long press may start a recording")
            if f0 == rec and t0 != rec and "press" in evl and not evl.startswith("long press"):
                errors.append(f"transition {rec} -> {t0} on '{ev}': only a long press may stop a recording")
            if ("short press" in evl or "double press" in evl) and f0 != t0:
                errors.append(f"'{ev}' changes state {f0} -> {t0}")
    s21 = section(fw, r"^### 2\.1 ", r"^### |^## ") or ""
    if not re.search(r"\| Long press \| 1,000 ms hold, for start and for stop \|", s21):
        errors.append("section 2.1 does not give the long press as 1,000 ms for start and stop")
    print(f"check 15 long press: {lp_count} transitions into the recording state checked")

    # 16. F3 rules
    f3 = 0
    head = "\n".join(fw.splitlines()[:4])
    if not re.match(r"^# .*\n\nVersion F4, ", fw):
        errors.append("header does not say Version F4")
    if follows(head) != "A5":
        errors.append(f"header follows {follows(head)}, expected architecture A5")
    if not re.search(r"follows[^\n]{0,80}sections 17\.11 and 17\.12", head, re.I):
        errors.append("header does not say it follows architecture sections 17.11 and 17.12")
    for lst in ("Changes from F3 to F4", "Changes from F2 to F3"):
        if lst not in fw:
            errors.append(f"the change list '{lst}' is missing")
    f3 += 4
    a166 = section(arch, r"^### 16\.6 ", r"^### |^## ") or ""
    if "64,000 bytes per second, 230.4 MB per hour" not in a166:
        errors.append("architecture 16.6 no longer gives 64,000 bytes per second, 230.4 MB per hour")
    ch = re.search(r"\| 23 \| 1 \| channels \| (\d+) \|", fw)
    rate = re.search(r"\| 24 \| 4 \| sample_rate_hz \| ([\d,]+) \|", fw)
    if not (ch and rate):
        errors.append("chunk header rows channels or sample_rate_hz not found")
    else:
        bps = int(ch.group(1)) * int(rate.group(1).replace(",", "")) * 2
        if bps != 64000 or bps * 3600 != 230_400_000:
            errors.append(f"audio format gives {bps} bytes per second, architecture 16.6 says 64,000")
        mm = re.search(r"holds ([\d,]+) frames of (\d+) channels", fw)
        pay = re.search(r"\+ (\d+) payload sectors \(([\d,]+) bytes\) = ([\d,]+) bytes", fw)
        if not (mm and pay):
            errors.append("section 5.3 chunk size sentences not found")
        else:
            frames, nch = int(mm.group(1).replace(",", "")), int(mm.group(2))
            sectors, pbytes, cbytes = int(pay.group(1)), int(pay.group(2).replace(",", "")), int(pay.group(3).replace(",", ""))
            if nch != int(ch.group(1)) or frames * nch * 2 != pbytes or sectors * 512 != pbytes or (sectors + 1) * 512 != cbytes:
                errors.append(f"chunk arithmetic: {frames} frames x {nch} ch x 2 = {frames * nch * 2}, {sectors} sectors = {sectors * 512}, chunk {cbytes}")
            if frames / int(rate.group(1).replace(",", "")) != 0.512:
                errors.append("a chunk is not 512 ms")
            for pat, want in ((r"Chunk ring, 3 x ([\d,]+) \| ([\d,]+)", 3), (r"/ (\d+)\) chunks of (\d+) sectors", None)):
                m = re.search(pat, fw)
                if not m:
                    errors.append(f"pattern not found: {pat}")
                elif want == 3:
                    if int(m.group(1).replace(",", "")) != cbytes or int(m.group(2).replace(",", "")) != 3 * cbytes:
                        errors.append(f"chunk ring line {m.group(0)} does not match the chunk of {cbytes} bytes")
                elif int(m.group(1)) != sectors + 1 or int(m.group(2)) != sectors + 1:
                    errors.append(f"chunk area divides by {m.group(1)} / {m.group(2)}, a chunk is {sectors + 1} sectors")
    f3 += 1
    per = section(fw, r"^Peripheral instances", r"^## ") or ""
    mic_rows = [ln for ln in per.splitlines() if ln.startswith("| Microphones")]
    if len(mic_rows) != 1 or "`pdm20`" not in mic_rows[0] or "pdm21" in mic_rows[0]:
        errors.append(f"peripheral table must hold one microphone row on pdm20 only: {mic_rows}")
    if re.search(r"\| `pdm21`", per):
        errors.append("a peripheral table row uses pdm21")
    f3 += 1
    a173 = section(arch, r"^### 17\.3 ", r"^### |^## ") or ""
    names = re.search(r"SW1 = up \((JOY_UP)\), SW3 = down \((JOY_DOWN)\), SW4 = toward the hand \((JOY_LEFT)\), SW5 = toward the fingertip \((JOY_RIGHT)\), SW2 = record button \((BTN_REC)\)", a173)
    s22 = section(fw, r"^### 2\.2", r"^### |^## ") or ""
    s22h = fw[fw.index("### 2.2"):].splitlines()[0]
    if not names:
        errors.append("architecture 17.3 switch-name line not found")
    else:
        for sw, sig in zip(("SW1", "SW3", "SW4", "SW5"), names.groups()):
            if not re.search(rf"{sw} [a-z ]+ {sig} P\d\.\d{{2}}", s22h):
                errors.append(f"heading of 2.2 does not give {sw} on {sig}")
        if not re.search(r"BTN_REC P0\.04 \(SW2\)", fw):
            errors.append("BTN_REC is not given as SW2")
    a165 = section(arch, r"^### 16\.5 ", r"^### |^## ") or ""
    w16 = re.search(r"close within (\d+) ms", a165)
    w22 = re.search(r"close within (\d+) ms", s22)
    if not (w16 and w22) or w16.group(1) != w22.group(1):
        errors.append(f"centre press window: architecture 16.5 {w16 and w16.group(1)} ms, firmware 2.2 {w22 and w22.group(1)} ms")
    f3 += 2
    bad = 0
    for i, ln in enumerate(body.splitlines(), 1):
        if re.search(r"JOY_CENTER|MIC_B_|P0\.03|P1\.24|P1\.25", ln) and not re.search(r"unused|not used", ln):
            bad += 1
            errors.append(f"unused pin named on a line that does not say unused (body line {i}): {ln[:70]}")
    f3 += 1
    a174 = section(arch, r"^### 17\.4 ", r"^### |^## ") or ""
    s31 = section(fw, r"^### 3\.1 ", r"^### |^## ") or ""
    for need in ("W0525AB001D", "full duty", "VDD_3V0", "Q1"):
        if need not in s31:
            errors.append(f"section 3.1 lacks '{need}'")
    a1716 = section(arch, r"^### 17\.16 ", r"^### |^## ") or ""
    if "W0525AB001D" not in a1716 or "full duty" not in a1716:
        errors.append("architecture 17.16 no longer names W0525AB001D at full duty")
    if "full duty" not in a174:
        errors.append("architecture 17.4 no longer says full duty")
    f3 += 1
    a178 = section(arch, r"^### 17\.10 ", r"^### |^## ") or ""
    cap = re.search(r"about ([\d.]+) to ([\d.]+) mAh \[CALC[^\]]*\]\. Recording at ([\d.]+) mA: ([\d.]+) to ([\d.]+) hours", a178)
    s11 = section(fw, r"^### 1\.1 ", r"^### ") or ""
    pm = re.search(r"Time left at ([\d.]+) mA on ([\d.]+) to ([\d.]+) mAh \[CALC\]: B15 (\d+) to (\d+) min, B5 (\d+) to (\d+) min, B2 (\d+) to (\d+) min", s11)
    pcts = {k: int(v) for k, v in re.findall(r"\*\*(B\d+)\*\*: state of charge at or under (\d+) %", s11)}
    if not (cap and pm and set(pcts) == {"B15", "B5", "B2"}):
        errors.append("battery recomputation lines not found (architecture 17.10 capacity line of 17.10, firmware 1.1 minutes line, three percentages)")
    else:
        ma, lo, hi = float(pm.group(1)), float(pm.group(2)), float(pm.group(3))
        if (lo, hi) != (float(cap.group(1)), float(cap.group(2))) or ma != float(cap.group(3)):
            errors.append(f"firmware battery {lo} to {hi} mAh at {ma} mA differs from architecture 17.10")
        want = []
        for k in ("B15", "B5", "B2"):
            want += [int(pcts[k] / 100 * c / ma * 60 + 0.5) for c in (lo, hi)]
        got = [int(x) for x in pm.groups()[3:]]
        if want != got:
            errors.append(f"battery minutes {got} differ from the computation {want}")
        s85 = section(fw, r"^### 8\.5 ", r"^### |^## ") or ""
        hr = re.search(r"\| Hours on [\d.]+ to [\d.]+ mAh \[CALC\] \| ([\d.]+) to ([\d.]+) \|", s85)
        if not hr or abs(float(hr.group(1)) - lo / ma) > 0.1 or abs(float(hr.group(2)) - hi / ma) > 0.1:
            errors.append(f"recording hours in 8.5 {hr and hr.groups()} differ from {lo / ma:.2f} to {hi / ma:.2f}")
        if hr and (hr.group(1), hr.group(2)) != (cap.group(4), cap.group(5)):
            errors.append(f"recording hours {hr.groups()} differ from architecture 17.10 {cap.group(4)} to {cap.group(5)}")
        print(f"check 16 battery: minutes {got}, hours {hr and hr.groups()}")
    f3 += 1
    s61 = section(fw, r"^### 6\.1 ", r"^### |^## ") or ""
    if not re.search(r"four pads.*VBUS, D-, D\+, GND", s61):
        errors.append("section 6.1 does not give four pads in the order VBUS, D-, D+, GND")
    if "VBUS, D-, D+, GND" not in a173:
        errors.append("architecture 17.3 pad order not found")
    f3 += 1
    print(f"check 16 F3 rules: {f3} rule groups checked")

    # 17. F4 rules
    f4 = 0
    clean = lambda s: s.replace("`", "")
    trows = []
    for cells in table_rows(trans_block or ""):
        if len(cells) >= 4 and cells[0] != "From":
            trows.append((clean(cells[0]), cells[1], clean(cells[2]), cells[3]))
    centre_ev = re.compile(r"(long|short|double) press of the joystick centre")
    dir_words = re.compile(r"\b(up|down|left|right|toward|direction|joystick|button)\b", re.I)
    if rec:
        starts = [r for r in trows if r[2] == rec and r[0] != rec]
        if len(starts) != 1 or starts[0][0] != "STANDBY" or not re.fullmatch(r"long press of the joystick centre", starts[0][1]):
            errors.append(f"the recording state must be entered by exactly one row, a long press of the joystick centre from STANDBY: {starts}")
        stops = [r for r in trows if r[0] == rec and r[1].lower().startswith("long press")]
        if len(stops) != 1 or stops[0][2] != "STANDBY" or "close" not in stops[0][3]:
            errors.append(f"a long press in {rec} must go to STANDBY and close the recording: {stops}")
        for r in trows:
            if r[0] == rec and "short press" in r[1].lower() and not (r[2] == rec and "highlight" in r[3]):
                errors.append(f"short press in {rec} must stay in it and mark a highlight: {r}")
            if r[0] == rec and "double press" in r[1].lower() and not (r[2] == rec and r[3].startswith("nothing")):
                errors.append(f"double press in {rec} must do nothing: {r}")
            if dir_words.search(r[1]) and not centre_ev.fullmatch(r[1]) and (rec in (r[0], r[2]) or r[0] != r[2]):
                errors.append(f"an event naming a direction, the joystick or a button touches the recording state or changes state: {r}")
            if centre_ev.fullmatch(r[1]) is None and re.search(r"press", r[1], re.I) and not r[1].lower().startswith(("long press", "short press", "double press")):
                errors.append(f"unknown press event: {r}")
    f4 += 1
    s21t = table_rows(s21)
    hdr = next((c for c in s21t if c[0] == "Gesture"), None)
    grows = {c[0]: c for c in s21t if len(c) >= 5 and c[0] != "Gesture"}
    if not hdr or not rec:
        errors.append("gesture table of 2.1 not found")
    else:
        ssr = re.compile(r"(start|stop|begin|end)\w*\s+(a |the )?recording", re.I)
        scols = [i for i, h in enumerate(hdr) if i > 1]
        i_rec = next((i for i, h in enumerate(hdr) if f"`{rec}`" in h), None)
        i_sb = next((i for i, h in enumerate(hdr) if "`STANDBY`" in h), None)
        lp = grows.get("Long press")
        if not lp or i_rec is None or i_sb is None or "stop the recording" not in lp[i_rec] or "start a recording" not in lp[i_sb]:
            errors.append("2.1 gesture table: the long press must stop the recording in the recording state and start one in STANDBY")
        for name in ("Short press", "Double press", "Graze", "Held 450 ms to 999 ms"):
            row = grows.get(name)
            if not row:
                errors.append(f"2.1 gesture table lacks the row {name}")
                continue
            for i in scols:
                if ssr.search(row[i]):
                    errors.append(f"2.1 gesture table: '{name}' starts or stops a recording: {row[i]}")
                if name == "Double press" and not row[i].startswith("does nothing"):
                    errors.append(f"2.1 gesture table: double press must do nothing: {row[i]}")
                if name in ("Graze", "Held 450 ms to 999 ms") and not row[i].startswith("ignored"):
                    errors.append(f"2.1 gesture table: '{name}' must be ignored: {row[i]}")
    f4 += 1
    m22 = table_rows(s22)
    h22 = next((c for c in m22 if c[0] == "Screen"), None)
    bad_dir = re.compile(r"(start|stop|begin)\w*\s+(a |the )?recording|highlight|long press", re.I)
    if not h22:
        errors.append("mapping table of 2.2 not found")
    else:
        ix = {h.lower(): i for i, h in enumerate(h22)}
        for c in m22:
            if c[0].startswith("SCR_"):
                for d in ("up", "down", "left", "right"):
                    if bad_dir.search(c[ix[d]]):
                        errors.append(f"2.2: a direction ({d}) on {c[0]} starts or stops a recording or marks a highlight: {c[ix[d]]}")
                if c[0] == "SCR_RECORDING" and "highlight" not in c[ix["centre"]]:
                    errors.append("2.2: the centre on SCR_RECORDING must mark the highlight (collision C1)")
    if not re.search(r"A direction never starts or stops a recording", s22):
        errors.append("2.2 does not say a direction never starts or stops a recording")
    colls = set(re.findall(r"^- \*\*(C\d)\*\*", s22, re.M))
    if colls != {"C1", "C2", "C3", "C4"}:
        errors.append(f"2.2 collisions listed {sorted(colls)}, expected C1 to C4")
    f4 += 1
    cs = {}
    for c in s21t:
        if len(c) >= 4 and c[0] in ("`SW2`", "`PAIR`"):
            cs[c[0]] = c
    if set(cs) != {"`SW2`", "`PAIR`"} or not all(c[1] and "ms" in c[2] and c[3] for c in cs.values()):
        errors.append(f"2.1 table 'Centre source' must give both cases with an input, a debounce in ms and a timing: {sorted(cs)}")
    elif "SW2 on BTN_REC" not in cs["`SW2`"][1] or "SW1 with SW3" not in cs["`PAIR`"][1]:
        errors.append("2.1 'Centre source': case SW2 must name SW2 on BTN_REC, case PAIR must name SW1 with SW3")
    if "CENTRE_SOURCE" not in s21:
        errors.append("2.1 does not name CENTRE_SOURCE")
    prm = {c[0]: c[1] for c in s21t if len(c) == 2}
    def pint(key, pat):
        mm = re.search(pat, prm.get(key, ""))
        return int(mm.group(1).replace(",", "")) if mm else None
    sh_hi = pint("Short press", r"40 ms to (\d+) ms")
    warn = pint("Warning pulse", r"at (\d+) ms")
    lng = pint("Long press", r"([\d,]+) ms hold")
    hold = pint("Release hold-off", r"^(\d+) ms")
    deb = pint("Debounce", r"(\d+) ms")
    gap = pint("Double-press window", r"starting (\d+) ms to")
    if None in (sh_hi, warn, lng, hold, deb, gap):
        errors.append(f"2.1 parameter table lacks a value: {(sh_hi, warn, lng, hold, deb, gap)}")
    else:
        if not sh_hi < warn < lng:
            errors.append(f"short-press ceiling {sh_hi} ms, warning {warn} ms and long press {lng} ms are not in order")
        if not deb < hold < gap:
            errors.append(f"release hold-off {hold} ms is not between the debounce {deb} ms and the double-press gap {gap} ms")
        if lng != 1000:
            errors.append(f"long press is {lng} ms, architecture 17.11 fixes 1.0 s")
    if not re.search(r"^\| MW \|[^\n]*\| \d+ on \| \d+ \|", s31, re.M):
        errors.append("the motor table (3.1) lacks the warning pattern MW")
    f4 += 1
    s12 = section(fw, r"^### 1\.2 ", r"^## ") or ""
    for r in trows:
        if r[2] == "CHARGING" and "charge on" not in r[3]:
            errors.append(f"the row into CHARGING does not turn the charger on: {r}")
        if r[0] in ("SHIP", "OFF") and r[2] == "BOOT" and "VBUS" in r[1] and "charge on" not in r[3]:
            errors.append(f"the ship-mode exit row does not turn the charger on: {r}")
    if not any(r[0] == "SHIP" and r[2] == "BOOT" and "VBUS" in r[1] for r in trows):
        errors.append("the row that leaves ship mode on VBUS is missing")
    ce = re.search(r"`charging-enable` \| ([^\n]*)", s81)
    if not ce or not ce.group(1).startswith("on whenever VBUS is present") or "off until" in ce.group(1):
        errors.append(f"`charging-enable` must be on whenever VBUS is present: {ce and ce.group(1)[:60]}")
    cc = re.search(r"`current-microamp` \| ([^\n]*)", s81)
    for need in ("CHARGE_CURRENT", "at most 1 C", "15 to 20 mA", "32 mA"):
        if not cc or need not in cc.group(1):
            errors.append(f"`current-microamp` row lacks '{need}'")
    if "R-CHG" not in s12:
        errors.append("rule R-CHG is not stated in section 1.2")
    f4 += 1
    s86 = section(fw, r"^### 8\.6 ", r"^### |^## ") or ""
    for need in ("VBUS is an input only", "nothing is driven onto any pad when no case is present"):
        if need not in s86:
            errors.append(f"section 8.6 lacks '{need}'")
    a1711 = section(arch, r"^### 17\.11 ", r"^### |^## ") or ""
    a1712 = section(arch, r"^### 17\.12 ", r"^### |^## ") or ""
    for need in ("long press of 1.0 s on the joystick's centre starts a recording", "a real switch under the nub's centre", "two-opposite-switches reading"):
        if need not in a1711:
            errors.append(f"architecture 17.11 no longer says '{need}'")
    if "INSIDE face of the band" not in a1712 or "VBUS is an input only" not in a1712:
        errors.append("architecture 17.12 no longer puts the pads on the inside face with VBUS an input only")
    if "just have long press on joystick as recording button" not in fw:
        errors.append("the owner's words about the joystick are not quoted")
    f4 += 1
    print(f"check 17 F4 rules: {f4} rule groups checked, {len(trows)} transition rows read")

    # 5. end matter
    if not re.search(r"^## questions_for_owner\s*$", fw, re.M):
        errors.append("section questions_for_owner missing")
    last = fw.rstrip("\n").splitlines()[-1] if fw.strip() else ""
    if not re.match(r"^RESULT: (done|blocked), ", last):
        errors.append(f"last line is not a RESULT line: {last[:60]!r}")
    print("check 5 end: questions_for_owner and RESULT line")

    for e in errors:
        print(f"FAIL {e}")
    print(f"{len(errors)} failures")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
