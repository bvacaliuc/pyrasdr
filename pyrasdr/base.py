#    This file is part of pyrasdr.
#
#    pyrasdr is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pyrasdr is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pyrasdr.  If not, see <http://www.gnu.org/licenses/>.

try:
    import numpy as np
except ImportError:
    raise NotImplementedError('numpy is required')

class RASDRException(Exception):
    """Base Exception class for the RASDR module"""

class PolarityException(RASDRException):
    """Buffer contained an IQ/QI inversion (data loss)"""

# http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class BaseRASDR(object):
    DEFAULT_GAIN = 34.0         # dB
    DEFAULT_FC = 400e6          # Hz
    DEFAULT_SR = 2e6            # Hz
    DEFAULT_BW = 1.5e6          # Hz
    DEFAULT_SAMPLES = 2048      # samples
    REFERENCE_FREQ = 30.72e6    # TCXO synthesizer

    gain_values = []
    valid_gains_db = []
    buffer = []
    num_bytes_read = 0
    
    state = AttributeDict({
        'open':False,
        'simulation':False,
        'gain':DEFAULT_GAIN,
        'fc':DEFAULT_FC,
        'sr':DEFAULT_SR,        # samples-per-second
        'sps':(1.0/DEFAULT_SR), # seconds-per-sample
        'bw':DEFAULT_BW,
        'samples':DEFAULT_SAMPLES,
        'tcxo':REFERENCE_FREQ,
        'tuner': { 'r':10, 'n':1 },
        })

    def __init__(self, instance=0, channel=0, simulation=False):
        self.open(instance, channel, simulation)

    def open(self, instance=0, channel=0, simulation=False):
        '''
        Initialize RASDR object.
        
        :param instance:    Identify which device.  Can be a numeric integer or a serial number string.
        :param channel:     Identify which channel.  RASDR2/3 has only channel '0'.  RASDR4 has '0' or '1'.
        :param simulation:  If True, will emulate a real device.
        '''
        self.state.open = True

    def close(self):
        '''Shutdown RASDR object and release resources.'''
        self.state.open = False

    def load(self, filename):
        '''
        Load an .ini file to the receiver.
        
        :param filename:    A string with a file path name.
        
        The function will load an ASCII file compatible with the Lime_Suite configuration
        file specification.  This file will be loaded to the reciever and provide a
        baseline configuration upon which to make further tuning adjustments according
        to the RASDR API.
        '''
        pass

    def _set_center_freq(self, frequency):
        '''
        Set center frequency of the channel.
        
        :param frequency: A numeric or string representing the tuning frequency in Hz
        
        Use get_center_freq() to see the precise frequency used.
        '''
        a = [ (r,n) for r in range(10,130,1) for n in range(1,32) ]
        f = [ (self.state.tcxo * r)/n for r,n in a ]
        e = np.square(np.subtract(np.array(f),frequency))
        (r,n) = a[e.argmin()]
        self.state.tuner['r'] = r
        self.state.tuner['n'] = n
        self.state.fc = (self.state.tcxo * r) / n

    def _get_center_freq(self):
        '''Return center frequency of tuner (in Hz).'''
        return self.state.fc

    def _set_sample_rate(self, rate):
        pass
    def _get_sample_rate(self):
        '''Return sample rate of the ADC (in Hz).'''
        return self.state.sr

    def _set_bandwidth(self, bw):
        pass
    def _get_bandwidth(self):
        '''Return bandwidth of the LPF prior to the ADC (in Hz).'''
        return self.state.bw

    def _set_gain(self, gain):
        pass
    def _get_gain(self):
        '''Return gain of the receiver (in dB).'''
        return self.state.gain

    def read(self, n=(DEFAULT_SAMPLES*2*2)):
        raise NotImplementedError('TODO')
    def read_samples(self, n=DEFAULT_SAMPLES):
        raise NotImplementedError('TODO')

    def _packed_bytes_to_iq(self, bytes, iq_polarity=False, otm_polarity=False):
        '''
        Unpack array of bytes to numpy array of complex numbers.
        
        :param bytes: A buffer-like object containing packed IQ data with control bits
        :option iq_polarity: A boolean indicating the order of IQ (False) or QI (True)
        :option otm_polarity: A boolean indicating the polarity of the PPS input
        :returns: A tuple representing a numpy array of complex values, the sample
            offset of the OTM (or -1 if not found), the time offset (in seconds) from
            the *END* of the buffer that the OTM marker occured.
        
        The function will strip control bits from a raw data stream obtained from a
        RASDR2/3 receiver and return a complex numpy array with the samples arranged
        in the correct order.  The function will also analyze the control bits in the
        stream for the on-time-marker (OTM) or pulse-per-second input that was sampled
        along with the stream.
        '''
        b = np.frombuffer(bytes,dtype='<i2')
        iq = np.empty(len(b)//2, 'complex')
        if iq_polarity:
            ri = 1                  # QIQIQI...
            qi = 0
        else:
            ri = 0                  # IQIQIQ...
            qi = 1
        re = b[ri::2] & 0x1000      # in-phase samples
        im = b[qi::2] & 0x1000      # quadrature samples
        otm = b & 0x8000            # on-time-marker
        iq.real = b[ri::2] & 0xFFF  # strip control bits
        iq.imag = b[qi::2] & 0xFFF  # "
        if re.max()>0 or im.min()<1:
            raise PolarityException('Expected {}...'.format('QIQI' if iq_polarity else 'IQIQ'))
        iq /= (4095/2)
        iq -= (1 + 1j)
        otm_index = -1              # on-time-marker not found
        if otm_polarity and otm.min()<1:
            otm_index = int(otm.argmin()/2)
        elif not otm_polarity and otm.max()>0:
            otm_index = int(otm.argmax()/2)
        return iq, otm_index, (len(iq)-otm_index)*self.state.sps

    # Property-based interface to the object
    center_freq = property(_get_center_freq, _set_center_freq,
                    doc='set or get the center frequency of tuner (in Hz)')
    sample_rate = property(_get_sample_rate, _set_sample_rate,
                    doc='set or get the sample rate of the ADC (in Hz)')
    gain = property(_get_gain, _set_gain,
                    doc='set or get the gain of the receiver (in dB)')
    bandwidth = property(_get_bandwidth, _set_bandwidth,
                    doc='set or get the bandwidth of the LPF prior to the ADC (in Hz)')
