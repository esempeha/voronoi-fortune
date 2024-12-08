# Voronoi Diagram with Fortune's Algorithm

### Group

Introducing our group **kindaVoronoi()** consisting of
1. Abbilhaidar Farras Zulfikar (2206026012)
2. Ravie Hasan Abud (2206031864)
3. Jason Kent Winata (2206081313)

Here, we design a Voronoi diagram algorithm using Fortune's algorithm and visualize it using the Python programming language with the help of the TKinter library.

## Getting Started

### Requirements
Make sure you have installed:
- Python 3.x
- Tkinter

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/esempeha/voronoi-fortune.git
   ```

2. Navigate to the project directory:
   ```bash
   cd voronoi-fortune
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Features

- Add point(s) and automatically generate the voronoi diagram: 
   - clicking on the canvas to add a point
   - manually enter the point coordinates in X and Y input text
   - load a .txt file with the point format (x, y) or x, y by clicking the "Load Point(s)" button
   - generate random points by clicking the "Random Points" button to add 15-30 random points and automatically generate the voronoi diagram
- Delete point(s) and automatically update the voronoi diagram: 
   - clear all points by clicking the "Clear All" button
   - clear a specific point by choosing a specific point and then click the "Delete Selected Point" button
- Save point(s) to a .txt file by clicking the "Save Point(s)" button