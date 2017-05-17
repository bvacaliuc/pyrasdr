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

from base import BaseRASDR

class RASDR4(BaseRASDR):

    def __init__(self, instance=0, channel=0, simulation=False):
        super(RASDR4, self).__init__(instance,channel,simulation)



