# Lan Huang Scripts
General, short, command-line scripts for the Lan Huang Laboratory (written mainly in Python). Python was chosen for its cross-platform and emphasis on [duck-typing](https://en.wikipedia.org/wiki/Duck_typing) and readability, making simple, powerful code.

These scripts should be fully supported on any Python-supported operating system, using any Python 2.7.x or Python 3.4.x version.

**Table of Contents**

- [Utilities](#utilities)
  - [Python](#python)
    - [File Fixing Scripts](#file-fixing-scripts)
    - [Automated Data Analysis](#automated-data-analysis)
  - [JavaScript](#javascript)
    - [Protein Prospector](#protein-prospector)

## Utilities

### Python

#### File Fixing Scripts

> **Goals**
> Use [Trans-Proteomic Pipeline](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3017125/) file standards to fix lab-used scripts to improve their implementation. This is because the lab-used scripts may have better performance, better algorithms, but suffer from not being part of a mainstream, maintained software package.

1. [Fix Pava](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/python/fix_pava.py)
    * Corrects mis-assigned charge states due to algorithm differences between the PAVA Raw Distiller and the MSConvert TPP-compatible MGF extractor and writes them back to a copy of the PAVA file.
2. [Fix Fusion](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/python/fix_pava.py)
    * Corrects missing data from the PAVA Raw Distiller with newer Thermo Raw file formats, by using scan data from TPP-compatible MGF files extracted with MSConvert,

### Automated Data Analysis

1. [Check Coverage](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/python/check_coverage.py)
    * Checks the sequence coverage for a list of UniProt IDs given by the user in a list of files supplied for the user. These can have optional labels, if desired. It then outputs the sequence coverage of each peptide using '+'/' ', in a format similar to ClustalW.

### JavaScript

#### Protein Prospector

1. [Batch Tag](https://github.com/Alexhuszagh/Lan-Huang-Scripts/blob/master/javascript/batch_tag.js)
    * Injects an HTML Select Form Attribute into the Protein Prospector webpage, allowing users to toggle between common settings in order to rapidly select user configurations or output report formats.
