# Lidar Tracker (Python)

A Python port of the `lidarTracker` application. The UI and processing are written in Python (PySide6, NumPy, OpenCV). Only the lidar driver contact is kept in C++, exposed to Python as the `rs_bridge` module (pybind11).

## Features

- Live point cloud view from a RoboSense lidar (RSAIRY model, see note below)
- Colour-banded depth view using percentage-based bands
- Static-point filtering (voxel-based, multi-frame)
- Probe mode: cursor-based readout of position and velocity values
- UI layout editable in Qt Designer (`ui/mainwindow.ui`)

## Project Structure

```
main.py                         Entry point; loads the UI and connects signals
app/__init__.py                 Package marker
app/lidar_view.py               Lidar view, point processing, colour bands
app/widgets.py                  ToggleSwitch and GaugePanel widgets
ui/mainwindow.ui                Layout (edit with Qt Designer)
bridge/                         C++ source and CMake project for rs_bridge
rs_bridge.cp312-win_amd64.pyd   Built bridge module (Python 3.12, Windows x64)
```

`rs_bridge` must sit next to `main.py` so Python can import it.

## Requirements

- Windows 10/11, x64
- Python 3.12 (from python.org)
- Visual Studio Build Tools with the "Desktop development with C++" workload (only needed to rebuild `rs_bridge`)
- CMake and NMake (included with the Build Tools)
- Lidar connected to the PC by Ethernet, with the PC's IP set on the same subnet as the lidar

## Setup

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bat
python main.py
```

The bridge listens on:

| Stream | UDP port |
|--------|----------|
| msop (point data) | 6699 |
| difop (device info) | 7788 |

Make sure your firewall allows incoming UDP on these ports.

## Using the UI

- **FIRE / search switch (`swSearch`)**: turns probe mode on and off. Probe mode is enabled when this switch is off.
- **Static switch (`swStatic`)**: hides points classified as static.
- **Range (`rangeSpin`)**: maximum display range in metres (default 100 m).
- **Gauges (`gVx`, `gVy`, `gVz`, `gV`)**: show probe velocity and position values.

### Editing the layout

1. Open `ui/mainwindow.ui` in Qt Designer (Qt Creator: double-click the file).
2. Change positions, sizes, and properties. For gauges, edit `title`, `minimum`, and `maximum` in the Property Editor.
3. Save and run `python main.py`. No recompile is needed.

Do not rename these widgets, because `main.py` looks them up by name: `lidarView`, `swSearch`, `swStatic`, `rangeSpin`, `gVx`, `gVy`, `gVz`, `gV`.

## Colour Bands

The `BANDS` table in `app/lidar_view.py` defines the depth colour bands by percentage of the maximum range:

| Range | Band |
|-------|------|
| 0–10% | Band 1 |
| 10–50% | Band 2 |
| 50–90% | Band 3 |
| 90–100% | Band 4 |

Edit the boundaries and colours in that table.

## Rebuilding rs_bridge

Run these in a "x64 Native Tools" prompt, from the project root:

```bat
cd bridge
cmake -S . -B build -G "NMake Makefiles" ^
  -DRS_DRIVER_SRC=<path-to-rs_driver-source> ^
  -Dpybind11_DIR=<path-to-pybind11-cmake-dir> ^
  -DPython_EXECUTABLE=..\.venv\Scripts\python.exe
cmake --build build
```

Then copy the built `rs_bridge.cp312-win_amd64.pyd` from `bridge\build` to the project root.

The build defines `DISABLE_PCAP_PARSE`, so only live UDP input is supported. PCAP playback is not included.

## Troubleshooting

- **Black screen, no points**: check the cable, the PC IP, and that UDP ports 6699 and 7788 are open.
- **`ImportError: rs_bridge`**: the `.pyd` is missing from the project root, or it was built for a different Python version. It must match Python 3.12.
- **Lidar model**: the bridge is configured for RSAIRY. Other models need a change in `bridge/rs_bridge.cpp` and a rebuild.

## Known Limitations

- Output of the `fire` command over UDP is not implemented yet (`swFire` is a TODO).
- The FIRE button in `mainwindow.ui` is not connected to any action yet.
- Performance is about 10 Hz from the lidar; the view may lag by about one frame because of the 3-frame median filter.

## Licence

Add your licence here.
