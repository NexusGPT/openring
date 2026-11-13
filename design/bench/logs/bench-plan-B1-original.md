# Bench prototype plan

Version B1, 2026-11-10. Written to be built by the owner or by a partner without change: every part has its order code, every wire its pin, every test its pass line (owner, 2026-11-10: "I will decide later if I build it or a partner does. At the end of the day, it shoul dbe the same"). Facts and prices come from `design/bench/bench-kits.md` (listings read on 2026-11-10). A line tagged [CHECK] names one thing to confirm on the part itself before wiring; nothing else is left open.

## 1. What the bench build is, and what it proves

A table-top recorder made from development kits and jumper wires. It has no ring shape. It runs the ring's own microphone, power chip and vibration motor on Nordic's development kit, and it answers three questions before any custom board is paid for:

| # | Question | Pass line (written before the test) |
|---|---|---|
| Q1 | Is the speech quality as good as a Plaud recorder's? | Word error rate of the bench recorder is not higher than the Plaud's in each of the 6 conditions of section 5 |
| Q2 | How much current does recording take? | 4.0 mA or less from a 3.8 V supply while recording 2 channels (the estimate in `design/architecture.md` 16.8). Above it, the hours in 16.8 are recomputed from the measured value |
| Q3 | Do the controls behave as designed? | Long press 1.0 s starts, long press 1.0 s stops, short press marks a highlight, the light is on for exactly the time the microphones are powered, one vibration on start and two on stop (`design/firmware.md`) |

The screen is NOT on bench build 1: no seller offers this screen with an adapter board and example code (`bench-kits.md` section 4). It joins when Tailor Pixels sends the start-up code (architecture open item 12.1).

## 2. What to buy

| # | Item | Order code | Seller | Price (USD, 1 unit) | Stock shown | Why |
|---|---|---|---|---|---|---|
| 1 | Nordic nRF54LM20 DK | NRF54LM20-DK | Digi-Key | 45.00 | 321 | The ring's main chip family, with debugger and USB |
| 2 | Nordic Power Profiler Kit II | NRF-PPK2 | Digi-Key | 107.30 | 1,608 | Measures current from 200 nA to 1 A (Q2) |
| 3 | Nordic nPM1300 EK | NPM1300-EK | Digi-Key | 64.35 | 158 | The ring's power chip: charger, two supplies, switches |
| 4 | Infineon microphone kit for IM68D128BV01 | KITIM68D128BV01FLEXTOBO1 | Digi-Key | 75.19 | 9 | The ring's microphone on flex boards. Lead time 97 weeks when stock ends: buy first |
| 5 | Adafruit microSD breakout board+ | 254 | Adafruit | 7.50 | in stock | Stand-in for the ring's storage chip (same SPI protocol). The 4 GB chip breakout (Adafruit 6039, 12.50) is out of stock |
| 6 | Vybronics coin motor | VC0720B088L | Digi-Key | 3.23 | 714 | The ring's vibration motor |
| 7 | Adafruit MOSFET driver | 5648 | Adafruit | 3.95 | in stock | Switches the motor from a chip pin |
| 8 | Lithium polymer cell 40 mAh, JST-PH, protected | PRT-13852 | SparkFun | 7.14 | in stock | Battery of the ring's size class |
| | **Total of lines 1 to 8** | | | **313.66** | | |
| 9 | Plaud NotePin (reference device) | | plaud.ai | 159.00 | pre-order | The device to beat (Q1). Plaud Note at 159.00 is the other choice |
| 10 | microSD card 8 GB or more, 2 push buttons, 1 red LED, 680 ohm resistor, jumper wires, breadboard | | any | not priced | | Small parts |
| 11 | A loudspeaker with a flat response for speech and a sound level meter | | any | not priced | | For section 5 |

Links for every line: `design/bench/bench-kits.md`, sections 1 to 8.

## 3. Wiring

Signal names and chip pins are the ring's own (`design/architecture.md` sections 7 and 16.6), so the bench firmware moves to the ring unchanged.

| Signal | Chip pin | Goes to |
|---|---|---|
| MIC_A_CLK | P1.13 | Infineon adapter board, CLOCK of microphone 1 and microphone 2 |
| MIC_A_DATA | P1.11 | Infineon adapter board, DATA of both microphones (microphone 1 SELECT to ground = left, microphone 2 SELECT to supply = right) |
| VDD_MIC | nPM1300 EK load switch 1 output | microphone supply, 1.8 V |
| SD_SCK, SD_MOSI, SD_MISO, SD_CS | P2.01, P2.02, P2.04, P2.05 | microSD breakout CLK, DI, DO, CS; breakout supply from the 3.0 V output |
| PMIC_SDA, PMIC_SCL, PMIC_INT | P1.26, P1.27, P1.28 | nPM1300 EK TWI header and interrupt |
| BTN_REC | P0.04 | push button to ground |
| JOY_LEFT, JOY_RIGHT | P0.08, P1.31 | two push buttons to ground (the ring's 2-direction thumb control) |
| MOTOR | P3.01 | Adafruit MOSFET driver input; the motor between the 3.0 V output and the driver |
| Recording light | no chip pin | 3.0 V, 680 ohm, LED, then a transistor whose gate is VDD_MIC (as in the ring) |
| Battery | nPM1300 EK battery connector | 40 mAh cell |
| Supplies | nPM1300 EK output 1 = 1.8 V, output 2 = 3.0 V | DK supply input and the parts above |

- Current measurement (Q2): the Power Profiler Kit II in source mode at 3.8 V on the nPM1300 EK's battery input, in place of the cell.
- [CHECK 1] On the DK, find each chip pin above on headers P1 to P5 and P17 (printed on the board). The DK's pin table could not be read: Nordic's user guide is behind a browser check. Open it in a browser: `https://docs.nordicsemi.com` , nRF54LM20 DK, "Connector interface".
- [CHECK 2] On the nPM1300 EK, read the battery connector's polarity and the TWI header from its user guide (same site) before plugging the cell. The cell's connector is JST-PH with 2 pins.
- [CHECK 3] The DK has its own nPM1300 that supplies the chip. Set the DK to take its supply from the external EK as its guide describes, or run the first tests on the DK's own power chip and add the EK second.

## 4. Firmware starting point

- Tool: Nordic's nRF Connect SDK (Zephyr), board target for the nRF54LM20 DK.
- Start from four of the SDK's own samples, then join them: the digital microphone sample (PDM capture), the file system sample on an SD card over SPI, the nPM1300 sample (charger and supplies), and the button sample. Sample names change between SDK versions: pick them in the SDK's sample browser. I list them from knowledge of the SDK and did not open the SDK today.
- Settings fixed by the design: microphone clock 1.280 MHz, ratio 80, 16 kHz, 16 bit, 2 channels; raw file of 64,000 bytes per second; behaviour and states from `design/firmware.md`.
- Order of work: (1) record 10 seconds from 2 microphones to memory and send it over USB; (2) write the stream to the card; (3) add the button rules and the light; (4) add the power chip and the motor; (5) measure current.

## 5. Test against the Plaud (Q1)

Method taken from published sources (`bench-kits.md` section 9): the LibriSpeech test-clean corpus (licence CC BY 4.0), the Whisper speech-to-text model (MIT licence), the jiwer scoring tool (Apache-2.0), and the two distances and three noise levels that Plaud itself publishes for its chamber test.

1. Take 50 sentences from LibriSpeech test-clean, the same 50 for every run.
2. Play them from the loudspeaker. Set the speech level once, at 1 m, with the sound level meter, and write the value down.
3. Put the bench microphones and the Plaud side by side. Record both at the same time.
4. Six conditions: 1 m and 3 m, each at three noise levels: quiet (about 35 dB), moderate (about 55 dB), loud (about 70 dB). Noise comes from a second loudspeaker playing recorded office noise.
5. Export both recordings. Transcribe both with the same Whisper model. Score each against the corpus text with jiwer.
6. Result table: 6 rows, word error rate of the bench and of the Plaud, and the difference. Pass line: Q1 in section 1.

- The bench recording is 2 raw channels. Score channel 1 alone first, then the two channels combined toward the loudspeaker. The second number shows what two microphones add.
- [CHECK 4] Plaud's export format (MP3 or WAV, sample rate) is not confirmed: its support page refused automated reading. Note what the device exports on the day.

## 6. What the bench build does not cover

- The screen (see section 1).
- The ring's size, its antenna and its microphone openings: sound through a slot in a metal wall is bench test B7 on the first housing.
- The curved battery in the band: the bench uses a flat 40 mAh cell charged to 4.2 V.

## 7. Two findings the owner should know

1. **The kit on sale carries the nRF54LM20B, and the ring design names the nRF54LM20A.** Nordic's page and Digi-Key both describe the kit with the B chip. The bench runs on the B kit, the only one on sale. Which of the two the ring uses is decided after reading Nordic's revision overview for both; it is added to the supplier list as item S11.
2. **Microphone kits are scarce:** 9 in stock for the ring's microphone, and a 97-week lead time after that.
