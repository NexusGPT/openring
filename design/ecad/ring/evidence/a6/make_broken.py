import csv
R = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/")
rows = list(csv.DictReader(open(R + 'netlist.csv')))
def write(name, fn):
    rr = [dict(r) for r in rows]
    n = fn(rr)
    assert n == 1, (name, n)
    with open(R + 'evidence/a6/broken/' + name, 'w', newline='') as f:
        w = csv.DictWriter(f, ['net', 'reference', 'pin_number', 'pin_name', 'pin_type']); w.writeheader(); w.writerows(rr)
def setnet(ref, pin, net):
    def f(rr):
        n = 0
        for r in rr:
            if r['reference'] == ref and r['pin_number'] == pin:
                r['net'] = net; n += 1
        return n
    return f
write('b1_u10_pin12_net_removed.csv', setnet('U10', '12', ''))          # the required case: one net removed from one pin
write('b2_u3_clk_direct_to_chip_net.csv', setnet('U3', '3', 'SD_SCK'))  # F07: card joined to the 1.8 V net
write('b3_jband_a_motor_plus_on_gnd.csv', setnet('J_BAND_A', '7', 'GND'))  # tail pad on the wrong net
write('b4_cp1_vbus_pad_on_vbusout.csv', setnet('CP1', '1', 'VBUSOUT'))  # a pad on a source net
print('written')
