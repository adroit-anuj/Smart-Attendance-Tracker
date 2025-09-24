

import serial
import pandas as pd
import csv
import datetime
import time
from sklearn.linear_model import LinearRegression
import numpy as np

# Serial port configuration (adjust COM port as needed)
SERIAL_PORT = 'COM3'  # On Windows; use '/dev/ttyUSB0' or similar on Linux/Mac
BAUD_RATE = 9600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# File paths for CSV logs
ATTENDANCE_LOG = 'attendance_log.csv'
SESSION_DATA = 'session_data.csv'

# Initialize session state
session_active = False
professor_uid = 'PROF1234'  # Example professor UID
subject_id = 'EE-396'      # Example subject ID
session_start_time = None
attendance_records = {}    # {UID: [entry_time, exit_time]}
session_temps = []
session_humids = []

# Load or initialize session data for predictions
try:
    session_df = pd.read_csv(SESSION_DATA)
except FileNotFoundError:
    session_df = pd.DataFrame(columns=['Date', 'Subject', 'Prof_UID', 'Attendance_Count', 'Avg_Temp', 'Avg_Humid'])

def initialize_attendance_log():
    """Initialize attendance_log.csv if it doesn't exist."""
    try:
        with open(ATTENDANCE_LOG, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'UID', 'Status'])
    except FileExistsError:
        pass

def log_attendance(date, uid, status):
    """Log attendance to CSV."""
    with open(ATTENDANCE_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, uid, status])

def end_session():
    """End the session, compute averages, and predict next attendance."""
    global session_active, session_start_time, attendance_records, session_temps, session_humids, session_df
    if not session_active:
        return
    
    # Count present students (those with both entry and exit scans)
    present_count = sum(1 for uid, times in attendance_records.items() if times[1] is not None)
    
    # Compute average temperature and humidity
    avg_temp = sum(session_temps) / len(session_temps) if session_temps else 0
    avg_humid = sum(session_humids) / len(session_humids) if session_humids else 0
    
    # Log session data
    session_data = {
        'Date': session_start_time.strftime('%Y-%m-%d'),
        'Subject': subject_id,
        'Prof_UID': professor_uid,
        'Attendance_Count': present_count,
        'Avg_Temp': round(avg_temp, 2),
        'Avg_Humid': round(avg_humid, 2)
    }
    session_df = pd.concat([session_df, pd.DataFrame([session_data])], ignore_index=True)
    session_df.to_csv(SESSION_DATA, index=False)
    
    # Predict next session's attendance using linear regression
    if len(session_df) >= 2:  # Need at least 2 points for regression
        X = np.array(range(1, len(session_df) + 1)).reshape(-1, 1)  # Day numbers
        y = session_df['Attendance_Count'].values  # Attendance counts
        model = LinearRegression()
        model.fit(X, y)
        next_day = len(session_df) + 1
        predicted_attendance = model.predict([[next_day]])[0]
        print(f"Predicted attendance for next session: {round(predicted_attendance)}")
    
    # Reset session
    session_active = False
    session_start_time = None
    attendance_records.clear()
    session_temps.clear()
    session_humids.clear()

def main():
    global session_active, session_start_time, attendance_records, session_temps, session_humids
    initialize_attendance_log()
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            current_time = datetime.datetime.now()
            
            if line.startswith('Student ID: '):
                uid = line.split(': ')[1]
                if not session_active:
                    if uid == professor_uid:
                        session_active = True
                        session_start_time = current_time
                        ser.write('Logged_1000\n'.encode('utf-8'))
                        print(f"Session started by professor at {session_start_time}")
                    else:
                        ser.write('Rejected_2000\n'.encode('utf-8'))
                        log_attendance(current_time.strftime('%Y-%m-%d'), uid, 'Rejected')
                else:
                    if uid == professor_uid:
                        end_session()
                        ser.write('Logged_1000\n'.encode('utf-8'))
                        print("Session ended")
                    else:
                        # Dual-scan verification
                        if uid not in attendance_records:
                            attendance_records[uid] = [current_time, None]
                            ser.write('Logged_1000\n'.encode('utf-8'))
                            log_attendance(current_time.strftime('%Y-%m-%d'), uid, 'Entry')
                        elif attendance_records[uid][1] is None:
                            attendance_records[uid][1] = current_time
                            ser.write('Logged_1000\n'.encode('utf-8'))
                            log_attendance(current_time.strftime('%Y-%m-%d'), uid, 'Present')
                        else:
                            ser.write('Ignored_1500\n'.encode('utf-8'))
                            log_attendance(current_time.strftime('%Y-%m-%d'), uid, 'Ignored')
            
            elif line.startswith('Temp: '):
                try:
                    temp = float(line.split('Temp: ')[1].split(' C')[0])
                    humid = float(line.split('Humid: ')[1].split(' %')[0])
                    if session_active:
                        session_temps.append(temp)
                        session_humids.append(humid)
                        print(f"Logged Temp: {temp} C, Humid: {humid} %")
                except ValueError:
                    print("Invalid sensor data received")
            
            elif line == '!!!!!!DHT Error!!!!!!':
                print("DHT sensor error detected")
        
        time.sleep(0.01)  # Reduced from 100ms to 10ms for responsiveness

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        ser.close()
        print("Program terminated, serial port closed")
     
