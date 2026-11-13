A=(__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/architecture.md")
M='REPLACED by section 17.11 (record button removed; one control, the joystick)'
b=open(A,'rb').read().decode('utf-8')
nl='\r\n' if '\r\n' in b else '\n'
L=b.split(nl)
def find(s):
    r=[i for i,l in enumerate(L) if l.startswith(s)]
    assert len(r)==1,(s,r); return r[0]
# in-place cell/sentence marks
def sub(start,old,new):
    i=find(start); assert L[i].count(old)==1,(start,old); L[i]=L[i].replace(old,new)
sub('| Cell | -13.0 to +6.0','record switch on the +Y edge at X -5','record switch on the +Y edge at X -5 ('+M+'. Do not use: the record switch)')
sub('- Main board: 27.2 x 12.6 mm, 0.4 mm','with a notch 1.0 x 3.0 mm at the record switch','with a notch 1.0 x 3.0 mm at the record switch ('+M+'. Do not use: the record switch notch)')
sub('| S16 | Flex ribbons','to reach the record switch and the joystick','to reach the record switch and the joystick ('+M+'; only the joystick remains)')
sub('| S17 | Openings in the band','the record pill has 0.29 mm of metal at its thinnest side, under the 0.40 mm rule','the record pill has 0.29 mm of metal at its thinnest side, under the 0.40 mm rule ('+M+'. Do not use: the record pill)')
# note lines under block diagram line and heading 16.5 (insert after, from the bottom up)
i=find('### 16.5 Thumb control'); L.insert(i+1,'> '+M+': the heading and the lines below about a record button are history (17.11 and 17.29).')
i=find('            |  6 inputs <-----'); L.insert(i+1,'            (note: '+M+'; a long press of its centre records)')
open(A,'wb').write(nl.join(L).encode('utf-8'))
