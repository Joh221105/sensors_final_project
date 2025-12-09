# Sensors Final Project

## OVERVIEW

### rotary deCODEr

A hardware-driven reflex and timing game built on the ESP32-S3 using CircuitPython, combining rotary input, motion detection, tactile feedback, and sound effects into a compact arcade experience. Players rotate a cursor on a circular dial, attempt precision hits, survive random motion events, and race against a decreasing timer.

The game includes:

- Campaign Mode (10 levels - Easy/Medium/Hard)
- Endless Survival Mode
- Global High Scores for both modes
- Sound & visual feedback
- A separate BLE-connected “Safe Device” that unlocks only when the player wins

This project blends electronics, embedded programming, and game design into a unique physical experience.

### System Architecture Overview

The game uses two ESP32-S3 boards:

- 1. Main Game Board (ESP32-S3)
      - Rotary encoder input
      - Button press
      - NeoPixel feedback
      - Accelerometer (stay-still challenge)
      - OLED game UI
      - Piezo buzzer sound effects
      - Game logic (levels, scoring, endless mode)

- 2. Standalone Safe Device (ESP32-S3)
      - A separate physical object (a box, lock, door, puzzle, etc.) that stays locked until player wins
      - Upon victory, the servo moves a certain degree to unlock latch


### How to Play
1. Select a Mode
- Upon boot:
    - Campaign Mode (10 Levels - Easy/Medium/Hard)
    -   Easy → 3 Lives
    -   Medium → 2 Lives
    -   Hard → 1 Life
    - Endless Mode
2. Rotate to Move the Cursor
  - Turn the rotary encoder clockwise or counterclockwise to slide your cursor around the circle.

3. Press the Button to Hit the Zone

  - Hit the button when the cursor overlaps the glowing success zone.
  - Success decrease the number of inputs remainining
  - Failure causes a stunned screen for 2 seconds

4. Stay still events
  - Hold the device perfectly still to pass

5. Campaign Mode ramps up difficulty by shrinking zones, lowering timers, and speeding rotation response.

6. Scoring
  - At the end of each level, remaining time is added to total score

7. Endless Mode (Survival)
  - Starts with 30 seconds, zone gets smaller every 3 successful input
  - Every successful input adds 1 second
  - Survive as long as possible for high score


### Safe Device Integration (Second ESP32-S3)

Separate safe/vault structure, remains using a servo motor until the user beats the game
- Listens via BLE for command from controller esp32-s3 to rotate to unlock latch

Integration allows project to double as a productivity tool, increasing difficulty to access easily distracting devices


### Hardware Used

- ESP32-S3 x2 (Game + Safe Device)
- ADXL345 Accelerometer
- Rotary Encoder
- Passive Piezo Buzzer
- 128×64 SSD1306 OLED
- NeoPixel (single LED)
- Servo (for Safe Lock)
- Button input

### Design Inspiration

- Safecracking wheels
- Dial to represent a dial when unlocking a safe
- Arcade timing bars
- Safe-like enclosure to 

### Future Ideas

- 2-player sabotage mode (one player disrupts the other via BLE, introduction of a third microcontroller)
- Add new random events to increase difficulty and add variety

> Portions of this project were developed with assistance from OpenAI’s ChatGPT and Anthropic’s Claude.
