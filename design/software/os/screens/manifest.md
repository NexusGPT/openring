| picture | scene | size | frame hash (FNV-1a over the 240 x 120 RGB read-back) | lit px | sha256 of PNG (16 hex) | sha256 of 4x PNG |
|---|---|---|---|---|---|---|
| status | STANDBY, screen off, short press of the centre; clock set to 2026-11-12 10:42 UTC (rtime_set) | 240x120 | f709d68c91f6ed7d | 862 | 66f277b72280141b | 2771558dafd9684a |
| menu | SCR_MENU, first item highlighted (Right from the status screen) | 240x120 | cd392cc16e7f0d94 | 6050 | 1478b47fcdc2beb3 | 08408355180079a7 |
| settings | SCR_SETTINGS, Screen brightness highlighted | 240x120 | 0292214c06bb4840 | 5870 | d9c695e880d6a836 | 91c926fb287309aa |
| recording-idle | RECORDING, 3 s after the last input, 00:12:47 elapsed (SCR_REC_DIM) | 240x120 | d804611545d1514b | 240 | 67321eb2da3d77ac | cbf6fed60aa69173 |
| recording | RECORDING, a joystick direction 0 s ago, 00:12:47 elapsed (SCR_RECORDING) | 240x120 | a86f898c3db76a4a | 2061 | f24f817eaa0a37c5 | 3a13c91c804d87e1 |
| recording-highlight | RECORDING, one highlight marked (short press), SCR_RECORDING with the count | 240x120 | fb716ae72ab8c103 | 2324 | 7d03105b127d243f | fef80932af91c6e4 |
| notifications-empty | SCR_NOTIFS with an empty inbox | 240x120 | 4b9432db4ae47965 | 567 | c4a4dd65d04fc8d6 | 091c126c3aadd56e |
| notifications | SCR_NOTIFS, two notifications in the inbox, newest first, the first highlighted | 240x120 | 65292800c4b1c55c | 5297 | 66e78a2eb8dbcd7c | cc63c1cfb9dcdec7 |
| notification | SCR_NOTIF, 'Grace Lin' with both actions (dismiss left, positive right) | 240x120 | f134876382d8dcc6 | 1488 | a80c48a19c3234e8 | e85a29761a660727 |
| modes | SCR_MODES, Media highlighted (first time) | 240x120 | 88fc0f34e51e3d89 | 5573 | cb4eb2984a72983d | b46f289aa14e2aa6 |
| control-media | SCR_CONTROL Media: track 'Night Drive', playing (decoder of ring_iphone) | 240x120 | d964f558e5079182 | 1647 | bd9b0e1741ded2dc | e3d147f4cc56a4b1 |
| control-presenter | SCR_CONTROL Presenter | 240x120 | a6d21eed16e385e8 | 1512 | 0bb663b1bcbdb3a5 | f8d7f2bb63c6e241 |
| control-pointer | SCR_CONTROL Pointer | 240x120 | d7e3e3d68b251b6d | 1258 | 69e161ae20d294f5 | caf41057ef9287f0 |
| control-agent | SCR_CONTROL Agent, words Accept and Decline only | 240x120 | 7d13b3f7836cd857 | 1668 | 6fdcd3344d468f4f | 288edef009255dfe |
| devices | SCR_DEVICES, three devices Phone, Laptop (active, light pill), Tablet (neutral names set with rscr_set_device_name); cursor on the first | 240x120 | 624965dd60ef8943 | 2606 | a5cb32842a069bd4 | 36dc413ec5118921 |
| device | SCR_DEVICE, Laptop, 'Use' highlighted | 240x120 | a25f903369ade9b4 | 6243 | fb672565d0f03d76 | 388d69ac34b34b4c |
| confirm | SCR_CONFIRM, 'Remove Laptop?' | 240x120 | fe1f109ba8c82731 | 1416 | fb048d46374388d6 | a322c5041fc36e63 |
| pairing | SCR_PAIR, passkey 482 913 from the devices callback, about 50 s left | 240x120 | 57af93807ed09253 | 1198 | 5cabaf9572688dab | 42ec9ee30a871a2a |
| charging | CHARGING, 64 %, 38 min to full (VBUS in) | 240x120 | 030514ed798d13c1 | 1259 | 33c32b39fd0dda9e | cea9394da769a5a1 |
| message | SCR_MESSAGE 'In case' (long press refused in CHARGING) | 240x120 | d778a8a69797908d | 247 | e8500c601d1504eb | 49ef40a0d3f4b6f1 |
| message-battery-low | SCR_MESSAGE 'Battery low' (long press at B5) | 240x120 | cca8ad6585561432 | 448 | 82a5aca649f43356 | 97b5a5371a7bb835 |
