# How the software is built into a package for a manufacturer

Date: 2026-11-11. Sources: the behaviour specification `design/firmware.md` (version F6, cited as FW), the assembly order `design/mfg/assembly/assembly.md` (AS), and the reader's findings `design/software/research-production.md` (RP with its section) and `design/software/research-toolchain.md` (RT). Tags of the reader's files: [F] = the page was opened and read; [S] = search text only. Nordic's manual pages refused automated reading, so every Nordic command here is [S] and must be confirmed on the bench.

## 0. What exists and what does not

- Exists: the factory test list with its pass limits (FW 9.3, 13 commands), the factory flow by assembly step (FW 9.3 table; AS steps 5, 16, 18, 20, 21, 24, 25, 26, 27), the memory layout and the update rules (FW 9.2).
- Does not exist: the source code (W1 to W15, FW 10.2), the test fixture and its program (W13), the signing key, the battery model, the screen driver.

## 1. What the manufacturer receives

A published intake list of a contract manufacturer asks for exactly these items (Seeed Fusion, RP 9 [F]): the files to flash with version, date and hardware revision; flashing instructions (programmer, connections, software, steps); the test environment; the test steps; the expected result and the pass or fail limit of each test.

For this ring:

| Item | Content | State |
|---|---|---|
| Programming file | one file with the start program (MCUboot) and the signed software, for the bare board | to build; Nordic names it `merged.hex` (RP 1 [S]) |
| Settings content | the settings area with the factory mark set to 1 | to build (FW 9.3) |
| Update file | the signed image that the case or a computer sends over USB | to build (FW 9.2) |
| Release note | version, date, hardware revision it fits, checksum (SHA-256) of each file | to write per release |
| Flashing instruction | probe, the pads TP3, TP4, TP5, supply and ground, the command, read-back, the lock | steps exist (FW 9.3, AS step 5); the command is [S] |
| Test specification | the 13 test commands, method and pass limit of each, by assembly step | exists (FW 9.3) |
| Fixture protocol | the USB commands of FW section 6 and the factory sub-commands | exists as specification; the fixture program is W13 |
| Shipping state | first charge to 50 percent, then SHIP_ENTER; sample rings SHIP_SAMPLE | exists (FW 9.3, AS steps 26, 27) |
| Not in the package | the private signing key, the source code (unless the contract says so) | |

The ring uses one software image for test and for shipping; a mark in the settings opens the factory tests and SHIP_ENTER clears it (FW 9.3). Say this in the release note, because makers expect either one image or two and must not mix them (RP 9 [F]).

## 2. Build the release

1. Fix the SDK version (see bring-up.md section 3) and build with the start program in one step. Zephyr's documented form, shown for another board (RT 4 [F]):
   `west build -b <board> --sysbuild <application folder> -- -DSB_CONFIG_BOOTLOADER_MCUBOOT=y`
   For the ring the board is the ring's own board `ring_nrf54lm20a` (W1).
2. Outputs, by Nordic's names (RP 1 [S]): `merged.hex`, the start program and the application together, for the programming contacts; `dfu_application.zip`, the update image with a manifest. The ring's own USB update sends the signed image (FW 9.2). Reports exist of a `merged.hex` that lacked the application on a sister chip (RP 1 [S], forum): always read the programmed board back and compare.
3. Memory layout to respect (FW 9.2): start program 64 KB at 0x00000000; running image 976 KB at 0x00010000; update image 976 KB at 0x00104000; settings 20 KB at 0x001F8000.

## 3. Sign the software (RP 2)

- The start program accepts only software signed with your key. MCUboot ships example keys and says they "should never be used for production, since the private key is publicly available" ([F], docs.mcuboot.com).
- Make a key once: `imgtool.py keygen -k <name>.pem -t ed25519` ([F]; the tool supports rsa-2048, rsa-3072, ecdsa-p256 and ed25519). Which types the nRF54LM20A build accepts was not found in a readable page: confirm before you choose.
- Give the build the key through `CONFIG_BOOT_SIGNATURE_KEY_FILE`. It accepts a public-key-only file, so "the signing private key is held by a release team and only an exported public key is provided to bootloader builders" ([F]).
- Production start programs "should embed only the production public key" ([F]). Development units may accept a development key as well.
- Keep the private key offline, with one backup, with you. Whoever holds it can make software that every ring accepts. The manufacturer does not need it.
- On this chip family the public key can also be stored in the chip's key store (KMU) instead of inside the start program, and an erase of everything removes it (RP 2 [S]). Decide one way before the first production build.

## 4. Version and downgrade (RP 3)

- Set the version in a `VERSION` file of the application (Nordic's recommended way since SDK 2.5.0, [S]).
- Conflict to settle: MCUboot's downgrade prevention "is only available when the overwrite-based image update strategy is used" ([F]). The ring's specification uses swap with rollback (FW 9.2). With swap, the start program does not refuse an older signed image. Either the ring's own update code refuses a lower version (a rule to add to FW 9.2), or the mode changes to overwrite and the rollback is lost. Rollback matters more on a ring that cannot be opened; the first way is the default.

## 5. Program each board in the factory

- Access: TP3 SWDCLK, TP4 SWDIO, TP5 NRESET, supply and ground, on the bare board only (AS step 5).
- Command ([S], RP 4): `nrfutil device program --firmware merged.hex --options chip_erase_mode=ERASE_ALL`, then `nrfutil device reset --reset-kind=RESET_PIN`. One forum report says SEGGER's own tool failed on an external nRF54LM20A where `nrfutil` worked through the same probe (RP 4 [S]).
- If the key lives in the key store: it is written by a separate step, `nrfutil device x-provision-keys` (RP 4 [S], forum answer by Nordic).
- Read back and compare, then set the lock of the start program (FW 9.2 rule 4) and decide on the debug lock (bring-up.md section 9). A chip with the debug lock and without the erase lock can be opened again by an erase of everything; with both it cannot be recovered (RP 4 [S]).
- Chips can also be bought pre-programmed from a distributor or a programming house; no readable Nordic page on it was found (RP 4).

## 6. Data per ring

- Each chip carries a factory-set 48-bit device address (FICR DEVICEADDR; RP 5 [S]). Use it as the ring's identity.
- The fixture records per ring: device address, software version, hardware revision, ring size, every test value, date. This record is the traceability a maker and a regulator ask for (RP 5 [F], Seeed).

## 7. Test each ring

- The 13 test commands with method and limit are in FW 9.3: both microphones, screen, joystick, centre press, motor, light, storage, radio, charger, crystal, and the two ship commands.
- They run at the assembly steps of the FW 9.3 flow table: board (step 5), cables joined (16), open ring (18), after the dam (20), after the liner (21), after the leak test (24), closed ring (25), first charge (26), ship (27).
- Radio: the ring's own test is an advertising level seen by the fixture (T-RADIO). Nordic's Direct Test Mode sample measures transmit power, receiver sensitivity, frequency offset and packet error rate; it is marked experimental and is meant for certification and debugging (RP 6 [S]). The certification lab needs it; the line can keep T-RADIO.
- Another maker's practice: check the current draw right after programming and after power off (RP 6 [F], Movesense).

## 8. What must exist before the product is sold (RP 7, RP 8)

- Bluetooth: "ALL Bluetooth Products must be qualified", under your own membership; "Your supplier or other member companies cannot qualify your products on your behalf" ([F], bluetooth.com). Fee read on the Bluetooth SIG's fee page, effective 1 March 2026: 12,000 US dollars for an Adopter member, 6,000 for an Associate member (process.md section 4 [F]).
- EU: CE marking under the Radio Equipment Directive after testing and conformity assessment ([F], European Commission page; the directive's text was not readable).
- US: FCC certification before marketing ([S]).
- Battery: the cell needs a UN 38.3 transport test summary from its maker ([S]).
- Licences that travel with the binary: Zephyr and MCUboot are Apache 2.0 ([F]); Nordic's binary libraries carry Nordic's 5-clause licence: use only with a Nordic chip, no reverse engineering, and the notice in the documentation unless the software is embedded in a Nordic chip in a product ([F]).

## 9. Order of work to reach a package

1. Write and prove the software on the development kit (bring-up.md section 5).
2. Make the signing key; settle key place (in the start program or in the key store) and the downgrade rule.
3. Design the two fixtures (bare board; closed ring through the pads) and write the fixture program (W13).
4. Build release 0.1, program three boards, run the whole flow of section 7 by hand.
5. Freeze the package of section 1 with checksums; hand it to the maker with a golden sample ring.

## 10. Not verified

- Every Nordic command and file name marked [S].
- The signature types of the nRF54LM20A build, and the start program's size with a rescue mode (bring-up.md section 1).
- Nordic's own production guide for this chip family (found, not readable): "nRF54L Series Production Programming".
