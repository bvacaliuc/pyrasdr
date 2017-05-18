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

class ParameterError(RASDRException):
    """A parameter exceeds defined limits"""

# http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class BaseRASDR(object):
    DEFAULT_GAIN = [ 6.0, 25.17, 0.0 ]
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
        'instance':None,
        'channel':None,
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

    def __str__(self):
        '''Describe key parameters of the receiver.'''
        msg = 'RASDR-base.{}.{}{} {}\n'.format(
            self.state.instance,
            self.state.channel,
            '-sim' if self.state.simulation else '',
            'open' if self.state.open else 'closed')
        msg += '  Fc={:.3e} Hz, BW={:.1e} Hz, Fs={:.1e} s/sec\n'.format(
            self.state.fc, self.state.bw, self.state.sr)
        msg += '  Gains={} ({:.2f} dB total)\n'.format(
            self.state.gain, self.gain)
        msg += '  Ref={:.3e} Hz, Tuner={}\n'.format(
            self.state.tcxo, self.state.tuner)
        return msg

    def open(self, instance=0, channel=0, simulation=False):
        '''
        Initialize RASDR object.
        
        :param instance:    Identify which device.  Can be a numeric integer or a serial number string.
        :param channel:     Identify which channel.  RASDR2/3 has only channel '0'.  RASDR4 has '0' or '1'.
        :param simulation:  If True, will emulate a real device.
        '''
        self.state.instance = instance
        self.state.channel = 0
        self.state.simulation = simulation
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
        
        Use _get_center_freq() to see the precise frequency used.
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
        '''
        Set sample rate of the channel.

        :param rate: A numeric or string representing the sample rate in Hz

        Use _get_sample_rate() to see the actual sample rate used.

        May raise a ParameterError exception if device limits are exceeded.
        '''
        r = float(rate)
        if r < 1e6 or r > 32e6:
            raise ParameterError('{:.0f} exceeds limit of [{:.0e},{:.0e}]'.format(r,1e6,32e6))
        self.state.sr = r
        self.state.sps = (1.0/r)

    def _get_sample_rate(self):
        '''Return sample rate of the ADC (in Hz).'''
        return self.state.sr

    def _set_bandwidth(self, bandwidth):
        '''
        Set bandwidth of the channel.

        :param bandwidth: A numeric or string representing the LPF bandwidth in Hz

        Use _get_bandwidth() to see the actual bandwidth programmed to the receiver.

        May raise a ParameterError exception if device limits are exceeded.
        '''
        bw = float(bandwidth)
        if bw < 0.75e6 or r > 28e6:
            raise ParameterError('{:.0f} exceeds limit of [{:.0e},{:.0e}]'.format(bw,0.75e6,28e6))
        self.state.bw = bw

    def _get_bandwidth(self):
        '''Return bandwidth of the LPF prior to the ADC (in Hz).'''
        return self.state.bw

    def _set_gain(self, gain):
        '''
        Set the total gain of the channel.

        :param gain: A numeric scalar, array or string requesting the receiver gain in dB

        Use _get_gain() to see the actual gain programmed to the receiver.
        TODO: consider allowing gain to be an array of gain values for the stages.

        The gain of the system is the sum of the various gain stages available in the
        receiver.  This interface provides a simple scalar setting to an otherwise
        complex operation.  According to recommended tuning, gain is to be applied
        as far upstream in the signal chain as possible.  Therefore, this function
        will assign and program gain as follows:

          1) the LNA
          2) the VGA1 (after the mixer)
          3) the VGA2 (after the LPF)

        May raise a ParameterError exception if device limits are exceeded.
        '''
        g = float(gain)
        if bw < 0.0 or r > 61.17:
            raise ParameterError('{:.0f} exceeds limit of [{:.0e},{:.0e}]'.format(g,0.0,61.17))
        ga = [ 0.0, 0.0, 0.0 ]
        # compute LNA gain (0.0=bypass, 3.0=midgain, 6.0=maxgain)
        if g>3.0:
            ga[0] = 6.0
        else:
            ga[0] = 3.0 if g>0.0 else 0.0
        g -= ga[0]
        # compute VGA1 gain
        if g>25.17:
            ga[1] = 25.17
        else:
            ga[1] = g   # TODO: there is a table of fixed values
        g -= ga[1]
        # compute VGA2 gain
        if g>30.0:
            ga[2] = 30.0
        else:
            ga[2] = float(int(g/3.0)*3)
        self.state.gain = ga

    def _get_gain(self):
        '''Return gain of the receiver (in dB).'''
        gain = 0.0
        for g in self.state.gain:
            gain += g
        return gain

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
        return iq, otm_index, (len(iq)-otm_index-1)*self.state.sps

    # Property-based interface to the object
    center_freq = property(_get_center_freq, _set_center_freq,
                    doc='set or get the center frequency of tuner (in Hz)')
    sample_rate = property(_get_sample_rate, _set_sample_rate,
                    doc='set or get the sample rate of the ADC (in Hz)')
    gain = property(_get_gain, _set_gain,
                    doc='set or get the gain of the receiver (in dB)')
    bandwidth = property(_get_bandwidth, _set_bandwidth,
                    doc='set or get the bandwidth of the LPF prior to the ADC (in Hz)')
