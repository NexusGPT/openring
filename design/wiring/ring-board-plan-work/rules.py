# Placement rules of ring-board-plan.md, round 2. Model coordinates (mm), KiCad = model + (100, 100).
import math
OFF_BOARD={'RT1','BT1','SW1','SW2','SW3','SW4','SW5','M1','CP1','CP2','CP3','CP4','DISP1'}
REMOVED={'TP7','TP10','TP20'}                       # plan a.2
ADDED=[]                                            # C89 and LT1 are already in parts.csv
FP_OVERRIDE={'C88':'OpenRing:Chip_0603','C89':'OpenRing:Chip_0201','LT1':'OpenRing:Chip_0201',
             'C35':'OpenRing:Chip_0402','C36':'OpenRing:Chip_0402'}   # lead's rulings 2026-11-13
X0,X1E,Y0,Y1E,RC=-13.6,13.6,-6.3,6.3,0.8            # outline, corner radius (PLACE PCB1)
EDGE_EXC={'ANT1':0.10,'U5':0.20,'U6':0.20}          # courtyard may pass the outline by this much (body flush with the edge by design); pads stay 0.10 inside
KEEPOUTS=[dict(name='antenna',r=(-13.6,3.10,-9.20,6.30),allow={'ANT1','LT1'}),
          dict(name='antenna',r=(-9.20,3.30,-8.75,6.30),allow={'ANT1','LT1'}),   # notch round U3's body corner (no U3 copper there)
          dict(name='tail A',r=(-3.50,-5.60,-1.00,-3.40),allow={'J_BAND_A'}),
          dict(name='tail B',r=(-3.50,3.40,-1.00,5.60),allow={'J_BAND_B'})]
RESERVED=[  # copper of scripted tracks plus their gap: no auto-placed courtyard there
 (-0.26,-0.70,0.26,3.56),(-6.96,3.04,0.26,3.56),(-6.96,3.04,-6.44,6.16),     # RF line d.1 (X 0.00 leg, Y 3.30 leg, rise X -7.40)
 (4.15,1.36,4.83,4.40),(3.90,1.36,4.83,1.75),(1.60,4.00,4.83,4.70),(-3.20,5.70,1.70,6.20),          # USB pair d.2
 (8.80,1.40,11.20,1.75),(10.75,1.40,11.20,3.30),(7.70,1.30,8.25,3.30)]        # SW1, SW2 (U2 table)
AVOID={'C31':[(-14.8,-8.3,-6.8,-1.3)],'C32':[(6.8,-8.3,14.8,-1.3)]}         # Class 2 parts 2.0 mm or more from the microphone bodies
FIXED={ # ref: (x, y, rotation, zone)
 'U1':(4.0,0.0,0,'U1'),'U2':(8.5,0.0,270,'Z5'),'U3':(-5.0,0.0,0,'U3'),'U4':(4.0,-3.9,0,'Z12'),'L10':(6.5,-3.9,90,'Z12'),
 'X1':(3.0,3.0,0,'Z3'),'X2':(6.0,3.35,90,'Z3'),'U5':(-10.8,-4.8,90,'Z7'),'U6':(10.8,-4.8,270,'Z11'),
 'J1':(-11.65,-0.15,270,'Z13'),'ANT1':(-10.80,5.25,180,'antenna'),'U11':(0.0,4.2,0,'Z9'),'C83':(0.0,5.45,0,'Z9'),'C84':(1.27,5.0,90,'Z9'),
 'U9':(3.12,5.2,90,'Z9'),'J_BAND_A':(-2.25,-4.325,0,'Z10'),'J_BAND_B':(-2.25,4.325,0,'Z10'),
 'L72':(8.87,3.75,0,'Z6'),'L71':(12.02,3.75,0,'Z6'),'C74':(9.05,2.14,0,'Z5'),
 'L2':(1.70,-0.39,0,'Z2'),'C3':(1.10,-1.31,90,'Z2'),'L3':(0.48,-0.39,0,'Z2'),'C12':(-0.12,-1.31,90,'Z2'),
 'C13':(-8.30,4.98,90,'Z8'),'L4':(-7.75,5.90,0,'Z8'),'C89':(-7.15,4.98,90,'Z8'),'LT1':(-12.45,3.25,0,'antenna'),
 'C35':(-8.25,-5.35,90,'Z7'),'C36':(8.25,-3.40,90,'Z11'),'R32':(8.25,-4.90,90,'Z11'),
 # U1 supply parts by hand (Nordic's arrangement: at the chip's row A side and its VDD E10 side)
 'C4':(2.83,-2.06,0,'Z1'),'C5':(1.05,-2.50,90,'Z1'),'C6':(4.00,-2.06,90,'Z1'),'FB1':(4.65,-2.06,90,'Z1'),'C7':(5.60,-1.75,0,'Z1'),
 'L1':(1.00,-4.32,90,'Z1'),'C23':(2.37,-3.40,90,'Z12'),'C22':(2.37,-5.10,90,'Z12'),'C14':(6.01,-0.84,90,'Z4'),'C1':(6.01,0.35,90,'Z4'),'C2':(6.67,0.66,90,'Z4'),'C10':(5.42,1.71,0,'Z3'),
 # U2 parts by hand
 'R72':(6.67,-1.70,90,'Z4'),'R71':(6.67,-0.52,90,'Z4'),'C85':(8.52,-2.13,0,'Z5'),'C71':(10.40,-2.13,0,'Z5'),
 'C86':(10.30,0.00,90,'Z5'),'C79':(12.45,5.60,0,'Z6'),'C87':(11.15,0.20,90,'Z5'),
}
BSIDE={t for t in ('TP1','TP2','TP3','TP4','TP5','TP6','TP8','TP9','TP11','TP12','TP13','TP14','TP15','TP16','TP17','TP18','TP19','TP21','TP22')}  # test pads on L4 (screen face): flat copper, no height
BODY_PAIRS={('U5','U3'):0.20,('U3','U5'):0.20}   # mechanically fixed pair: bodies 0.20 apart (mic-path.md C13); courtyard margins overlap
ANCHOR={ # ref: (x, y, zone, priority) - the pin the part serves (plan f.1)
 'L1':(2.0,-2.2,'Z1',0),'C4':(3.35,-1.9,'Z1',1),'C5':(3.0,-1.9,'Z1',2),'C6':(4.0,-1.9,'Z1',1),'FB1':(4.3,-1.9,'Z1',2),'C7':(4.65,-1.9,'Z1',1),'C14':(4.95,-1.9,'Z1',2),
 'C1':(5.95,-0.2,'Z4',1),'C2':(5.95,0.2,'Z4',1),'R57':(6.6,0.6,'Z4',3),'R58':(6.6,0.3,'Z4',3),'R71':(6.8,-0.9,'Z4',3),'R72':(6.8,-1.2,'Z4',3),
 'C10':(5.2,1.8,'Z3',1),'R1':(5.6,1.8,'Z3',1),'C11':(5.9,1.6,'Z3',0),'R2':(3.3,1.6,'Z3',0),
 'C71':(8.94,-2.1,'Z5',1),'C72':(9.3,-2.1,'Z5',0),'C85':(8.06,-2.1,'Z5',1),'C73':(8.5,-2.1,'Z5',0),'C86':(10.2,0.0,'Z5',1),'C87':(10.2,0.42,'Z5',1),
 'C75':(10.4,-0.6,'Z5',0),'C76':(10.4,0.9,'Z5',0),'C77':(10.6,-1.0,'Z5',0),'C78':(9.88,5.3,'Z6',0),'C79':(12.6,5.3,'Z6',1),'C80':(9.3,5.3,'Z6',0),'C88':(11.0,5.4,'Z6',0),
 'R31':(-6.6,-4.4,'Z7',2),'C31':(-6.3,-5.5,'Z7',2),'C32':(6.5,-1.9,'Z11',2),
 'U10':(-5.25,-4.6,'Z15',-1),'C81':(0.75,-1.75,'Z15',1),'C82':(1.8,-3.5,'Z15',1),'R60':(-0.4,-2.0,'Z15',3),'R63':(-0.4,-2.4,'Z15',3),'R64':(-0.4,-2.8,'Z15',3),'R65':(-0.4,-3.2,'Z15',3),
 'C60':(-0.45,-1.6,'Z15',1),'C61':(-0.45,-3.6,'Z15',1),
 'C21':(2.4,-4.6,'Z12',0),'C24':(3.0,-5.7,'Z12',0),'C26':(5.0,-5.8,'Z12',0),'C27':(7.4,-5.9,'Z12',0),'R66':(2.5,-3.0,'Z12',3),
 'C25':(-9.55,1.2,'Z13',0),'C28':(-9.55,-1.0,'Z13',2),'C29':(-9.55,0.0,'Z13',2),
 'R61':(1.0,3.8,'Z9',3),'R62':(1.0,4.3,'Z9',3),
 **{t:(-5.0,0.0,'Z14 (L4)',5) for t in ('TP1','TP2','TP3','TP4','TP5','TP6','TP8','TP9')},
 **{t:(-5.0,0.0,'Z14 (L4)',6) for t in ('TP11','TP12','TP13','TP14','TP15','TP16','TP17','TP18','TP19')},
 **{t:(-5.0,0.0,'Z14 (L4)',7) for t in ('TP21','TP22')},
}
def overlap(a,b):
    return a[0]<b[2] and b[0]<a[2] and a[1]<b[3] and b[1]<a[3]
def _in_outline(x,y,tol):
    if not (X0-tol<=x<=X1E+tol and Y0-tol<=y<=Y1E+tol): return False
    for cx,cy in ((X0+RC,Y0+RC),(X1E-RC,Y0+RC),(X0+RC,Y1E-RC),(X1E-RC,Y1E-RC)):
        if (abs(x-cx)>0 and (x<cx if cx<0 else x>cx)) and ((y<cy if cy<0 else y>cy)):
            if math.dist((x,y),(cx,cy))>RC+tol+1e-6: return False   # 1e-6: equality passes, as KiCad's DRC
    return True
def inside(cy,ref):
    tol=EDGE_EXC.get(ref,0.0)
    return all(_in_outline(x,y,tol) for x in (cy[0],cy[2]) for y in (cy[1],cy[3]))
J1_HOUSING=(6.10,3.35)   # Hirose catalogue p3: A 6.1 along the row, (3.35) closed depth (read from the picture)
def override_cy(ref,cy,x,y,rot):
    if ref=='J1':   # contact row along Y at rotation 270
        return (x-J1_HOUSING[1]/2,y-J1_HOUSING[0]/2,x+J1_HOUSING[1]/2,y+J1_HOUSING[0]/2)
    if ref in ('J_BAND_A','J_BAND_B'):   # band-interface.md section 2: keep-out X -3.50 to -1.00, |Y| 3.40 to 5.60
        return (-3.50,-5.60,-1.00,-3.40) if ref=='J_BAND_A' else (-3.50,3.40,-1.00,5.60)
    if ref in ('U5','U6'):  # courtyard 0.10 round the 4.0 x 3.0 body (library: 0.145)
        return (x-2.1,y-1.6,x+2.1,y+1.6)
    return cy
