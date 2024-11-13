# VSE-Audio-Exporter-Addon

[![Software License](https://img.shields.io/badge/license-GPL-brightgreen.svg?style=flat-square)](LICENSE.md)
<p>
    <a href="#table"><img alt="Blender"
            src="https://img.shields.io/badge/Blender-gray?logo=blender&style=flat-square" /></a>
</p>

### Audio Exporter
Streamline your audio export workflow within Blender's Video Sequence Editor (VSE). Export audio strips individually or as a single, combined file with extensive customizations. Choose from MP3, FLAC, AC3, or MP2 formats and set sample rates, bit rates, and speaker configurations (stereo, 5.1, or 7.1). Gain control over audio channel mapping with advanced speaker arrangements to suit both simple and surround sound projects.  
  
**Location:** Sequencer > Audio Export (Tab)

---

### Features

- **Customizable Export Options:** Choose between `Separate Files` and `Combined File` modes to match your export needs.
- **Channel Configurations and Speaker Mapping:** Supports stereo, 5.1, and 7.1 speaker arrangements with up to 8 channels that can be customized for each output.
- **File Naming and Path Management:** Automatically generates unique filenames to avoid overwriting, with an auto-numbering feature for batch exports.
- **Sample and Bit Rate Control:** Select sample rates and bit rates to match project requirements, including options for high-quality or compressed outputs.
- **Error Handling and Tooltips:** Provides informative messages and tooltips to help troubleshoot issues, such as invalid output paths or unselected audio strips.

---

### Release Notes - Version 1.0.0

- **Initial Release:**
  - Added support for exporting audio in MP3, FLAC, AC3, and MP2 formats.
  - Implemented `Separate Files` mode to export each selected audio strip individually, with unique filenames.
  - Added `Combined File` mode to combine selected audio strips into a single file.
  - Integrated speaker arrangement options (Stereo, 5.1 Surround, 7.1 Surround) for combined exports.
  - Configurable audio properties including sample rate, bit rate, and channel mapping.
  - Includes file path validation with error reporting.
  - Icons and tooltips for user-friendly navigation in the Audio Export tab.

---
