## py4pd-upic

`py4pd-upic` is a Pure Data (Pd) external object inspired by the works of Iannis Xenakis. This object is designed to facilitate the conversion of SVG (Scalable Vector Graphics) data into coordinate information within the Pure Data environment.

## List of Objects

### Playback
- **`u.playsvg`**: 
  - Method: `read` the svg file, requires the svg file.
  - Method: `play` the svg file;
  - Method: `stop` the player;
    
### Message Retrieval
- **`u.getmsgs`**: 
  - Method: Get all messages set in the properties text input inside Inkscape.
  
### Atributtes

- **`u.filterattr`**: Filter object by attribute.
    - Avaiable atributter are: `fill`, `stroke`, `eventType`, `sides`, `duration`, `onset`. 
  
- **`u.getattr`**: Method to get the values of some attribute for some svg form.

### Subevents

Subevents are svgs draw inside svgs draws. 

- **`u.getchilds`**: Returns a list with all the childs of the event.  
- **`u.playchilds`**: Put the childs on time, playing following the onset of the father.

### Paths
- **`u.getpath`**: Get the complete path of paths.
- **`u.playpath`**: Play the complete path of paths.


## Install

1. Create a new Pure Data patch.
2. Create a `py4pd` object.
3. Send a message with `pip install git+https://github.com/charlesneimog/py4pd-upic`.
4. Restart Pure Data.
5. Create a new object `py4pd -lib upic`.

All the objects must be avaiable to use now.

