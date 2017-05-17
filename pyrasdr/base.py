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
        'sr':DEFAULT_SR,
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

    def set_center_freq(self, frequency):
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

    def get_center_freq(self):
        '''Return center frequency of tuner (in Hz).'''
        return self.state.fc
