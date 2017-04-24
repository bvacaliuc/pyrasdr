# The pyrasdr Project
This is a cross-platform, pure-python interface to receivers supported by the [RASDR](https://github.com/myriadrf/RASDR) project.

It is intended to provide a simplified, streamlined path to setup, control/tuning and
data collection of the RASDR receivers on all platforms and operating systems that
support USB, networking and Python.

The API is modeled after the very clean and pythonic part of [pyrtlsdr](https://github.com/roger-/pyrtlsdr).
However it will also contain the aspects of [pyLMS7002M](https://github.com/myriadrf/pyLMS7002M) that provide
a pythonic interface to the registers of the core devices present on the RASDR boards.  See this [example](https://github.com/myriadrf/pyLMS7002M/blob/master/examples/VNA/measureVNA.py)

## Devices Supported
 1. [RASDR2](http://rasdr.org) - TBD
 1. [RASDR4](http://rasdr4.blogspot.com) - In Progress

# Usage

pyrasdr is currently used by cloning the repository and adding its base directory to your ```PYTHONPATH```.
At this time it is under construction.

## Examples

Simple way to read and print some samples:

```python
from pyrasdr import RASDR4

sdr = RASDR4(channel=0)

# configure device
sdr.sample_rate = 2.0e6    # Hz
sdr.bandwidth   = 1.5e6    # Hz
sdr.center_freq = 408.1e6  # Hz
sdr.gain        = 56.0     # dB

print(sdr.read_samples(2048))
```

Plotting the PSD with matplotlib:

```python
from pylab import psd, xlabel, ylabel, show
from pyrasdr import RASDR4

sdr = RASDR4(channel=0)

# configure device
sdr.sample_rate = 2.0e6    # Hz
sdr.bandwidth   = 1.5e6    # Hz
sdr.center_freq = 408.1e6  # Hz
sdr.gain        = 56.0     # dB

samples = sdr.read_samples(256*1024)

# use matplotlib to estimate and plot the PSD
psd(samples, NFFT=2048, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
xlabel('Frequency (MHz)')
ylabel('Relative power (dB)')

show()
```

An actual plot using these values is ```TBD```, as well as simple test examples.


# Environment Setup
## MacOS
 1. Install [Anaconda Python](https://www.continuum.io/downloads)<br>
Choose either Python 3.x or 2.x version (it doesn't matter, we will be creating a virtual environment) and 32-bit/64-bit as appropriate for your system.
 1. Obtain the [pyrasdr](https://github.com/bvacaliuc/pyrasdr) project.
 1. Install [fftw](http://www.fftw.org/) using [homebrew](https://brew.sh/)<br>
```
$ brew install fftw
==> Downloading https://homebrew.bintray.com/bottles/fftw-3.3.6-pl2.yosemite.bot
######################################################################## 100.0%
==> Pouring fftw-3.3.6-pl2.yosemite.bottle.tar.gz
🍺  /usr/local/Cellar/fftw/3.3.6-pl2: 46 files, 10.8MB
```
 4. Create and/or activate a virtual environment based on the needed configuration:<br>
```
$ conda env create -f pyLMS7002M.yml
```
*NOTE: you only need to do this once on a computer, afterward, you can start an Anaconda Python prompt and simply activate the virtual environment:*
```
$ source activate pyLMS7002m
(pyLMS7002m) $
```
 5. next step...
