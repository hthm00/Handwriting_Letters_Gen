# Handwriting_Letters_Gen

![handwriting_letter_image](https://mhuynh.dev/assets/Handwritting%20Robot.jpg)

## Inspiration
Chances of opening and replying a hanwriting letter are 50% higher rates than a printed one.

## What it does
Scans printed notes on the envelope and turns it into a handwritting one.

## How I built it
* Using an existing 3D Printer, I added a pen holder and a camera to capture the printed notes.
* I wrote a Python script to convert my handwriting font into GCode file (that is used to upload to the 3D Printer) 

## Challenges I ran into
* Converting handwriting font into coordinates is extremely buggy
* Pytesseract OCR is not always accurate, so I need to add a RegEx expression to regconize if it detects an address
* Adding a feeder to feed each envelope one after the other

## Accomplishments that I am proud of
Make it sucessfully run!!!

## What I learned
* Controlling the 3D Printer remotely by installing Rasberry Pi
* Control Elegoo Uno R3 using Python commands

## What's next
* Adding a belt with a motor so the evenlopes could run one after another

## Built With
python c++
