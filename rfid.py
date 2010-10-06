#!/usr/bin/env python

"""Read the README.md file"""

################################################################################
# MIT License - Share/modify/etc, but please keep this notice.
#
# Copyright (c) 2010 Matt Williamson, App Delegate Inc
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
################################################################################

import sys
import os
import sqlite3
import serial
import subprocess

# Change this to the port displayed in your Arduino IDE
# It will be com3 or something for Windows...
serial_port = '/dev/tty.usbserial-A70064Mh'
baud_rate = 9600

# Define the db path to ./rfids.db, relative to this file
sql_file = os.path.join(os.path.dirname(__file__), 'tags.db')
needs_creation = not os.path.exists(sql_file)
db_connection = sqlite3.connect(sql_file)
db_connection.row_factory = sqlite3.Row

if needs_creation:
    print 'Creating initial database...'
    cursor = db_connection.cursor()
    cursor.execute("CREATE TABLE rfid_tags (tag_id text, is_enabled integer)")
    db_connection.commit()
    print 'Database created.'

def access_granted(serial_com):
    # This is called when a tag has been scanned and validated
    # Write your own logic here to do more on the computer
    
    say('Access Granted')
    # Send the letter G for grant
    serial_com.write('G')
    print 'Tag access granted.'
    
def access_denied(serial_com):
    # This is called when a tag has been scanned and denied
    # Write your own logic here to do more on the computer
    
    say('Access Denied')
    # Send the letter D for deny
    serial_com.write('D')
    print 'Tag access denied.'

def usage():
    sys.exit("""
RFID Reader Authentication Server
    
Usage
    Run authentication server: 
        python rfid.py serve
        
    List all tags: 
        python rfid.py list
        
    Disable tag: 
        python rfid.py disable <tag>
        
    Enable previously disabled tag: 
        enable <tag>
    """)
    
# If on OS X, we can speak, flite is a viable alternative for others
can_say = os.path.exists('/usr/bin/say')
def say(text):
    global can_say
    if can_say:
        subprocess.call(['say', '-v', 'Zarvox', text])
    
def run_server():
    print 'Starting serial server...'
    try:
        com = serial.Serial(serial_port, baud_rate)
        print 'Connected to arduino. Awaiting RFID scans.'
        chars = []
        while True:
            char = com.read()
            # Read characters from serial until we hit line endings
            if char != '\r' and char != '\n' and len(chars) <= 10:
                chars.append(char)
                # If we have 10 characters, then we have an RFID tag
                if len(chars) >= 10:
                    tag_id = ''.join(chars[:10])
                    print 'Checking tag:', tag_id
                    cursor = db_connection.cursor()
                    cursor.execute('SELECT * FROM rfid_tags WHERE tag_id = ?', (tag_id,))
                    record = cursor.fetchone()
                    if record and record['is_enabled']:
                        access_granted(com)
                    else:
                        access_denied(com)
            else:
                # Reset buffer
                chars = []
    except serial.SerialException:
        print '*ERROR*'
        print 'Could not open serial port.'
        sys.exit('Edit rfid.py and make sure you define serial_port properly.')

def main():
    if len(sys.argv) > 1:
        cursor = db_connection.cursor()
        if sys.argv[1] == 'list':
            print 'All Tags:'
            cursor.execute('SELECT * FROM rfid_tags')
            for row in cursor:
                print '\t', row['tag_id'], 'ENABLED' if row['is_enabled'] else 'disabled'
            return True
        if sys.argv[1] == 'disable' or sys.argv[1] == 'enable':
            if len(sys.argv) == 3:
                tag_id = sys.argv[2]
                if len(tag_id) != 10:
                    sys.exit('*ERROR* Tag must be 10 character long, hexidecimal.')
                cursor.execute('SELECT * FROM rfid_tags WHERE tag_id = ?', (tag_id,))
                record = cursor.fetchone()
                enabled = sys.argv[1] == 'enable'
                if record:
                    cursor.execute('UPDATE rfid_tags SET is_enabled = ? WHERE tag_id = ?', (enabled, tag_id))
                    db_connection.commit()
                    print '%s access for tag' % ('ENABLED' if enabled else 'disabled')
                else:
                    print 'Added tag with access %s' % ('ENABLED' if enabled else 'disabled')
                    cursor.execute('INSERT INTO rfid_tags (tag_id, is_enabled) VALUES (?, ?)', (tag_id, enabled))
                    db_connection.commit()
                return True
        if sys.argv[1] == 'serve':
            run_server()
    usage()

if __name__ == '__main__':
    main()
