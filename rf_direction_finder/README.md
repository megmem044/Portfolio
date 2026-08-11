# RF Direction Finder

This repository contains the hardware and firmware for a portable RF direction-finding receiver. The design uses four antenna inputs and two coherent receive paths to capture I/Q data for estimating the direction of an incoming signal.

The project is under active development. The PCB design is present, but the firmware is still at the driver and bring-up stage; signal processing and bearing calculation have not been implemented in the application yet.

## System overview

The receiver is split into a digital section and an RF front end:

- Four coaxial antenna inputs feed two switchable receive paths.
- Each path includes RF filtering/amplification and an ADL5801 mixer.
- Two LMX2572 synthesizers provide the local oscillator signals from a shared reference clock.
- ADL5380 quadrature demodulators produce differential I/Q outputs.
- An ADS131B04 four-channel, 24-bit ADC samples the two I/Q pairs.
- An ESP32-S3 DevKitC-1 controls the RF switches, synthesizers, ADC, display, and supporting circuitry.
- The digital section also includes battery charging and power regulation.

## Repository layout

```text
.
|-- firmware/
|   `-- rdf_receiver/          PlatformIO project for the ESP32-S3
|       |-- lib/HAL/           RF switch, synthesizer, ADC, and LCD interfaces
|       |-- src/main.cpp       Application entry point
|       `-- platformio.ini     Board and library configuration
|-- hardware/
|   |-- rdf_kicad/             KiCad project, schematics, PCB, and interactive BOM
|   `-- custom_kicad_library/  Project-specific symbols, footprints, and 3D models
`-- mechanical/                Placeholder for enclosure and mechanical CAD
```

The main KiCad project is `hardware/rdf_kicad/rdf_kicad.kicad_pro`. Its hierarchical schematic is divided into the digital section, RF front end, two receive-path instances, LO generation, and ADC/power sections. A browser-based interactive BOM is available at `hardware/rdf_kicad/bom/ibom.html`.

## Firmware

The firmware targets an `esp32-s3-devkitc-1` using the Arduino framework. It is set up to use the standard SPI library along with Adafruit GFX and the ST7735/ST7789 display library.

Current HAL work includes:

- LMX2572 register loading, frequency configuration, and lock detection
- ADS131-series SPI register access and 24-bit sample reads
- RF switch and LCD interfaces
- Initial pin assignments for two RF switches, two synthesizers, one ADC, and a 240 x 240 display

Several parts are not complete. The pin assignments in `hal.h` are marked for correction, the RF switch and LCD implementations are unfinished, and `main.cpp` is still the default application scaffold.

### Build

Install [PlatformIO](https://platformio.org/), then run the following from the repository root:

```sh
cd firmware/rdf_receiver
pio run
```

To upload to a connected ESP32-S3:

```sh
pio run --target upload
```

PlatformIO downloads the libraries listed in `platformio.ini` during the first build. A successful build is not expected until the unfinished HAL implementations are completed.

## Hardware files

Open `hardware/rdf_kicad/rdf_kicad.kicad_pro` in KiCad to view the schematic and PCB layout. Keep `hardware/custom_kicad_library` in place because the design uses the symbols, footprints, and 3D models stored there.

The hardware design includes components such as:

- ESP32-S3-DevKitC-1-N8R8
- LMX2572 frequency synthesizers
- ADL5801 mixers and ADL5380 quadrature demodulators
- ADS131B04-Q1 ADC
- BSW6440 RF switches
- MCP73871 battery charger and TPS61090 boost converter

The checked-in PCB and BOM should be reviewed against the schematics and manufacturer data before fabrication. The design contains project-specific footprints and existing DRC exclusions that need to be considered during that review.

## Project status

- KiCad hierarchical schematics: present
- PCB layout: present
- Interactive BOM: present
- ESP32-S3 PlatformIO project: configured
- Peripheral drivers: partially implemented
- Data acquisition and direction-finding algorithm: not implemented
- Mechanical enclosure files: not yet added
