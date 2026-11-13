F=(__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/case/pcb/board-notes.md")
t=open(F,encoding="utf-8").read()
reps=[('(the case\'s USB input is 5 V: `design/case/case-architecture.md` section 4 and SL row C2.3, "5 V")','(the case\'s USB input is 5 V: `design/case/case-architecture.md` line 96, "VBUS 5 V", and SL row C2.3)'),
("so use a meter of 10 Mohm or more)","so read it with a meter of 10 Mohm input or more; my reading)"),
('(search of case_esp32s3_mini1.pdf and case_esp32s3_ds.pdf for "115200", "baud", "rst:0x", "invalid header": no hit, W/txt/ and W/search_boot.log)','(search of case_esp32s3_mini1.pdf and case_esp32s3_ds.pdf for "115200", "baud", "rst:0x", "invalid header": the only hits are the feature lines "Programmable baud rate" and "Automatic baud rate detection", which name no value; case-proc-work/search_boot.log)')]
for a,b in reps:
    assert a in t, a
    t=t.replace(a,b)
open(F,"w",encoding="utf-8").write(t)
print("ok")
