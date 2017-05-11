# pbsf2
Pokémon Box SoundFont 2 generator

### Prerequisites
* Python 3
* <a href="https://github.com/freepats/tools/tree/master/sfubar-9">sfubar</a>

### Usage
Use pokemon_sf2.py to generate sfubar-compatible soundfont configuration files, then pass them to sfubar with the <code>--txt2sf</code> conversion switch.

You can drag-and-drop .wt files onto the .py script since it only takes one argument.

**Note**: The respective .pcm files must be in the same folder as the .wt files.

**Note**: When the script has finished generating samples and the soundfont descriptor, do not move or rename any files! Pass the .txt file directly to sfubar.
