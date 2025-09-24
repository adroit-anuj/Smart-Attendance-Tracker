## Youtube video link : https://youtu.be/zJNw-fKk1p0?si=IvCjLdzy4YcPM6TO

# RFID-Based Attendance System with Environmental Monitoring

This project implements an RFID-based attendance system integrated with environmental monitoring, designed for classroom use. It uses an Arduino Uno to read RFID tags, monitor temperature and humidity via a DHT22 sensor, display real-time feedback on an I²C LCD, and provide audible cues via a buzzer. A Python backend logs attendance and environmental data to CSV files and predicts future attendance using linear regression. A Tkinter-based GUI displays real-time logs, session summaries, and predictions.

## Features

- **RFID Attendance**: Scans 13.56 MHz RFID tags to log student entry/exit with dual-scan verification.
- **Environmental Monitoring**: Measures temperature and humidity every 3 seconds using a DHT22 sensor.
- **Real-Time Feedback**: Displays scan status on a 16x2 LCD and plays buzzer tones (e.g., 1000Hz for success, 2000Hz for rejection).
- **Data Logging**: Stores attendance (`attendance_log.csv`) and session summaries (`session_data.csv`).
- **Predictive Analytics**: Uses linear regression to forecast the next session’s attendance based on historical data.
- **GUI Interface**: Displays real-time attendance logs, session data, environmental readings, and predicted attendance.

## Hardware Requirements

- **Arduino Uno** or compatible microcontroller
- **MFRC522 RFID Reader** (13.56 MHz, SPI interface)
- **DHT22 Sensor** (temperature and humidity)
- **LCD1602 with I²C Backpack** (16x2 display)
- **Buzzer** (active or passive, PWM-compatible)
- **RFID Tags** (passive, 13.56 MHz, ISO 14443A)
- **10kΩ Resistor** (for DHT22 pull-up)
- **Jumper Wires** and **Breadboard**
- **USB Cable** (for Arduino-PC connection)

### Pin Connections

- **MFRC522**:
  - SS (SDA): Pin 10
  - RST: Pin 9
  - MOSI: Pin 11
  - MISO: Pin 12
  - SCK: Pin 13
- **DHT22**:
  - Data: Pin 2 (with 10kΩ pull-up to 5V)
  - VCC: 5V
  - GND: Ground
- **LCD1602 (I²C)**:
  - SDA: A4
  - SCL: A5
  - VCC: 5V
  - GND: Ground
- **Buzzer**:
  - Positive: Pin 3 (PWM)
  - Negative: Ground

## Software Requirements

- **Arduino IDE** (for uploading the Arduino sketch)
- **Python 3.8+**
- Python libraries:
  ```bash
  pip install pyserial pandas scikit-learn
  ```
- **Tkinter** (included with standard Python)
- Arduino libraries:
  - `SPI` (built-in)
  - `MFRC522` (install via Arduino Library Manager)
  - `Wire` (built-in)
  - `LiquidCrystal_I2C` (install via Arduino Library Manager)
  - `DHT` (install via Arduino Library Manager)

## File Structure

```
rfid-attendance-system/
├── attendance_log.csv       # Logs RFID scans (Date, UID, Status)
├── session_data.csv         # Logs session summaries (Date, Subject, Prof_UID, Attendance_Count, Avg_Temp, Avg_Humid)
├── rfid_attendance.ino      # Arduino sketch for hardware control
├── backend.py               # Python backend for serial communication and data logging
├── gui.py                   # Python GUI for displaying logs and predictions
└── README.md                # Project documentation
```

## Setup Instructions

1. **Hardware Setup**:
   - Connect the MFRC522, DHT22, LCD1602, and buzzer to the Arduino Uno as per the pin connections above.
   - Ensure the DHT22 has a 10kΩ pull-up resistor between the data pin and 5V.
   - Connect the Arduino to your computer via USB.

2. **Arduino Setup**:
   - Install the Arduino IDE from [arduino.cc](https://www.arduino.cc/en/software).
   - Install the required Arduino libraries (`MFRC522`, `LiquidCrystal_I2C`, `DHT`) via the Library Manager.
   - Open `rfid_attendance.ino` in the Arduino IDE.
   - Upload the sketch to the Arduino Uno.

3. **Python Setup**:
   - Install Python 3.8+ from [python.org](https://www.python.org/downloads/).
   - Install required Python libraries:
     ```bash
     pip install pyserial pandas scikit-learn
     ```
   - Update the `SERIAL_PORT` variable in `gui.py` (and optionally `backend.py`) to match your Arduino’s port:
     - Windows: `COM3` (check in Device Manager)
     - Linux/Mac: `/dev/ttyUSB0` or `/dev/ttyACM0` (check with `ls /dev/tty*`)

4. **CSV Files**:
   - Ensure the project directory has write permissions for `attendance_log.csv` and `session_data.csv`.
   - Optionally, pre-populate `session_data.csv` with historical data (e.g., for the sequence \(1, 3, 3, 2, 1, 2\)):
     ```csv
     Date,Subject,Prof_UID,Attendance_Count,Avg_Temp,Avg_Humid
     2025-09-17,EE-396,PROF1234,1,25.0,60.0
     2025-09-18,EE-396,PROF1234,3,25.2,61.0
     2025-09-19,EE-396,PROF1234,3,25.1,60.5
     2025-09-20,EE-396,PROF1234,2,24.9,59.8
     2025-09-21,EE-396,PROF1234,1,25.3,60.2
     2025-09-22,EE-396,PROF1234,2,25.0,60.0
     ```

## Usage

1. **Run the GUI**:
   - Execute the GUI script:
     ```bash
     python gui.py
     ```
   - The GUI will display:
     - **Status**: Session active/inactive with start time.
     - **Environmental Data**: Real-time temperature and humidity.
     - **Attendance Log**: Scrolled text showing RFID scans (Date, UID, Status).
     - **Session Table**: Historical session data (Date, Subject, Prof_UID, Attendance, Avg_Temp, Avg_Humid).
     - **Prediction**: Predicted attendance for the next session.

2. **Start a Session**:
   - Scan the professor’s RFID card (UID: `PROF1234`) to start a session.
   - The GUI updates to show "Session: Active" with the start time.

3. **Log Attendance**:
   - Scan student RFID cards:
     - First scan: Logs "Entry".
     - Second scan: Logs "Present" (dual-scan verification).
     - Duplicate scans: Logs "Ignored".
     - Scans outside a session: Logs "Rejected".
   - The Arduino LCD shows the UID and status; the buzzer plays tones (1000Hz for logged, 2000Hz for rejected, etc.).

4. **Environmental Monitoring**:
   - The Arduino sends temperature and humidity every 3 seconds.
   - The GUI displays the latest readings; errors show as "Temp: Error | Humid: Error".

5. **End a Session**:
   - Scan the professor’s RFID card again to end the session.
   - The backend logs the session summary to `session_data.csv` (attendance count, average temperature/humidity).
   - The GUI updates the session table and shows the predicted attendance for the next session using linear regression.

6. **Prediction**:
   - The system predicts the next session’s attendance based on all prior sessions’ counts in `session_data.csv`.
   - For the sequence \(1, 3, 3, 2, 1, 2\), the prediction for the next session is ~1.8 (rounded to 2).

## Notes

- **Professor UID**: Replace `PROF1234` in `gui.py` with your actual professor RFID UID.
- **Subject ID**: Update `subject_id` (`EE-396`) in `gui.py` as needed.
- **Serial Port**: Verify the correct serial port using:
  - Windows: Device Manager
  - Linux/Mac: `ls /dev/tty*`
- **Linear Regression**: The GUI uses all prior sessions for prediction. To use a three-session window (as mentioned in the project report), modify the `end_session` function:
  ```python
  if len(session_df) >= 3:
      X = np.array(range(len(session_df)-2, len(session_df)+1)).reshape(-1, 1)
      y = session_df['Attendance_Count'].tail(3).values
  ```

## Troubleshooting

- **Serial Connection Fails**:
  - Ensure the Arduino is connected and the correct port is specified.
  - Close the Arduino IDE Serial Monitor to avoid port conflicts.
  - Check with:
    ```bash
    python -m serial.tools.list_ports
    ```
- **CSV Write Errors**:
  - Ensure the project directory has write permissions.
  - Close any programs accessing `attendance_log.csv` or `session_data.csv`.
- **DHT22 Errors**:
  - Verify the 10kΩ pull-up resistor and wiring.
  - Check for "!!!!!!DHT Error!!!!!!" in the GUI or console.
- **GUI Freezing**:
  - The serial loop runs in a separate thread, but if issues occur, adjust `time.sleep(0.01)` in `gui.py`.
- **Prediction Mismatches**:
  - Verify `session_data.csv` contents match your data (e.g., \(1, 3, 3, 2, 1, 2\)).
  - Check the regression logic in `end_session`.

## License

This project is for educational purposes and licensed under the MIT License.
