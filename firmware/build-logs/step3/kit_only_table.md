| Format | Rests on | What a real iPhone must confirm |
|---|---|---|
| ANCS Notification Source: byte sizes and little-endian order of the fields and of the u32 id | the kit's parser (`kit/ancs_client.c:60-110`); Apple's text lists the fields, the figure with the sizes is not saved | the 8-byte layout and the byte order |
| ANCS Get Notification Attributes request and answer: u16 little-endian lengths, u32 little-endian id | the kit's encoder (`kit/ancs_client.c:409-453`); Apple's text names a "16-bit length parameter" | the byte order of the lengths and the id in the request and in the answer |
| AMS Remote Command ids (play 0, pause 1, next 3, previous 4, volume up 5, volume down 6) | the kit's enum (`kit/ams_client.h:82-98`, values implicit 0..6); the Apple appendix is not saved | each id does what its name says |
| AMS entity and attribute ids (player 0, track 2; PlaybackInfo 1; artist 0, title 2) | the kit's enums (`kit/ams_client.h:100-142`) | the ids |
| AMS Entity Update flag bit 0 = truncated | the kit's header (`kit/ams_client.h:58-59`); Apple's text only says a flag can say "truncated" | the bit (the ring ignores the flag) |
| AMS PlaybackInfo `<state>,<rate>,<elapsed>`, state 0 paused, 1 playing | the kit's sample README (`kit/ams_sample_readme_excerpt.txt`); no Apple page saved | the format and the state numbers (2 and 3 are ignored) |
| CTS Current Time, 10 bytes | the kit (`kit/cts_client.c:19-25,103-135`); Bluetooth SIG, not saved | the layout |
| CTS day of week (1 Monday to 7 Sunday) | nothing (stand-in only; the ring ignores the field) | not needed by the ring |
| Local Time Information, 2 bytes: zone and daylight offset | nothing saved: the author's reading of the Bluetooth SIG specification | the layout, the units (15 minutes), the daylight codes (0, 2, 4, 8) and the "unknown" values; that the iPhone serves the characteristic at all |
| Behaviour: the replay of held notifications flagged pre-existing when the ring subscribes; Removed after a dismiss; time notifications on a change | the stand-in's choices (Apple's appendix has the flag; nothing says the replay) | all three |
