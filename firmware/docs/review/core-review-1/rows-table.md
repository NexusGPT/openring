| row | spec line | from | event | to | code: table line / actions line | action list in code (ordered) | test line | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 133 | SHIP | VBUS appears (case contact) | BOOT | 4 / 22 | CHARGE_ON | 28 | pass |
| 2 | 134 | OFF | VBUS appears | BOOT | 5 / 23 | CHARGE_ON | 29 | pass |
| 3 | 135 | BOOT | init done, superblock open flag clear, no VBUS, battery [guard OPEN_CLEAR_NO_VBUS_ABOVE_B5] | STANDBY | 6 / 26 | SD_OFF | 30 | pass |
| 4 | 136 | BOOT | init done, superblock open flag set [guard OPEN_SET] | RECOVERY | 7 / 29 | SD_ON | 31 | pass |
| 5 | 137 | BOOT | init done, VBUS present [guard VBUS] | CHARGING | 8 / 32 | SD_OFF CHARGE_ON | 32 | pass |
| 6 | 138 | BOOT | storage init fails 3 times, 200 ms apart | ERR_STORAGE_FAULT | 9 / 36 | LOG_EVENT MF | 33 | pass |
| 7 | 139 | BOOT | battery at B2 and no VBUS [guard NO_VBUS] | OFF | 10 / 40 | SHIP_MODE | 34 | pass |
| 8 | 140 | BOOT | battery at B5 and no VBUS [guard NO_VBUS] | ERR_BATTERY_LOW | 11 / 43 | M3 | 35 | pass |
| 9 | 141 | RECOVERY | scan done, no VBUS [guard NO_VBUS] | STANDBY | 12 / 46 | WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF | 36 | pass |
| 10 | 142 | RECOVERY | scan done, VBUS present [guard VBUS] | CHARGING | 13 / 51 | WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF CHARGE_ON | 37 | pass |
| 11 | 143 | RECOVERY | read error during scan | ERR_STORAGE_FAULT | 14 / 57 | LOG_EVENT MF | 39 | pass |
| 12 | 144 | STANDBY | long press of the joystick centre | RECORDING | 15 / 61 | OPEN M1 | 40 | pass |
| 13 | 145 | STANDBY | short press of the joystick centre | STANDBY | 16 / 66 | SCREEN_CENTRE MT SCREEN_ON SCR_STATUS_5S | 41 | pass with note F5 (extra MT on the screen-on branch) |
| 14 | 146 | STANDBY | double press of the joystick centre | STANDBY | 17 / 75 | (none) | 42 | pass |
| 15 | 147 | STANDBY | menu "Power off" confirmed | OFF | 18 / 77 | SAVE_SETTINGS_TIME M2 SHIP_MODE | 43 | pass |
| 16 | 148 | STANDBY | VBUS appears | CHARGING | 19 / 82 | CHARGE_ON | 44 | pass |
| 17 | 149 | STANDBY | battery reaches B15 | STANDBY | 20 / 85 | M3 SCR_STATUS_5S | 45 | pass |
| 18 | 150 | STANDBY | battery reaches B5 | ERR_BATTERY_LOW | 21 / 92 | M3 | 46 | pass |
| 19 | 151 | STANDBY | battery reaches B2 | OFF | 22 / 95 | SAVE_SETTINGS_TIME SHIP_MODE | 47 | pass |
| 20 | 152 | STANDBY | free space at SFULL | ERR_STORAGE_FULL | 23 / 99 | M3 | 48 | pass |
| 21 | 153 | RECORDING | long press of the joystick centre | STANDBY | 24 / 102 | CLOSE M2 | 49 | pass |
| 22 | 154 | RECORDING | short press of the joystick centre | RECORDING | 25 / 106 | HIGHLIGHT MH SCR_RECORDING_3S | 50 | pass |
| 23 | 155 | RECORDING | double press of the joystick centre | RECORDING | 26 / 111 | (none) | 51 | pass |
| 24 | 156 | RECORDING | BLE control "highlight" from a bonded phone | RECORDING | 27 / 113 | HIGHLIGHT MH | 52 | pass |
| 25 | 157 | RECORDING | VBUS appears (case insertion during a recording) | CHARGING | 28 / 117 | CLOSE M2 CHARGE_ON | 53 | pass |
| 26 | 158 | RECORDING | battery reaches B15 | RECORDING | 29 / 122 | M3 | 54 | pass |
| 27 | 159 | RECORDING | battery reaches B5 | ERR_BATTERY_LOW | 30 / 128 | CLOSE M3 | 55 | pass |
| 28 | 160 | RECORDING | battery reaches B2 | OFF | 31 / 132 | CLOSE SHIP_MODE | 56 | pass |
| 29 | 161 | RECORDING | free space reaches S30 | RECORDING | 32 / 136 | M3 SCR_MSG_30MIN_3S | 57 | pass |
| 30 | 162 | RECORDING | free space at SFULL | ERR_STORAGE_FULL | 33 / 143 | CLOSE M3 | 58 | pass |
| 31 | 163 | RECORDING | chunk write fails 3 times | ERR_STORAGE_FAULT | 34 / 147 | STOP_PDM CLOCKS_LOW MIC_OFF MF | 59 | pass |
| 32 | 164 | RECORDING | the PDM instance gives no block for 100 ms | ERR_MIC_FAULT | 35 / 153 | CLOSE MF | 61 | pass |
| 33 | 165 | RECORDING | sudden power loss (cell cut, short, brown-out) during a | BOOT | 36 / 157 | (none) | 62 | pass |
| 34 | 166 | CHARGING | USB configured by the case (`USBD_MSG_CONFIGURATION`) | TRANSFER | 37 / 159 | SD_ON MOUNT | 63 | pass |
| 35 | 167 | CHARGING | VBUS removed, free space above SFULL, battery above B5 [guard ABOVE_SFULL_ABOVE_B5] | STANDBY | 38 / 163 | (none) | 64 | pass |
| 36 | 168 | CHARGING | VBUS removed, free space at SFULL [guard SFULL] | ERR_STORAGE_FULL | 39 / 164 | (none) | 65 | pass |
| 37 | 169 | CHARGING | VBUS removed, battery at B5 [guard AT_B5] | ERR_BATTERY_LOW | 40 / 165 | (none) | 66 | pass |
| 38 | 170 | CHARGING | nPM1304 event charge error | ERR_CHARGER | 41 / 167 | LOG_CHARGE_ERROR CHARGE_OFF MF | 67 | pass |
| 39 | 171 | CHARGING | long press | CHARGING | 42 / 172 | M3 SCR_MSG_IN_CASE_3S | 68 | pass |
| 40 | 172 | TRANSFER | USB suspended or unconfigured by the case | CHARGING | 43 / 176 | FINISH_COMMAND SD_OFF CHARGE_ON | 69 | pass |
| 41 | 173 | TRANSFER | VBUS removed | STANDBY | 44 / 181 | ABORT_COMMAND SD_OFF | 70 | pass |
| 42 | 174 | TRANSFER | command FW_END accepted | BOOT | 45 / 185 | REQUEST_UPGRADE_TEST REBOOT | 71 | pass |
| 43 | 175 | TRANSFER | command FACTORY_ENTER with the factory flag set [guard FACTORY_FLAG] | FACTORY_TEST | 46 / 189 | FACTORY_MODE | 72 | pass |
| 44 | 176 | TRANSFER | long press | TRANSFER | 47 / 192 | M3 | 73 | pass |
| 45 | 177 | ERR_STORAGE_FULL | VBUS appears | CHARGING | 48 / 195 | CHARGE_ON | 74 | pass |
| 46 | 178 | ERR_STORAGE_FULL | long press | ERR_STORAGE_FULL | 49 / 198 | M3 SCR_MSG_STORAGE_FULL_3S | 75 | pass |
| 47 | 179 | ERR_STORAGE_FULL | battery reaches B5 | ERR_BATTERY_LOW | 50 / 202 | M3 | 76 | pass |
| 48 | 180 | ERR_STORAGE_FULL | battery reaches B2 | OFF | 51 / 205 | SHIP_MODE | 77 | pass |
| 49 | 181 | ERR_BATTERY_LOW | VBUS appears | CHARGING | 52 / 208 | CHARGE_ON | 78 | pass |
| 50 | 182 | ERR_BATTERY_LOW | long press | ERR_BATTERY_LOW | 53 / 211 | M3 SCR_MSG_BATTERY_LOW_3S | 79 | pass |
| 51 | 183 | ERR_BATTERY_LOW | battery reaches B2 | OFF | 54 / 215 | SAVE_SETTINGS_TIME SHIP_MODE | 80 | pass |
| 52 | 184 | ERR_STORAGE_FAULT | VBUS appears | CHARGING | 55 / 219 | CHARGE_ON | 81 | pass |
| 53 | 185 | ERR_STORAGE_FAULT | 60 s elapsed and storage init succeeds [guard STORAGE_INIT_OK] | STANDBY | 56 / 222 | RUN_RECOVERY | 82 | pass |
| 54 | 186 | ERR_STORAGE_FAULT | battery reaches B2 | OFF | 57 / 227 | SHIP_MODE | 83 | pass |
| 55 | 187 | ERR_MIC_FAULT | 5 s elapsed | STANDBY | 58 / 230 | (none) | 84 | pass |
| 56 | 188 | ERR_MIC_FAULT | VBUS appears | CHARGING | 59 / 232 | CHARGE_ON | 85 | pass |
| 57 | 189 | ERR_CHARGER | VBUS removed | STANDBY | 60 / 235 | (none) | 86 | pass |
| 58 | 190 | FACTORY_TEST | command FACTORY_EXIT | BOOT | 61 / 237 | REBOOT | 87 | pass |
| 59 | 191 | FACTORY_TEST | command SHIP_ENTER | SHIP | 62 / 240 | CLEAR_FACTORY_FLAG SHIP_MODE | 88 | pass |
| 60 | 192 | FACTORY_TEST | command SHIP_SAMPLE (sample rings only) | SHIP | 63 / 244 | SHIP_MODE | 90 | pass |
| 61 | 193 | FACTORY_TEST | VBUS removed, no ship command accepted | BOOT | 64 / 247 | REBOOT | 91 | pass |
