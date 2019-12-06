# Masivo public transport routes simulator

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
        gcc -shared -Wl,-soname, -o c_code/masivo_c.so -fPIC c_code/masivo_c.ccd


Running
=======

Running without C compilation:
    
    python3 main.py

