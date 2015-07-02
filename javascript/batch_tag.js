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
 * Automated scripts to configure and edit "Batch Tag" and "Batch Tag Web"
 * settings on Protein Prospector. Can be configured into a TamperMonkey
 * script.
 *
 * This adds a HTML DOM "settings" element into the Protein Prospector
 * Batch Tag site, enabling customizing elements upon selection.
*/

// ESLint settings
/*eslint no-underscore-dangle:0, curly: 2*/
/*global location b:true, document b:true, DEFAULT_MODS b:true*/

// -------------
//   CONSTANTS
// -------------

var DEFAULT_MODS = [    //eslint-disable-line no-unused-vars, no-undef
  /*
   * Sets the default mod configurations for standard searches.
   * Provides a baseline for configurations to select in the DOM select
   * elemeents.
  */
  "Acetyl (Protein N-term)",
  "Acetyl+Oxidation (Protein N-term M)",
  "Deamidated (N)",
  "Gln->pyro-Glu (N-term Q)",
  "Met-loss (Protein N-term M)",
  "Met-loss+Acetyl (Protein N-term M)",
  "Oxidation (M)"
];

var DSSO = [
  /*
   * Sets the default mod configurations for DSSO searches.
  */
  "XL:A-Alkene (Protein N-term)",
  "XL:A-Alkene (Uncleaved K)",
  "XL:A-Sulfenic (Protein N-term)",
  "XL:A-Sulfenic (Uncleaved K)",
  "XL:A-Thiol(Unsaturated) (Protein N-term)",
  "XL:A-Thiol(Unsaturated) (Uncleaved K)"
];

var SILAC_13C6K = [
  /*
   * Sets the default mod configurations for MS/MS SILAC 13C(6) searches.
  */
  "Label:13C(6)15N(2) (K)"
];

var SILAC_13C6K_DSSO = [
  /*
   * Sets the default mod configurations for DSSO SILAC 13C(6) 15N(2) searches.
  */
  "Label:13C(6)15N(2)+XL:A-Alkene (Uncleaved K)",
  "Label:13C(6)15N(2)+XL:A-Sulfenic (Uncleaved K)",
  "Label:13C(6)15N(2)+XL:A-Thiol (Uncleaved K)"
];

// -------------
//   FUNCTIONS
// -------------

var defaultSettings = function() {
  /*
   * Reloads current webpage to reset settings upon loading
  */
  "use strict";
  location.reload();
};

var ms2Standard = function(cls) {
  /*
   * Sets the default MS/MS search settings, assuming full Carbamidomethyl
   * incorporation.
  */
  "use strict";
  // Set the constant mods
  cls.setConstantMods(["Carbamidomethyl (C)"]);
  cls.setVariableMods(DEFAULT_MODS);
  // Set the Protease/Missed Cleavage stuff
  cls.setProtease(["missed"], [2]);
  cls.setMaxMods(2);
};

var ms2Silac = function(cls) {
  /*
   * Sets the MS/MS search settings with 13C(6) 15N(2)-K SILAC labeling.
  */
  "use strict";
  // Call standard MS/MS settings
  ms2Standard(cls);
  cls.setVariableMods(SILAC_13C6K, false);
};

var dssoStandard = function(cls) {
  /*
   * Sets the search settings for DSSO (XLMS).
  */
  "use strict";
  // Set the constant mods
  cls.setConstantMods(["Carbamidomethyl (C)"]);
  cls.setVariableMods(DEFAULT_MODS.concat(DSSO));
  // Set the Protease/Missed Cleavage stuff
  cls.setProtease(["missed"], [4]);
  cls.setMaxMods(4);
};

var silacDsso = function(cls) {
  /*
   * Sets the search settings for DSSO (XLMS) with 13C(6) 15N(2)-K
   * SILAC labeling.
  */
  "use strict";
  // Call standard DSSO settings
  dssoStandard(cls);
  var mods = DEFAULT_MODS.concat(SILAC_13C6K).concat(SILAC_13C6K_DSSO);
  cls.setVariableMods(mods);
};

var backbone15NDsso = function(cls) {
  /*
   * Sets the search settings for DSSO (XLMS) with ubiquitous
   * backbone 15N labeling.
  */
  "use strict";
  // Call standard DSSO settings
  dssoStandard(cls);
};

var trypsin = function(cls) {
  /*
   * Sets the default configurations for Proteins digested with trypsin.
  */
  "use strict";
  cls.setProtease(["enzyme", "nonSpecific"],
                  ["Trypsin", "at 0 termini"]);
};

// -------------
//  DOM STORAGE
// -------------

// Create core Batch Tag class
function BatchTag() {
  "use strict";
  /*
   * Contains the core DOM elements of the BatchTag website stored within the
   * DATA subheadings.
   *
   * Private methods are then defined to access individual members, and then
   * custom settings these elements can be done via setValue() or various
   * other functions, along with pre-defined settings such as "constants".
  */
  // -------------
  //     DATA
  // -------------
  // grab our databases
  this._database = {
    "ds": document.getElementsByName("database")[0],
    "dna": document.getElementsByName("dna_frame_translation")[0],
    "user": document.getElementsByName( "user_protein_sequence")[0],
    "species": document.getElementsByName("species")[0],
    "nTermLim": document.getElementsByName("n_term_aa_limit")[0]
  };

  // grab protease conditions
  this._protease = {
    "enzyme": document.getElementsByName("enzyme")[0],
    "nonSpecific": document.getElementsByName("allow_non_specific")[0],
    "missed": document.getElementsByName("missed_cleavages")[0]
  };

  // grab file name identifiers
  this._outputFilename = document.getElementsByName("output_filename")[0];

  // grab our mod lists
  this._mods = {
    "const": document.getElementsByName("const_mod")[0],
    "variable": document.getElementsByName("msms_mod_AA")[0],
    // Variable mod labels
    "mod_1_label": document.getElementsByName("mod_1_label")[0],
    "mod_2_label": document.getElementsByName("mod_2_label")[0],
    "mod_3_label": document.getElementsByName("mod_3_label")[0],
    "mod_4_label": document.getElementsByName("mod_4_label")[0],
    "mod_5_label": document.getElementsByName("mod_5_label")[0],
    "mod_6_label": document.getElementsByName("mod_6_label")[0],
    // Variable Mod Specificty
    "mod_1_specificity": document.getElementsByName("mod_1_specificity")[0],
    "mod_2_specificity": document.getElementsByName("mod_2_specificity")[0],
    "mod_3_specificity": document.getElementsByName("mod_3_specificity")[0],
    "mod_4_specificity": document.getElementsByName("mod_4_specificity")[0],
    "mod_5_specificity": document.getElementsByName("mod_5_specificity")[0],
    "mod_6_specificity": document.getElementsByName("mod_6_specificity")[0],
    // Variable Mod Composition
    "mod_1_composition": document.getElementsByName("mod_1_composition")[0],
    "mod_2_composition": document.getElementsByName("mod_2_composition")[0],
    "mod_3_composition": document.getElementsByName("mod_3_composition")[0],
    "mod_4_composition": document.getElementsByName("mod_4_composition")[0],
    "mod_5_composition": document.getElementsByName("mod_5_composition")[0],
    "mod_6_composition": document.getElementsByName("mod_6_composition")[0],
    // Variable Mod Exact Mass
    "mod_1_accurate_mass": document.getElementsByName(
      "mod_1_accurate_mass")[0],
    "mod_2_accurate_mass": document.getElementsByName(
      "mod_2_accurate_mass")[0],
    "mod_3_accurate_mass": document.getElementsByName(
      "mod_3_accurate_mass")[0],
    "mod_4_accurate_mass": document.getElementsByName(
      "mod_4_accurate_mass")[0],
    "mod_5_accurate_mass": document.getElementsByName(
      "mod_5_accurate_mass")[0],
    "mod_6_accurate_mass": document.getElementsByName(
      "mod_6_accurate_mass")[0],
    "maxMods": document.getElementsByName("msms_max_modifications")[0],
    "msms_max_peptide_permutations": document.getElementsByName(
      "msms_max_peptide_permutations")[0]
  };

  // grab our mass mod lists
  this._massMods = {
    "type": document.getElementsByName("mod_range_type")[0],
    "start": document.getElementsByName("mod_start_nominal")[0],
    "end": document.getElementsByName("mod_end_nominal")[0],
    "defect": document.getElementsByName("mod_defect")[0],
    "mod_comp_ion": document.getElementsByName("mod_comp_ion"),
    "nTermType": document.getElementsByName("mod_n_term_type")[0],
    "modNTerm": document.getElementsByName("mod_n_term")[0],
    "cTermType": document.getElementsByName("mod_c_term_type")[0],
    "modCTerm": document.getElementsByName("mod_c_term")[0],
    "uncleaved": document.getElementsByName("mod_uncleaved")[0],
    "neutralLoss": document.getElementsByName("mod_neutral_loss")[0]
  };

  // grab our crosslinking mod attributes
  this._crosslinking = {
    "searchType": document.getElementsByName("link_search_type")[0],
    "maxHits": document.getElementsByName("max_saved_tag_hits")[0]
  };

  // grab our link param attributes
  this._links = {
    "link_aa": document.getElementsByName("link_aa")[0],
    "bridge": document.getElementsByName("bridge_composition")[0]
  };

  // grab our matrix modification attributes
  this._matrix = {
    "boxes": document.getElementsByName("msms_search_type")
  };

  // grab our presearch parameters
  this._preSearch = {
    // Base element
    "element": document.getElementById("ejb_2")[0],
    "taxon": document.getElementsByName("species_names")[0],
    "low_mw": document.getElementsByName("msms_prot_low_mass")[0],
    "high_mw": document.getElementsByName("msms_prot_high_mass")[0],
    "full_mw_range": document.getElementsByName("msms_full_mw_range")[0],
    "low_pi": document.getElementsByName("low_pi")[0],
    "high_pi": document.getElementsByName("high_pi")[0],
    "full_pi_range": document.getElementsByName("full_pi_range")[0],
    "from_file": document.getElementsByName("results_from_file")[0],
    "prog": document.getElementsByName("input_program_name")[0],
    "input_name": document.getElementsByName("input_filename")[0],
    "remove": document.getElementsByName("species_remove")[0]
  };

  // Grab lower left objects
  this._other = {
    "mass": document.getElementsByName("parent_mass_convert")[0],
    "charge": document.getElementsByName("msms_precursor_charge_range")[0],
    "par_tol": document.getElementsByName("msms_parent_mass_tolerance")[0],
    "par_tol_units": document.getElementsByName(
      "msms_parent_mass_tolerance_units")[0],
    "frag_tol": document.getElementsByName("fragment_masses_tolerance")[0],
    "frag_tol_units": document.getElementsByName(
      "fragment_masses_tolerance_units")[0],
    "error": document.getElementsByName(
      "msms_parent_mass_systematic_error")[0]
  };

  // -------------
  //     CORE
  // -------------

  this.constants = function() {
    /*
     * This function sets the default constants for the Batch Tag Search.
     * These values are typically those that never change, and therefore
     * should never be toggled.
    */
    // Define key values
    var allValues = {
      "_database": {
        "nTermLim": ""
      },
      "_other": {
        "mass": "monoisotopic",
        "par_tol_units": "ppm",
        "frag_tol_units": "Da",
        "par_tol": 20,
        "frag_tol": 0.6,
        "error": 0
      },
      "_mods": {
        "mod_1_label": "",
        "mod_2_label": "",
        "mod_3_label": "",
        "mod_4_label": "",
        "mod_5_label": "",
        "mod_6_label": "",
        "mod_1_specificity": "",
        "mod_2_specificity": "",
        "mod_3_specificity": "",
        "mod_4_specificity": "",
        "mod_5_specificity": "",
        "mod_6_specificity": "",
        "mod_1_composition": "",
        "mod_2_composition": "",
        "mod_3_composition": "",
        "mod_4_composition": "",
        "mod_5_composition": "",
        "mod_6_composition": "",
        "mod_1_accurate_mass": "",
        "mod_2_accurate_mass": "",
        "mod_3_accurate_mass": "",
        "mod_4_accurate_mass": "",
        "mod_5_accurate_mass": "",
        "mod_6_accurate_mass": "",
        "msms_max_peptide_permutations": ""
      },
      "_massMods": {
        "type": "Da",
        "start": "-100",
        "end": "100",
        "defect": "0.00048",
        "mod_comp_ion": Array.apply(null, new Array(20)).map(
          Boolean.prototype.valueOf, false),
        "nTermType": "Peptide",
        "modNTerm": false,
        "cTermType": "Peptide",
        "modCTerm": false,
        "uncleaved": false,
        "neutralLoss": false
      },
      "_crosslinking": {
        "searchType": "No Link",
        "maxHits": "1000"
      },
      "_preSearch": {
        "low_mw": 1000,
        "high_mw": 125000,
        "full_mw_range": true,
        "low_pi": "3.0",
        "high_pi": "10.0",
        "full_pi_range": true,
        "from_file": false,
        "prog": "msfit",
        "input_name": "last_res",
        "remove": false
      },
      "_links": {
        "link_aa": "C->C",
        "bridge": ""
      },
      "_matrix": {
        "boxes": Array.apply(null, new Array(3)).map(
          Boolean.prototype.valueOf, false)
      }
    };
    // Automatically set values for all
    for (var tableName in allValues) {
      // grab table with attributes
      var table = allValues[tableName];
      for (var propertyName in table) {
        // Set all property values
        var attr = this[tableName][propertyName];
        var value = table[propertyName];
        this.setValue(attr, value);
      }
    }
  };

  this.setProtease = function(keys, values) {
    /*
     * this sets the protease attributes
     * Use:
     * BatchTag.setProtease(["missed"], [5]);
    */
    for (var i = 0; i < keys.length; i++) {
      // Grab key
      var key = keys[i];
      // Grab attr/value pair
      var attr = this._protease[key];
      var value = values[i];
      this.setValue(attr, value);
    }
  };

  this.setMaxMods = function(count) {
    /*
     * Sets the max mod counts
     * Use:
     * BatchTag.setMaxMods(4);
    */
    this.setValue(this._mods.maxMods, count);
  };

  this.setConstantMods = function(values, blank) {
    /*
     * This sets the constant mods by attribute name.
     * Use:
     * BatchTag.setConstantMods(["Cyano (C)", "Cys->Dha (C)"]);
    */
    // first need to blank all mods in that key
    var toBlank = blank || true;
    this._setMods(values, "const", toBlank);
  };

  this.setVariableMods = function(values, blank) {
    /*
     * This sets the variable mods by attribute name
     * BatchTag.setVariableMods([Cyano (C), "Cys->Dha (C)"]);
     * first need to blank all mods in that key
    */
    var blankMods = blank || true;
    this._setMods(values, "variable", blankMods);
  };

  this._setMods = function(values, key, blank) {
    /*
     * PRIVATE, full functionality can be called from
     * this.setVariableMods or this.setConstantMods
     *
     * Sets the current mods list, with keys and value
     * and grabs the attribute from the key to the stored mod type.
    */
    // pairs to select within the
    if (blank) {
      this._blankSelectBox(this._mods[key]);
    }
    // now need to set all the values
    this._setSelectMultiple(this._mods[key], values);
  };

  // -------------
  //  BLANK UTILS
  // -------------

  this._blankSelectBox = function(attr) {
    /*
     * Blanks all entries within the DOM select element
     * Only, of course, works with select-multiple DOM elements.
     *
     * Blanks from a given DOM element attr.
    */
    // blanks
    for (var i = 0; i < attr.length; i++) {
      attr[i].selected = false;
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

  // This toggles the selection for a given HTML "select-one" box
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

  // This sets the selection for a given HTML "select-multiple" box
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

  // This sets the HTML text value for a given attribute
  this._setTextValue = function(attr, value) {
    attr.value = value;
  };

  // This sets the HTML checkstate for a checkbox
  this._setCheckBox = function(attr, value) {
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

var batchTag = new BatchTag();
batchTag.constants();

// -------------
//   CREATE
// NEW ELEMENT
// -------------

var functions = {
  "Default": defaultSettings,
  "MS/MS -- Standard": function() {
    "use strict";
    ms2Standard(batchTag);
  },
  "MS/MS -- SILAC 13C(6) 15N(2) K": function() {
    "use strict";
    ms2Silac(batchTag);
  },
  "XLMS -- DSSO Standard": function() {
    "use strict";
    dssoStandard(batchTag);
  },
  "XLMS -- DSSO SILAC 13C(6) 15N(2) K": function() {
    "use strict";
    silacDsso(batchTag);
  },
  "XLMS -- 15N Backbone DSSO": function() {
    "use strict";
    backbone15NDsso(batchTag);
  },
  "Protease -- Trypsin": function() {
    "use strict";
    trypsin(batchTag);
  }
};

function InjectOptions(elementName) {
  "use strict";
  /*
   * Adds a DOM select-one element to the Batch Tag Search page,
   * which contains configurable elements to set default parameters.
   *
   * Specifically adds the entry after elementName, which it grabs the
   * first entry from the DOM with that name.
  */

  // -------------
  // NEW ELEMENTS
  // -------------

  this._newOptions = function(newElement, textNodeName) {
    /*
     * Creates a new DOM element for configurable user options.
    */
    var presetOptions = document.createElement(newElement);
    presetOptions.appendChild(document.createTextNode(textNodeName));
    presetOptions.appendChild(document.createElement("br"));

    return presetOptions;
  };

  this._addSelect = function() {
    /*
     * Adds a new select element to the DOM and adds an eventListen for
     * signal changes.
    */
    var newSelect = document.createElement("select");
    // Need to set, since inside the event listener, will be missing
    var this_ = this;
    newSelect.addEventListener("change", function () {
      // Grab the currently selected item
      var propertyName = this_._getSelected(newSelect).innerHTML;
      // Grab element function and call
      var func = functions[propertyName];
      func();
    });

    return newSelect;
  };

  this._addOptions = function(configurations, select) {
    /*
     * Adds user configuration settings to a widget from a function list
     *
     * Converts the configuration list to a series of bound options
     * in a select DOM element.
    */

    // Populate new element -- Init counter
    var i = 0;
    for (var propertyName in functions) {
      // Create option
      var opt = document.createElement("option");
      opt.value = i;
      opt.innerHTML = propertyName;
      select.appendChild(opt);
      i++;
    }
    return;
  };

  // -------------
  //     UTILS
  // -------------

  this._getSelected = function(ele) {
    /*
     * Grabs the currently selected element from a DOM element
     * if the DOM element is ele.type === "select-one".
    */
    // Iterate over entries in box
    for (var i = 0; i < ele.length; i++) {
      // Check if default value is desired value
      if (ele[i].selected === true) {
        return ele[i];
      }
    }
  };

  // -------------
  //     INIT
  // -------------

  this.init = function () {
    /*
     * Initializes the core widget list
    */
    // Create a new element
    this.presetOptions = this._newOptions("presetOptions", "Custom Lists");
    var newSelect = this._addSelect();
    this.presetOptions.appendChild(newSelect);
    // Grab parent"s location
    var ele = document.getElementsByName(elementName)[0];
    var parent = ele.offsetParent;
    // Add new separator and add element
    for (var i = 0; i < 5; i++) {
      parent.appendChild(document.createElement("br"));
    }
    // Now need to add the options and add to widget
    this._addOptions(functions, newSelect);
    parent.appendChild(this.presetOptions);
  };
}

// -------------
//   INJECT
// NEW ELEMENT
// -------------

var inject = new InjectOptions("parent_mass_convert");
inject.init();
