# Skils1Project

## Team Members
Noman- Helps with everything (primarily IOT and programming the game)
Willem- Game programming (3rd person)
Mohammed- Game programming (1st person)
Klaudija- Animation and aesthetics
Ray- IOT programming

## Game Overview
This project is a game with both first-person and third-person gameplay modes built using Pygame. The first-person mode features a turn-based combat system with question-answer mechanics, while the third-person mode offers platformer gameplay with physics and collision detection.

## Bluetooth IoT Integration
The game includes a custom Bluetooth IoT component that allows players to control the game using a physical joystick controller (Raspberry Pi Pico W).

### Technical Details
- **Communication Protocol**: Uses BLE (Bluetooth Low Energy) for wireless communication
- **Data Format**: `<HHB` (two unsigned shorts and one unsigned byte) for X position, Y position, and button state
- **Target Device**: "PicoJoystick-AIO" (Pico W running custom firmware)

### Key Components
- **bleaktest.py**: Standalone test script for BLE connectivity debugging

### Features
- Thread-safe communication between BLE and game threads
- Automatic reconnection if the device disconnects
- Joystick deadzone handling to prevent jitter
- Fallback to keyboard controls when BLE device is not connected

## Game Features
- **First-Person Mode**: Turn-based combat with question-answer mechanics, timer system, and abilities
- **Third-Person Mode**: 2D platformer with physics, platform collision, hazards, and "coyote time" jump mechanics
- **Level Building**: Custom level creation system
- **Question System**: JSON-based question database with custom question creation tools
