import pytest
import sys

def test():
    with pytest.warns(None) as record:
        # test import components
        from plugins import LMS7002, ADF4002, Si5351, Proxy
        # test import receivers
        from pyrasdr import RASDR4
        # test instantiation, description and configuration 
        sdr = RASDR4(simulation=True)
        sys.stdout.write(str(sdr)+'\n')
        sdr.sample_rate = 10.0e6   # Hz
        sdr.bandwidth   = 8.0e6    # Hz
        sdr.center_freq = 1420.4e6 # Hz
        sdr.gain        = 56.0     # dB
        sys.stdout.write(str(sdr)+'\n')
        # test unpacking subroutine
        with open('test.dat','r') as f:
            buf = f.read()
            iq = sdr._packed_bytes_to_iq(buf)
            sys.stdout.write(str(iq)+'\n')
    return True

if __name__ == '__main__':
    assert test()
