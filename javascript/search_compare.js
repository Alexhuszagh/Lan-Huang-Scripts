/* Copyright (C) 2015 Alex Huszagh <<github.com/Alexhuszagh>>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

// -------------
//     USE
// -------------

/*
 * Automated scripts to configure and edit "Search Compare" settings
 * on Protein Prospector. Can be configured into a TamperMonkey script.
 *
 * This locally stores the settings for the Protein Prospector Batch Tag
 * site, so the user can then configure the settings via inject.js.
*/

// ESLint settings
/*eslint no-underscore-dangle:0, curly: 2*/
/*global document location:true*/

// -------------
//   FUNCTIONS
// -------------

var defaultSettingsSearch = function() {
  /*
   * Reloads current webpage to reset settings upon loading
  */
  "use strict";
  location.reload();
};

var noQuantitationSearch = function(cls) {
  /*
   * Turns off all quantitative aspects in the Protein Prospector
   * search settings
  */
  "use strict";
  cls.blankQuantitation();
};

var quantitationSearch = function(cls, label) {
  /*
   * Sets the ideal quantitation settings from a given list of labels.
  */
  "use strict";
  // Set the quantitation on
  cls.setQuantitation();
  // Turn on the label
  cls.setValue(cls._data.raw.quantitation, label);
  // Turn on HTML
  cls.setReportSettings(["format"], ["HTML"]);
};

var ms2BaseSearch = function(cls) {
  /*
   * Sets the minimal MS/MS search settings.
  */
  "use strict";
  // Set the overall scores
  cls.setScores(["proteinScore", "peptideScore", "proteinEv", "peptideEv"],
                ["22.0", "15.0", "0.01", "0.05"]);
  // Set it to keep only one peptide of replicates
  cls.setReportSettings(["format", "report", "sort1", "sort2", "minBestDiscr",
                         "replicates"],
                        ["Tab delimited text", "Protein",
                         "Expectation Value", "", "0.0", "Best Peptide Only"]);
};

var ms2StandardSearch = function(cls) {
  /*
   * Sets the default MS/MS search settings, assuming high score thresholds.
  */
  "use strict";
  // Set general basis for MS/MS searches
  ms2BaseSearch(cls);
  // Set the used columns
  cls.blankColumns();
  cls.setColumns(["mz", "charge", "error", "score", "eVal", "bestEv",
                  "numInDb", "coverage", "bestDiscrScore", "dbPeptide",
                  "time", "msmsInfo", "start", "number", "accession",
                  "mw", "species", "name", "links"]);
  // Set mods to all Mods 1 Column
  cls.setValue(cls._data.columns.modReporting, "All Mods (1 Column)");
  // Turn off any quantitation that may be selected
  noQuantitationSearch(cls);
};

var ms213C6QuantitationSearch = function(cls) {
  /*
   * Turns on the commonly used quantitation searches for a given Protein
   * Prospector output.
  */
  "use strict";
  ms2BaseSearch(cls);
  // Turn off any quantitation that may be selected
  quantitationSearch(cls, "Label:13C 15N (K)");
};

var falseDiscoveryRate = function(cls) {
  /*
   * Sets the base settings for finding out the MS false discovery rate,
   * or FDR.
  */
  "use strict";
  // Set the overall scores
  cls.setScores(["proteinScore", "peptideScore", "proteinEv", "peptideEv"],
                ["10.0", "10.0", "10000.0", "1.0"]);
  // Set it to keep only one peptide of replicates
  cls.setReportSettings(["format", "report", "sort1", "sort2", "minBestDiscr",
                         "replicates"],
                        ["HTML", "False Positive Rate",
                         "Expectation Value", "", "-10.0", "Keep Replicates"]);
  // Set the used columns
  cls.blankColumns();
  cls.setColumns(["mz", "charge", "error", "score", "eVal", "bestEv",
                  "numInDb", "coverage", "bestDiscrScore", "dbPeptide",
                  "time", "msmsInfo", "start", "number", "accession",
                  "mw", "species", "name", "links"]);
  // Set mods to all Mods 1 Column
  cls.setValue(cls._data.columns.modReporting, "All Mods (1 Column)");
  // Turn off any quantitation that may be selected
  noQuantitationSearch(cls);
};

var ms3BaseSearch = function(cls) {
  /*
   * Sets the minimal XLMS search settings, assuming high score thresholds.
  */
  "use strict";
  // Set the overall scores
  cls.setScores(["proteinScore", "peptideScore", "proteinEv", "peptideEv"],
                ["1.0", "1.0", "1.0", "1.0"]);
  // Set it to keep only one peptide of replicates
  cls.setReportSettings(["format", "report", "sort1", "sort2", "minBestDiscr",
                         "replicates"],
                        ["Tab delimited text", "Peptide",
                         "Expectation Value", "", "0.0", "Keep Replicates"]);
};

var ms3StandardSearch = function(cls) {
  /*
   * Sets the default XLMS search settings, assuming high score thresholds.
  */
  "use strict";
  // Set general basis for XLMS searches
  ms3BaseSearch(cls);
  // Set the used columns
  cls.blankColumns();
  cls.setColumns(["mz", "charge", "error", "score", "eVal", "dbPeptide",
                  "time", "msmsInfo", "start", "accession", "name"]);
  // Set mods to all Mods 1 Column
  cls.setValue(cls._data.columns.modReporting, "All Mods (1 Column)");
  // Turn off any quantitation that may be selected
  noQuantitationSearch(cls);
};

var minimalXlms = function(cls) {
  /*
   * Sets the minimal XLMS search settings for XL Discoverer.
  */
  "use strict";
  // Set general basis for XLMS searches
  ms3BaseSearch(cls);
  // Set the used columns
  cls.blankColumns();
  cls.setColumns(["mz", "charge", "error", "score", "eVal", "dbPeptide",
                  "time", "msmsInfo", "start", "accession", "name"]);
  // Set mods to all Mods 1 Column
  cls.setValue(cls._data.columns.modReporting, "All Mods (1 Column)");
  // Turn off any quantitation that may be selected
  noQuantitationSearch(cls);
};

// -------------
//  DOM STORAGE
// -------------

// Create core Batch Tag class
function SearchCompare() {
  "use strict";
  /*
   * Contains the core DOM elements of the SearchCompare website stored
   * within the DATA subheadings.
   *
   * Private methods are then defined to access individual members, and then
   * custom settings these elements can be done via setValue() or various
   * other functions, along with pre-defined settings such as "constants".
  */
  // -------------
  //     DATA
  // -------------
  // grab our databases
  this._data = {
    "report": {
      "format": document.getElementsByName("save_format")[0],
      "accessionNumbers": document.getElementsByName("accession_nums")[0],
      "preferredSpecies": document.getElementsByName("preferred_species")[0],
      "replicates": document.getElementsByName("peptide_filter")[0],
      "remove": document.getElementsByName("remove")[0],
      "multiSample": document.getElementsByName("multi_sample")[0],
      "spotFraction": document.getElementsByName("id_filter_list")[0],
      "bestDiscr": document.getElementsByName("best_disc_only")[0],
      "discrGraph": document.getElementsByName("disc_score_graph")[0],
      "report": document.getElementsByName("report_type")[0],
      "sort1": document.getElementsByName("sort_type")[0],
      "sort2": document.getElementsByName("sort_type_2")[0],
      "reportHomologous": document.getElementsByName(
        "report_homologous_proteins")[0],
      "unmatchedSpectra": document.getElementsByName("unmatched_spectra")[0],
      "saveSettings": document.getElementsByName("save_params")[0],
      "maxPkFilter": document.getElementsByName("msms_pk_filter")[0],
      "msmsMaxPeaks": document.getElementsByName("msms_max_peaks")[0],
      "maxReportHits": document.getElementsByName("msms_max_reported_hits")[0],
      "minBestDiscr": document.getElementsByName(
        "min_best_disc_score_ESI_ION_TRAP_low_res")[0]
    },
    "score": {
      // Protein and peptide scores
      "proteinScore": document.getElementsByName("min_protein_score")[0],
      "peptideScore": document.getElementsByName("min_peptide_score")[0],
      "proteinEv": document.getElementsByName("max_protein_evalue")[0],
      "peptideEv": document.getElementsByName("max_peptide_evalue")[0]
    },
    "raw": {
       // Raw user settings
      "rawType": document.getElementsByName("raw_type")[0],
      "quantitation": document.getElementsByName("quan_type")[0],
      "median": document.getElementsByName("rep_q_median")[0],
      "iqr": document.getElementsByName("rep_q_iqr")[0],
      "mean": document.getElementsByName("rep_q_mean")[0],
      "meanVal": document.getElementsByName("rep_q_n_sdv")[0],
      "stdDev": document.getElementsByName("rep_q_stdev")[0],
      "num": document.getElementsByName("rep_q_num")[0],
      "intensity": document.getElementsByName("rep_intensity")[0],
      "intThreshold": document.getElementsByName("intensity_threshold")[0],
      "resolution": document.getElementsByName("rep_resolution")[0],
      "intCs": document.getElementsByName("rep_cs_intensity")[0],
      "lhInt": document.getElementsByName("rep_a_lh_int")[0],
      "area": document.getElementsByName("rep_area")[0],
      "csArea": document.getElementsByName("rep_cs_area")[0],
      "csThreshold": document.getElementsByName("area_threshold")[0],
      "lhArea": document.getElementsByName("rep_a_lh_area")[0],
      "snr": document.getElementsByName("rep_snr")[0],
      "snrThreshold": document.getElementsByName("snr_threshold")[0],
      "noise_mean": document.getElementsByName("rep_n_mean")[0],
      "noiseSd": document.getElementsByName("rep_n_stdev")[0],
      "rtIntMin": document.getElementsByName("rt_int_start")[0],
      "rtIntMax": document.getElementsByName("rt_int_end")[0],
      "resolutionVal": document.getElementsByName("resolution")[0],
      "13CPerct": document.getElementsByName("percent_C13")[0],
      "15NPerct": document.getElementsByName("percent_N15")[0],
      "18OPerct": document.getElementsByName("percent_O18")[0],
      "purityCorr": document.getElementsByName("purity_correction")[0],
      "ionWindow": document.getElementsByName("reporter_ion_window")[0]
    },
    "columns": {
      "m_h": document.getElementsByName("report_m_plus_h")[0],
      "mz": document.getElementsByName("report_m_over_z")[0],
      "charge": document.getElementsByName("report_charge")[0],
      "mHCalc": document.getElementsByName("report_m_plus_h_calc")[0],
      "mZCalc": document.getElementsByName("report_m_over_z_calc")[0],
      "intensity": document.getElementsByName("report_intensity")[0],
      "error": document.getElementsByName("report_error")[0],
      "unmatched": document.getElementsByName("report_unmatched")[0],
      "num_peaks": document.getElementsByName("report_num_pks")[0],
      "rank": document.getElementsByName("report_rank")[0],
      "searchNum": document.getElementsByName("report_search_number")[0],
      "score": document.getElementsByName("report_score")[0],
      "scoreDiff": document.getElementsByName("report_score_diff")[0],
      "eVal": document.getElementsByName("report_expectation")[0],
      "pVal": document.getElementsByName("report_p_value")[0],
      "logP": document.getElementsByName("report_nlog_p_value")[0],
      "precursorNum": document.getElementsByName("report_num_precursor")[0],
      "gradient": document.getElementsByName("report_gradient")[0],
      "offset": document.getElementsByName("report_offset")[0],
      "discrScore": document.getElementsByName("report_disc_score")[0],
      "numInDb": document.getElementsByName("report_repeats")[0],
      "protScore": document.getElementsByName("report_prot_score")[0],
      "numUnique": document.getElementsByName("report_num_unique")[0],
      "peptideCount": document.getElementsByName("report_peptide_count")[0],
      "bestPepScore": document.getElementsByName("report_best_score")[0],
      "bestEv": document.getElementsByName("report_best_expect")[0],
      "coverage": document.getElementsByName("report_coverage")[0],
      "bestDiscrScore": document.getElementsByName(
        "report_best_disc_score")[0],
      "dbPeptide": document.getElementsByName("report_db_peptide")[0],
      "modReporting": document.getElementsByName("peptide_mod_type")[0],
      "proteinMods": document.getElementsByName("report_protein_mod")[0],
      "slipThres": document.getElementsByName("slip_threshold")[0],
      "massMods": document.getElementsByName("report_mass_mod")[0],
      "missedDleavages": document.getElementsByName(
        "report_missed_cleavages")[0],
      "time": document.getElementsByName("report_time")[0],
      "msmsInfo": document.getElementsByName("report_msms_info")[0],
      "length": document.getElementsByName("report_length")[0],
      "composition": document.getElementsByName("report_composition")[0],
      "start": document.getElementsByName("report_start_aa")[0],
      "end": document.getElementsByName("report_end_aa")[0],
      "prevAA": document.getElementsByName("report_previous_aa")[0],
      "nextAA": document.getElementsByName("report_next_aa")[0],
      "number": document.getElementsByName("report_number")[0],
      "accession": document.getElementsByName("report_accession")[0],
      "uniprot": document.getElementsByName("report_uniprot_id")[0],
      "geneName": document.getElementsByName("report_gene_name")[0],
      "protLength": document.getElementsByName("report_prot_len")[0],
      "mw": document.getElementsByName("report_mw")[0],
      "pi": document.getElementsByName("report_pi")[0],
      "species": document.getElementsByName("report_species")[0],
      "name": document.getElementsByName("report_name")[0],
      "links": document.getElementsByName("report_links")[0],
      "checkboxes": document.getElementsByName("report_checkboxes")[0]
    }
  };

  // -------------
  //     CORE
  // -------------

  this.constants = function() {
    /*
     * This function sets the default constants for the Search Compare.
     * These values are typically those that never change, and therefore
     * should never be toggled.
    */
    // Define key values
    var data = {
      "report": {
        "spotFraction": "",
        "multiSample": false,
        "remove": false,
        "reportHomologous": "Interesting",
        "unmatchedSpectra": false,
        "saveSettings": false,
        "maxPkFilter": "Max MSMS Pks",
        "msmsMaxPeaks": "",
        "maxReportHits": "",
        "bestDiscr": true,
        "discrGraph": true
      }
    };
    // Automatically set values for all
    for (var tableName in data) {
      // grab table with attributes
      var table = data[tableName];
      for (var propertyName in table) {
        // Set all property values
        var attr = this._data[tableName][propertyName];
        var value = table[propertyName];
        this.setValue(attr, value);
      }
    }
  };

  this.setScores = function(keys, values) {
    /*
     * This function sets the scores for the Search Compare report.
     * Use:
     * SearchCompare.setScores(["proteinScore"], ["22.0"]);
    */
    this._setIterables(keys, values, this._data.score);
  };

  this.setColumns = function(keys) {
    /*
     * This function sets the replicates for the Search Compare report.
     * Use:
     * SearchCompare.setColumns(["Keep Replicates"]);
    */
    for (var i = 0, len = keys.length; i < len; i++) {
      var key = keys[i];
      var attr = this._data.columns[key];
      this.setValue(attr, true);
    }
  };

  this.setReportSettings = function(keys, values) {
    /*
     * This function sets the report settings for the Search Compare report.
     * Use:
     * SearchCompare.setReportSettings(["format"], ["HTML"]);
    */
    this._setIterables(keys, values, this._data.report);
  };

  this.setQuantitation = function() {
    /*
     * Turns on the quantitation settings for the given Search
     * Compare report.
    */
    var keys = ["rawType", "mean", "meanVal", "stdDev", "intensity", "lhInt",
                "intThreshold", "csThreshold", "snrThreshold",
                "rtIntMin", "rtIntMax", "resolutionVal", "13CPerct",
                "15NPerct", "18OPerct", "ionWindow"];
    var values = ["Quantitation", true, "2.0", true, true, true, 0, 0, "10.0",
                  "-10.0", "30.0", "70000.0", 98, 98, 100, "0.4"];
    this._setIterables(keys, values, this._data.raw);
  };

  // -------------
  //  BLANK UTILS
  // -------------

  this.blankColumns = function() {
    /*
     * Blanks all entries within the this._data.columns for the checkBoxes
    */
    this._blankCheckBoxes(this._data.columns);
  };

  this.blankQuantitation = function() {
    /*
     * Undoes all the quantitation settings for the given Search
     * Compare report.
    */
    // Blank all checkboxes
    this._blankCheckBoxes(this._data.raw);
    // Turn all the other values back using iterables
    var keys = ["rawType", "quantitation", "meanVal", "intThreshold",
                "csThreshold", "snrThreshold", "rtIntMin", "rtIntMax",
                "resolutionVal", "13CPerct", "15NPerct", "18OPerct",
                "ionWindow"];
    var values = ["MS Precursor", "DTT_C 2H (C)", "2.0", 0, 0, "10.0", "-10.0",
                  "30.0", "70000.0", 98, 98, 100, "0.4"];
    this._setIterables(keys, values, this._data.raw);
  };

  this._blankCheckBoxes = function(holder) {
    /*
     * Blanks all checkBoxes within a data holder.
    */
    for (var propertyName in holder) {
      // Grab the DOM element and blank if checkbox
      var ele = holder[propertyName];
      if (ele.type === "checkbox") {
        ele.checked = false;
      }
    }
  };

  // -------------
  //     UTILS
  // -------------

  this._setIterables = function(keys, values, holder) {
    /*
     * This sets all values from a set of key/value iterables using the
     * holder to get the DOM elements from this.
    */
    for (var i = 0, len = keys.length; i < len; i++) {
      // Grab key
      var key = keys[i];
      // Grab attr/value pair
      var attr = holder[key];
      var value = values[i];
      this.setValue(attr, value);
    }
  };

  this.setValue = function(attr, value) {
    /*
     * Finds the HTML object type and sets the ELEMENT.value
     * ELEMENT.selected, or ELEMENT.checked state.
     *
     * Use: BatchTag.setValue(domCheckBox, false);
    */
    // DOM Select Elements
    if (attr.type === "select-one") {
     this._setSelectBox(attr, value);
    }
    // DOM Text Elements
    else if (attr.type === "text") {
      this._setTextValue(attr, value);
    }
    // DOM CheckBox Elements
    else if (attr.type === "checkbox") {
      this._setCheckBox(attr, value);
    }
    // DOM NodeList Elements
    // Uses duck-typing for IE compatability issues
    else if (typeof attr.length === "number"
             && typeof attr.item === "function")
    {
      for (var i = 0, len = attr.length; i < len; i++) {
        var tmpAttr = attr[i];
        var tmpValue = value[i];
        this.setValue(tmpAttr, tmpValue);
      }
      // this._setCheckBox(attr, value)
    }
  };

  this._setSelectBox = function(attr, value) {
    /*
     * Sets the selected elements in a given DOM select element..
     * If the DOM select element is select-one, only one value
     * should be passed, since each new selection overrides an old.
    */
    // Iterate over entries in box
    for (var i = 0, len = attr.length; i < len; i++) {
      // Check if default value is desired value
      if (attr[i].value == value) {   // eslint-disable-line eqeqeq
        attr[i].selected = true;
      }
    }
  };

  this._setSelectMultiple = function(attr, values) {
    /*
     * Iterates over all values and then changes the value's selection
     * in a given DOM select element.
    */
    // Iterate over values and call this._setSelectBox()
    for (var i = 0, len = values.length; i < len; i++) {
      // All the options are listed 0->6, need to check for numeric operties
      var value = values[i];
      this._setSelectBox(attr, value);
    }
  };

  this._setTextValue = function(attr, value) {
    /*
     * This sets the HTML text value for a given attribute
    */
    attr.value = value;
  };

  this._setCheckBox = function(attr, value) {
    /*
     * This sets the HTML checkstate for a checkbox
    */
    if (value) {
      attr.checked = true;
    }
    else {
      attr.checked = false;
    }
  };
}

// -------------
//     INIT
// -------------

// Grab the header for the form
var header = document.getElementsByClassName("form_name")[0];
var text = header.innerText || header.textContent;
var trimmed = text.trim();
// Check to see current webpage loaded
if (trimmed === "Search Compare") {
  /*
   * On initializing the SearchCompare features.
  */
  /*global searchCompare:true*/
  searchCompare = new SearchCompare();
  // searchCompare.constants();

  // -------------
  //   CREATE
  // NEW ELEMENT
  // -------------
  searchCompareFunctions = {  //eslint-disable-line no-unused-vars, no-undef
    "Default": defaultSettingsSearch,
    "MS/MS -- Standard": function() {
      "use strict";
      ms2StandardSearch(searchCompare);
    },
    "MS/MS -- 13C(6) 15N(2) Quantitation": function() {
      "use strict";
      ms213C6QuantitationSearch(searchCompare);
    },
    "XLMS -- Standard": function() {
      "use strict";
      ms3StandardSearch(searchCompare);
    },
    "False Discovery Rate": function() {
      "use strict";
      falseDiscoveryRate(searchCompare);
    },
    "XLMS -- Minimal Export": function() {
      "use strict";
      minimalXlms(searchCompare);
    }
  };
}
