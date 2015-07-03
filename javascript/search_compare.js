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
/*global document:true*/

// -------------
//   CONSTANTS
// -------------

// -------------
//    OBJECTS
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
    },
    "score": {
      "protein_score": document.getElementsByName("min_protein_score")[0],
      "peptide_score": document.getElementsByName("min_peptide_score")[0],
      "protein_ev": document.getElementsByName("max_protein_evalue")[0],
      "peptide_ev": document.getElementsByName("max_peptide_evalue")[0]
    },
    "raw": {
      "raw_type": document.getElementsByName("raw_type")[0],
      "quantitation": document.getElementsByName("quan_type")[0],
      "median": document.getElementsByName("rep_q_median")[0],
      "iqr": document.getElementsByName("rep_q_iqr")[0],
      "mean": document.getElementsByName("rep_q_mean")[0],
      "mean_val": document.getElementsByName("rep_q_n_sdv")[0],
      "std_dev": document.getElementsByName("rep_q_stdev")[0],
      "num": document.getElementsByName("rep_q_num")[0],
      "intensity": document.getElementsByName("rep_intensity")[0],
      "int_threshold": document.getElementsByName("intensity_threshold")[0],
      "resolution": document.getElementsByName("rep_resolution")[0],
      "int_cs": document.getElementsByName("rep_cs_intensity")[0],
      "lh_int": document.getElementsByName("rep_a_lh_int")[0],
      "area": document.getElementsByName("rep_area")[0],
      "cs_area": document.getElementsByName("rep_cs_area")[0],
      "cs_threshold": document.getElementsByName("area_threshold")[0],
      "lh_area": document.getElementsByName("rep_a_lh_area")[0],
      "snr": document.getElementsByName("rep_snr")[0],
      "snr_threshold": document.getElementsByName("snr_threshold")[0],
      "noise_mean": document.getElementsByName("rep_n_mean")[0],
      "noise_sd": document.getElementsByName("rep_n_stdev")[0],
      "rt_int_min": document.getElementsByName("rt_int_start")[0],
      "rt_int_max": document.getElementsByName("rt_int_end")[0],
      "resolution_val": document.getElementsByName("resolution")[0],
      "13C_perct": document.getElementsByName("percent_C13")[0],
      "15N_perct": document.getElementsByName("percent_N15")[0],
      "18O_perct": document.getElementsByName("percent_O18")[0],
      "purity_corr": document.getElementsByName("purity_correction")[0],
      "ionWindow": document.getElementsByName("reporter_ion_window")[0]
    },
    "columns": {
    }
  };

  // -------------
  //     CORE
  // -------------

  // sets the constant values for the site
  this.constants = function() {
    /*
     * This function sets the default constants for the Batch Tag Search.
     * These values are typically those that never change, and therefore
     * should never be toggled.
    */
    // Define key values
    var data = {
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

  // -------------
  //     UTILS
  // -------------

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
      for (var i = 0; i < attr.length; i++) {
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
    for (var i = 0; i < attr.length; i++) {
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
    for (var i = 0; i < values.length; i++) {
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
//   FUNCTIONS
// -------------

var searchCompareFunctions = {  //eslint-disable-line no-unused-vars, no-undef
};

var searchCompare = new SearchCompare();
// searchCompare.constants();
