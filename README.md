# The pyrasdr Project
This is a cross-platform, pure-python interface to receivers supported by RASDR.

It is intended to provide a simplified, streamlined path to setup, control/tuning and
data collection of the RASDR receivers on all platforms and operating systems that
support USB, networking and Python.

## Devices Supported
 1. [RASDR2](http://rasdr.org) - TBD
 1. [RASDR4](http://rasdr4.blogspot.com) - In Progress

## Environment Setup
### MacOS
 1. Install [Anaconda Python](https://www.continuum.io/downloads)
  * choose either Python 3.x or 2.x version (it doesn't matter, we will be creating a virtual environment) and 32-bit/64-bit as appropriate for your system.
 1. Obtain the [pyrasdr](https://github.com/bvacaliuc/pyrasdr) project.
 1. Install [fftw](http://www.fftw.org/) using [homebrew](https://brew.sh/)
```
$ brew install fftw
==> Downloading https://homebrew.bintray.com/bottles/fftw-3.3.6-pl2.yosemite.bot
######################################################################## 100.0%
==> Pouring fftw-3.3.6-pl2.yosemite.bottle.tar.gz
🍺  /usr/local/Cellar/fftw/3.3.6-pl2: 46 files, 10.8MB
```
 1. Create and/or activate a virtual environment based on the needed configuration:
```
$ conda env create -f pyLMS7002M.yml
```
*NOTE: you only need to do this once on a computer, afterward, you can start an Anaconda Python prompt and simply activate the virtual environment:*
```
$ source activate pyLMS7002m
(pyLMS7002m) $
```

 1. next step...
