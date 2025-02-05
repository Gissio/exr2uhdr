# exr2uhdr

`exr2uhdr` is a tool for converting EXR to [gainmap.js](https://github.com/MONOGRID/gainmap-js) Ultra HDR files. Unlike the [free online encoder](https://gainmap-creator.monogrid.com/), it does not require a browser.

## Installation

* Make sure Git, CMake, PYthon 3 and PIP are installed on your system.
* Install the latest [libultrahdr](https://github.com/google/libultrahdr):
  * Get the repository: 

        git clone --depth 1 --branch [tag] https://github.com/google/libultrahdr libultrahdr-[tag]

  * Configure:

        cd libultrahdr-[tag]
        mkdir build
        cd build
        cmake .. -DUHDR_WRITE_XMP=1
        cd ..

  * Build:

        cmake --build build

  * Install:

        sudo cmake --build build --target install
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

* Install the Python requirements (`pip install -r tools/requirements.txt`)
* Run: `python exr2uhdr.py -h`
