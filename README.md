# pbsf2
Pokémon Box SoundFont 2 generator

### Prerequisites
* Python 3
* <a href="https://github.com/freepats/tools/tree/master/sfubar-9">sfubar</a>

### Usage
Pass a .wt file to *pbsf2.py* to generate *sfubar*-compatible soundfont configuration files (.txt). Pass the configuration files to *sfubar* using the <code>--txt2sf</code> conversion option to generate SF2 files.

You can drag-and-drop a .wt file onto the .py script since it only takes one argument.

**Note**: The respective .pcm files must be in the same folder as the .wt files.

**Note**: When the script has finished generating the samples and configuration files, do not move or rename any files! Pass the configuration files directly to *sfubar*.
