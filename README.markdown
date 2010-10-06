Arduino RFID Authentication
===========================

This is an RFID authentication system. It allows a person to place an RFID tag within proximity of the reader device (usually 5-6 inches with this reader) and it will look up the tag in an SQLite database to check if it should grant access. If authorization is granted, the hardware device will turn a servo motor into a second position. The primary application of this being the unlocking of a door. This implementation also speaks aloud "Access Granted" or "Access Denied" if you are running the server on OS X. You can modify the source to use something like `flite` on other OSes. This project is very easily modified to do any sort of task. Some ideas are:

* Door locking (default implementation)
* An employee punch-in/punch-out system
* Real world item identification (affix a tag to every day items, such as your wallet; when scanned, open a web banking web page. attach one to your phone to initiate a Google Voice call, etc.)
* Russian roulette with RFID tags instead of guns


Here it is in action.

<object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/mws0nqkqvGg?hl=en&fs=1"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/mws0nqkqvGg?hl=en&fs=1" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>

[Via Youtube](http://www.youtube.com/watch?v=mws0nqkqvGg)

Hardware
--------

To make this RFID system, you'll need the following hardware:

* 1 Arduino (buy them from [Amazon](http://www.amazon.com/gp/product/B001N1EOT8?ie=UTF8&tag=appdelinc-20&linkCode=xm2&camp=1789&creativeASIN=B001N1EOT8) [arduino.cc](http://arduino.cc/en/Main/Buy))
* 1 Servo (I like [Hobby Partz](http://www.hobbypartz.com/) because they are cheap) *you don't need this if you are not unlocking a door*
* 1 RFID Reader module (buy from your local [Radio Shack](http://www.radioshack.com/product/index.jsp?productId=2906723) or [Parallax](http://www.parallax.com/StoreSearchResults/tabid/768/txtSearch/RFID/List/0/SortField/4/ProductID/114/Default.aspx)) *$8 if you get lucky and find one at Radio Shack*
* Some jumper wires to wire the whole thing together


Software
--------

* [Python](http://python.org) (2.6 tested, should work on 2.7)
* [pySerial](http://pyserial.sourceforge.net/)
* [Arduino IDE](http://www.arduino.cc/en/Main/Software)
* [NewSoftSerial](http://arduiniana.org/libraries/newsoftserial/)
* The Arduino sketch and the rfid.py file included with this README file


Usage
-----

**Wire it Up**

You can use the image `schematic/reader_breadboard.png` to reference the wiring diagram. Basically you just need to wire the pins as follows:

* Arduino pin 8         -> RFID pin SOUT
* Arduino pin 9         -> RFID pin /ENABLE
* Arduino pin GND       -> RFID pin GND
* Arduino pin 5V        -> RFID pin VCC

* Arduino pin GND       -> Servo wire BLACK
* Arduino pin Vin (9v)  -> Servo wire RED
* Arduino pin 3         -> Servo wire YELLOW

![Schematic](http://appdelegateinc.com/blog/wp-content/uploads/2010/10/rfid_bb.png)


You should end up with something like this.

![Overview](http://appdelegateinc.com/blog/wp-content/uploads/2010/10/overview.jpg)

![Close Up](http://appdelegateinc.com/blog/wp-content/uploads/2010/10/close_up.jpg)

**Program the Arduino**

First you need to install the `NewSoftSerial` library for Arduino. Read the [Arduino docs](http://www.arduino.cc/en/Reference/Libraries) on how to install a library.

Plug the Arduino into your computer and open the sketch `sketch/rfid_sketch.pde` with the Arduino IDE. Select which serial port to use for the Arduino (`Tools->Serial Port` on OS X). Click the upload button to write the sketch to your Arduino. You may need to try a few different ports before it works. Write down the port name, we'll need it later. It should look something like `/dev/tty.usbserial-A70064Mh` or `COM3`. It will probably be different for your machine.


**Set Up the Server**

Install the [pySerial](http://pyserial.sourceforge.net/) serial library for python. If you have `setup tools` installed, you can just run `easy_install pyserial`.

Open `rfid.py` with a text editor and look for this line: `serial_port = '/dev/tty.usbserial-A70064Mh'`. Change the `/dev/tty.usbserial-A70064Mh` to the serial port you wrote down in the previous step.

First, we'll run the server to watch for the RFID tags we want to allow. Open a terminal and cd to the project directory. Then run `python rfid.py serve`. This tells the python server to listen to the serial device for RFID tags. It will print debug information into the console.

    wraith:rfid mwilliamson$ python rfid.py serve
    Starting serial server...
    Connected to arduino. Awaiting RFID scans.
    Checking tag: 0F03042E80
    Tag access denied.
    ^C

Hit ctrl-c to kill the program. Now we have a tag we can enable: `0F03042E80`. We'll use the `enable` command to enable it.

    wraith:rfid mwilliamson$ python rfid.py enable 0F03042E80
    Added tag with access ENABLED

Now that we've added the tag, we can scan it successfully. You should see the servo spin, or a least the built in LED on pin 13 of the arduino will light up.

    wraith:rfid mwilliamson$ python rfid.py serve
    Starting serial server...
    Connected to arduino. Awaiting RFID scans.
    Checking tag: 0F03042E80
    Tag access granted.

You can revoke access to a particular tag by running the `disable command`

    wraith:rfid mwilliamson$ python rfid.py disable 0F03042E80
    disabled access for tag


**Errors**

If you see the following, make sure your Arduino is plugged into your computer and you correctly set up the serial port in `rfid.py`

    wraith:rfid mwilliamson$ python rfid.py serve
    Starting serial server...
    *ERROR*
    Could not open serial port.
    Edit rfid.py and make sure you define serial_port properly.

