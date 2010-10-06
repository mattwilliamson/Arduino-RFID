/*
RFID Reader that checks RFID tags against a database on a computer and
turns a servo if it is a valid tag in the database. See 
http://appdelegateinc.com/blog/2010/10/06/rfid-auth-using-arduino-and-python
for more details.

MIT License - Share/modify/etc, but please keep this notice.

Copyright (c) 2010 Matt Williamson, App Delegate Inc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

// RFID Settings
#include <NewSoftSerial.h>
// NewSoftSerial needs pin in and out, but RFID Reader only has IN
int pinUnused = 12;
int pinRfidEnable = 9;
int pinRfidSerialIn = 8;
int baudRateRfid = 2400;
NewSoftSerial rfidSerial(pinRfidSerialIn, pinUnused);


// These are used for serial communication
int val = 0; 
char rfid[10];
int bytesRead = 0;

// Servo settings
#include <Servo.h> 
Servo servo;
int pinServo = 3;
int servoLockedRotation = 150;
int servoUnlockedRotation = 30;
int unlockTime = 3000;

int pinLed = 13;

void emptySerialBuffers() {
   // This empties the serial buffers to prevent repeat reads
   while(rfidSerial.available() > 0) {
        rfidSerial.read();
    }
    while(Serial.available() > 0) {
        Serial.read();
    }
}

void setup() {
    // Serial to computer
    Serial.begin(9600);
    
    // Set up RFID Reader
    rfidSerial.begin(baudRateRfid);
    pinMode(pinRfidEnable, OUTPUT);
    digitalWrite(pinRfidEnable, LOW);

    // Set up servo
    servo.attach(pinServo);
    servo.write(servoLockedRotation);
    
    pinMode(pinLed, OUTPUT);
    digitalWrite(pinLed, LOW);
}

void loop() {
    // Read serial from RFID reader
    if(rfidSerial.available() > 0) {
        val = rfidSerial.read();
        
        // Got signal from RFID Reader
        if(val == 10) {
            bytesRead = 0;
            while(bytesRead < 10) {
                if(rfidSerial.available() > 0) {
                    val = rfidSerial.read();
                    // Line endings mean end of message
                    if(val == 10 || val == 13) {
                        break;
                    } 
                    rfid[bytesRead] = val;
                    bytesRead++;
                } 
            } 
            if(bytesRead == 10) {
                emptySerialBuffers();  
                // Send RFID tag to computer
                Serial.println(rfid);
                digitalWrite(pinRfidEnable, HIGH);
                // Wait for response from computer
                while(Serial.available() == 0) {
                    delay(10);
                }
            }
            bytesRead = 0;
        }
    }
    
    // Read serial from computer
    if(Serial.available() > 0) {
        // Got signal from computer
        // Disable RFID reader so we don't get repeats
        digitalWrite(pinRfidEnable, HIGH);
        val = Serial.read();
        
        if(val == 'G') {
            // Access Granted
            digitalWrite(pinLed, HIGH);
            servo.write(servoUnlockedRotation);
            delay(unlockTime);
            digitalWrite(pinLed, LOW);
            servo.write(servoLockedRotation);
        } else if(val == 'D') {
            // Access Denied
            // Wait a moment so we can't brute force crack
            delay(1000);
        }
        
        emptySerialBuffers();
    }
    
    // Reactivate RFID antenna
    digitalWrite(pinRfidEnable, LOW);
}

