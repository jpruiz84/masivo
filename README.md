# Masivo public transport routes simulator

Masivo is a new parallel simulation model based in OpenCL using a multi-core high performance platform for massive public transportation systems. Masivo works with predefined public transport system conditions, which include the stops’ total number, the stops’ capacity, and the Origin-Destination matrix (OD). This OD matrix and routes’ information are updated to this model via CSV files. Masivo gets the simulation results for total alighted passengers and average commute time. Similarly, it shows the performance indicators.

Installation
============

1. Install Intel OpenCL SDK from https://software.intel.com/en-us/opencl-sdk/choose-download
or download directly from:
	
        wget http://registrationcenter-download.intel.com/akdlm/irc_nas/vcp/15951/intel_sdk_for_opencl_applications_2019.5.345.tar.gz
        tar xvf intel_sdk_for_opencl_applications_2019.5.345.tar.gz 
        cd intel_sdk_for_opencl_applications_2019.5.345/
        sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/g' silent.cfg 
        ./install.sh -s silent.cfg


2. Install the unidecode, numpy, scipy, matplotlib, and wordcloud
Python libraries. For Windows, enter in the command line (Windows +
R, cmd, and Enter), and run the installation script:
        
        apt update
        apt install -y python3 python3-tk python3-pip git nano clinfo htop
        export LC_ALL=C
        python3 -m pip install --upgrade pip
        python3 -m pip install panda3d pyopencl numpy matplotlib scipy psutil 

3. Clone the repository
        
        cd ~/
        git clone https://github.com/jpruiz84/masivo

4. Compile the C source code components: 
        
        cd masivo
        gcc -shared -Wl,-soname, -o c_code/masivo_c.so -fPIC c_code/masivo_c.c


Running
=======

Running without C compilation:
    
    python3 main.py

Paper
=====

The paper that describes how Masivo works is available in: https://www.mdpi.com/2079-9292/8/12/1501


How to cite this work
=====================

If you use Masivo in a book, paper, website, technical report, etc., please include a reference to Masivo.

To cite Masivo, use the following [reference](https://www.mdpi.com/2079-9292/8/12/1501):

> Ruiz-Rosero, J.; Ramirez-Gonzalez, G.; Khanna, R. Masivo: Parallel Simulation Model Based on OpenCL for Massive Public Transportation Systems’ Routes. Electronics 2019, 8, 1501. https://doi.org/10.3390/electronics8121501

The bibtex entry for this is:

	@Article{electronics8121501,
	AUTHOR = {Ruiz-Rosero, Juan and Ramirez-Gonzalez, Gustavo and Khanna, Rahul},
	TITLE = {Masivo: Parallel Simulation Model Based on OpenCL for Massive Public Transportation Systems’ Routes},
	JOURNAL = {Electronics},
	VOLUME = {8},
	YEAR = {2019},
	NUMBER = {12},
	ARTICLE-NUMBER = {1501},
	URL = {https://www.mdpi.com/2079-9292/8/12/1501},
	ISSN = {2079-9292},
	ABSTRACT = {There is a large number of tools for the simulation of traffic and routes in public transport systems. These use different simulation models (macroscopic, microscopic, and mesoscopic). Unfortunately, these simulation tools are limited when simulating a complete public transport system, which includes all its buses and routes (up to 270 for the London Underground). The processing times for these type of simulations increase in an unmanageable way since all the relevant variables that are required to simulate consistently and reliably the system behavior must be included. In this paper, we present a new simulation model for public transport routes&rsquo; simulation called Masivo. It runs the public transport stops&rsquo; operations in OpenCL work items concurrently, using a multi-core high performance platform. The performance results of Masivo show a speed-up factor of 10.2 compared with the simulator model running with one compute unit and a speed-up factor of 278 times faster than the validation simulator. The real-time factor achieved was 3050 times faster than the 10 h simulated duration, for a public transport system of 300 stops, 2400 buses, and 456,997 passengers.},
	DOI = {10.3390/electronics8121501}
	}


## Authors

* **Juan Ruiz-Rosero** - *Initial work and documentation*

## License

This project is licensed under the MIT License -

