# ESP32 Star Wars Tactical Display

A Star Wars-inspired tactical display project for the Waveshare ESP32-S3-Touch-LCD-4 (4-inch Capacitive Touch Display).

## Hardware Requirements

- Waveshare ESP32-S3-Touch-LCD-4 (4-inch, 480x480 IPS Display)
- USB-C cable for programming

## Software Requirements

1. Visual Studio Code
2. PlatformIO IDE Extension
3. Python (Required for PlatformIO CLI)

## Project Setup

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Visual Studio Code
3. Install PlatformIO IDE extension in VS Code
4. Clone or download this project
5. Open the project folder in VS Code
6. PlatformIO will automatically install the required dependencies

## Features

- Star Wars-style tactical display
- Rotating targeting reticle
- Aurebesh text rendering
- Animated radar-like elements
- Touch interaction support (coming soon)

## Display Layout

The display features:
- Central targeting reticle
- Tactical arcs and angle lines
- Status panels with Aurebesh text
- Animated scanning effects

## Development Notes

- Using LovyanGFX library for display control
- Custom 8x8 Aurebesh font implementation
- Hardware-specific optimizations for ESP32-S3

## Troubleshooting

If you encounter issues:
1. Verify all connections
2. Check USB port in platformio.ini
3. Ensure ESP32-S3 board is properly powered
4. Verify touch screen calibration

## License

MIT License - Feel free to modify and distribute as needed.
