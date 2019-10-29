# Masivo public transport routes simulator

Installation
============

Install the unidecode, numpy, scipy, matplotlib, and wordcloud
Python libraries. For Windows, enter in the command line (Windows +
R, cmd, and Enter), and run the installation script:
        
    apt install -y python3 python3-tk python3-pip git nano
    python3 -m pip install --upgrade pip
    python3 -m pip install panda3d pyopencl numpy matplotlib scipy 


Running
=======

Running without C compilation:
    
    python3 main.py

Running with C compilation:
    
    gcc -shared -Wl,-soname, -o c_code/masivo_c.so -fPIC c_code/masivo_c.c; python3 main.py
