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
The game includes a custom Bluetooth IoT component that allows players to control the game using physical controllers built with Raspberry Pi Pico W devices.

### Technical Details
- **Communication Protocol**: Uses BLE (Bluetooth Low Energy) for wireless communication
- **Data Format**: 
  - Y Controller: `<HB` (unsigned short and unsigned byte) for Y position and button state
  - X Controller: `<H` (unsigned short) for X position
- **Target Devices**: 
  - "PicoYButton" - Controls jumping and button actions
  - "PicoXAxisOnly" - Controls horizontal movement

### Key Components
- **BluetoothV2/bluetooth_controller.py**: Core Bluetooth communication module that handles device discovery, connection management, and data processing
- **BluetoothV2/game_controller.py**: Game-specific controller interface that translates raw Bluetooth data into game actions
- **BluetoothV2/bleaktest.py**: Standalone test script for BLE connectivity debugging

### Features
- **Modular Architecture**: Bluetooth functionality is encapsulated in reusable modules
- **Multi-Device Support**: Connects to two separate Pico devices simultaneously
- **Background Threading**: Bluetooth operations run in a separate thread to avoid blocking the game loop
- **Automatic Reconnection**: Automatically reconnects if devices disconnect
- **Visual Feedback**: On-screen status indicator shows Bluetooth connection state
- **Joystick Deadzone**: Implements deadzone handling to prevent jitter
- **Fallback Controls**: Keyboard controls remain functional when BLE devices are not connected

### Game Control Mapping
- **X-Axis Controller**: Controls left/right movement in the platformer
- **Y-Axis Controller**: Triggers jumps when moved upward
- **Button**: Available for future functionality

### Bluetooth Integration in Game Flow

The Bluetooth controllers are fully integrated into the game's navigation flow across both platformer and first-person modes:

1. **Initialization**:
   - Bluetooth controllers are initialized when the platformer game is loaded
   - Each level loaded through `play_level.py` automatically connects to the Bluetooth devices
   - Visual feedback shows connection status in the top-left corner of the screen

2. **Input Handling**:
   - The game accepts input from both Bluetooth controllers and keyboard simultaneously
   - Keyboard controls serve as a fallback when Bluetooth is not connected
   - Smart priority handling prevents conflicts between input methods

3. **Controller Lifecycle**:
   - Controllers are properly initialized at the start of each game session
   - Background thread continuously monitors for device connections/disconnections
   - Controllers are properly cleaned up when exiting the game
   - Reconnection is automatic if devices disconnect during gameplay

4. **Cross-Mode Controller Sharing**:
   - A single Bluetooth controller instance is maintained throughout the entire game flow
   - When transitioning from platformer to first-person mode, the controller is passed seamlessly
   - This ensures continuous controller functionality across different game modes

### First-Person Mode Controller Integration

1. **Button Navigation**:
   - Players can use the X-axis controller (left/right) to navigate between buttons
   - The currently selected button is highlighted with a thicker border
   - The Y-axis controller (jump) or button press activates the selected button

2. **Interface Controls**:
   - Navigate between options like "Attack" and "Abilities" using the controller
   - Select answers to questions during the battle sequence
   - Choose abilities from the ability menu
   - Confirm actions with the jump button

3. **Visual Feedback**:
   - Selected buttons are highlighted with a thicker border and different color
   - This makes it clear which option is currently selected

## Game Navigation System

The game uses a state-based navigation system where different functions represent different screens or states of the application:

### Main Menu Structure

- **Entry Point**: The game starts by calling `main_menu()` in `start_page.py`
- **Main Menu Screen**: Displays four buttons: PLAY, OPTIONS, Q.MAKER, and QUIT
- **Instructions Screen**: Shows game instructions before starting gameplay

### Game Flow

1. User starts at the main menu
2. When selecting "PLAY":
   - The `play()` function is called
   - This shows the instructions screen via `show_instructions()`
   - After instructions, it calls `main()` from `play_level.py` with a level file
   - When the level is completed or quit, it returns to the main menu

### Game View Loading

The game has multiple views/modes that are loaded in different ways:

1. **Third-Person Platformer** (loaded via `play_level.py`):
   - The `main()` function loads a level from a JSON file
   - Creates all game objects (player, platforms, hazards, etc.)
   - Runs the game loop for the platformer

2. **First-Person Mode**:
   - Called via `run_game()` from the `first_person` module
   - Integrated within the level flow, triggered by events in the platformer

3. **Question Maker**:
   - Accessed via the Q.MAKER button
   - Calls `Qmaker()` from the question_maker module
   - Allows creating custom questions for the game

### Key Components

- **Button System**: Uses a custom `Button` class for all navigation elements
- **Level Loading**: Levels are stored as JSON files in a "levels" directory
- **Game State Management**: Each screen is a function with its own event loop
- **Bluetooth Integration**: Works with the platformer mode, controlling player movement

## Game Features
- **First-Person Mode**: Turn-based combat with question-answer mechanics, timer system, and abilities
- **Third-Person Mode**: 2D platformer with physics, platform collision, hazards, and "coyote time" jump mechanics
- **Level Building**: Custom level creation system
- **Question System**: JSON-based question database with custom question creation tools
