# exr2uhdr

`exr2uhdr` is a tool for converting EXR files to [gainmap.js](https://github.com/MONOGRID/gainmap-js) Ultra HDR files.

Unlike the [free online encoder](https://gainmap-creator.monogrid.com/), this tool operates from the command line without requiring a browser..

## Installation

These instructions are for UNIX systems.

1. Make sure Git, CMake, Python 3 and PIP are installed on your system.
2. Install [libultrahdr](https://github.com/google/libultrahdr):

  * Clone the repository: 

        git clone --depth 1 --branch [tag] https://github.com/google/libultrahdr libultrahdr-[tag]

  * Configure the project:

        cd libultrahdr-[tag]
        mkdir build
        cd build
        cmake .. -DUHDR_WRITE_XMP=1
        cd ..

  * Build the project:

        cmake --build build

  * Install the library:

        sudo cmake --build build --target install
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

3. Install Python dependencies:
  
      pip install -r tools/requirements.txt

4. Run the tool:

      python exr2uhdr.py -h
