# Lan Huang Scripts
General, short, command-line scripts for the Lan Huang Laboratory (written mainly in Python). Python was chosen for its cross-platform and emphasis on [duck-typing](https://en.wikipedia.org/wiki/Duck_typing) and readability, making simple, powerful code.

**Table of Contents**

- [Utilities](#utilities)
  - [File Fixing Scripts](#file-fixing-scripts)

## Utilities

### File Fixing Scripts

> **Goals**
> Use [Trans-Proteomic Pipeline](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3017125/) file standards to fix lab-used scripts to improve their implementation. This is because the lab-used scripts may have better performance, better algorithms, but suffer from not being part of a mainstream, maintained software package.

1. [Fix Pava](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/fix_pava.py)
    * Corrects mis-assigned charge states due to algorithm differences between the PAVA Raw Distiller and the MSConvert TPP-compatible MGF extractor and writes them back to a copy of the PAVA file.
2. [Fix Fusion](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/fix_pava.py)
    * Corrects missing data from the PAVA Raw Distiller with newer Thermo Raw file formats, by using scan data from TPP-compatible MGF files extracted with MSConvert,
