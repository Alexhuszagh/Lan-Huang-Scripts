/* Copyright (C) 2015 Alex Huszagh <<github.com/Alexhuszagh>>

xlDiscoverer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This xlDiscoverer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this xlDiscoverer.  If not, see <http://www.gnu.org/licenses/>.
*/

// -------------
//     USE
// -------------

/*
Automated scripts to configure and edit "Batch Tag" and "Batch Tag Web"
settings.

This adds a HTML DOM "settings" element into the Protein Prospector Batch Tag
site, enabling cust selectable elements.
*/

// -------------
//   CONSTANTS
// -------------

var DEFAULT_MODS = [
  'Acetyl (Protein N-term)',
  'Acetyl+Oxidation (Protein N-term M)',
  'Deamidated (N)',
  'Gln->pyro-Glu (N-term Q)',
  'Met-loss (Protein N-term M)',
  'Met-loss+Acetyl (Protein N-term M)',
  'Oxidation (M)'
];

var DSSO = [
  'XL:A-Alkene (Protein N-term)',
  'XL:A-Alkene (Uncleaved K)',
  'XL:A-Sulfenic (Protein N-term)',
  'XL:A-Sulfenic (Uncleaved K)',
  'XL:A-Thiol(Unsaturated) (Protein N-term)',
  'XL:A-Thiol(Unsaturated) (Uncleaved K)'
];

// -------------
//   FUNCTIONS
// -------------

var defaultSettings = function() {
}

var ms2Standard = function() {
  // Set the constant mods
  batch_tag.set_constant_mods(['Carbamidomethyl (C)']);
  batch_tag.set_variable_mods(DEFAULT_MODS);
  // Set the Protease/Missed Cleavage stuff
  batch_tag.set_protease(["missed"], [2]);
  batch_tag.set_max_mods(2);
}

var dssoStandard = function() {
  // Set the constant mods
  batch_tag.set_constant_mods(['Carbamidomethyl (C)']);
  batch_tag.set_variable_mods(DEFAULT_MODS.concat(DSSO));
  // Set the Protease/Missed Cleavage stuff
  batch_tag.set_protease(["missed"], [4]);
  batch_tag.set_max_mods(4);
}

var trypsin = function() {
  batch_tag.set_protease(["enzyme", "nonSpecific"],
                         ["Trypsin", "at 0 termini"])
}

var functions = {
  "Default": defaultSettings,
  "MS2 Standard": ms2Standard,
  "DSSO Standard": dssoStandard,
  "Trypsin": trypsin
}

// -------------
//    OBJECTS
// -------------

// Create core Batch Tag class
function BatchTag() {

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
  }

  // grab protease conditions
  this._protease = {
    "enzyme": document.getElementsByName("enzyme")[0],
    "nonSpecific": document.getElementsByName("allow_non_specific")[0],
    "missed": document.getElementsByName("missed_cleavages")[0]
  }

  // grab file name identifiers
  this._output_filename = document.getElementsByName("output_filename")[0];

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
    "max_mods": document.getElementsByName("msms_max_modifications")[0],
    "msms_max_peptide_permutations": document.getElementsByName(
      "msms_max_peptide_permutations")[0],
  }

  // grab our mass mod lists
  this._mass_mods = {
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
  }

  // grab our crosslinking mod attributes
  this._crosslinking = {
    "searchType": document.getElementsByName("link_search_type")[0],
    "maxHits": document.getElementsByName("max_saved_tag_hits")[0]
  }

  // grab our link param attributes
  this._links = {
    "link_aa": document.getElementsByName("link_aa")[0],
    "bridge": document.getElementsByName("bridge_composition")[0]
  }

  // grab our matrix modification attributes
  this._matrix = {
    "boxes": document.getElementsByName("msms_search_type"),
  }

  // grab our presearch parameters
  this._pre_search = {
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
  }

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
  }

  // -------------
  //     CORE
  // -------------

  // sets the constant values for the site
  this.constants = function() {
    // This function sets the constants for the Batch Tag Search
    // These values should never change

    // Define key values
    var allValues = {
      "_database": {
        "nTermLim": "",
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
      "_mass_mods": {
        "type": "Da",
        "start": "-100",
        "end": "100",
        "defect": "0.00048",
        "mod_comp_ion": Array.apply(null, new Array(20)).map(
          Boolean.prototype.valueOf,false),
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
      "_pre_search": {
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
          Boolean.prototype.valueOf,false)
      }
    }
    // Automatically set values for all
    for (tableName in allValues) {
      // grab table with attributes
      table = allValues[tableName];
      for (propertyName in table) {
        // Set all property values
        var attr = this[tableName][propertyName];
        var value = table[propertyName];
        this.set_value(attr, value);
      }
    }
  }

  // this sets the protease attributes
  // Use:
  // BatchTag.set_protease(["missed"], [5]);
  this.set_protease = function(keys, values) {
    for (var i = 0; i < keys.length; i++) {
      // Grab key
      var key = keys[i];
      // Grab attr/value pair
      var attr = this._protease[key];
      var value = values[i];
      this.set_value(attr, value);
    }
  }

  // Sets the max mod counts
  // Use:
  // BatchTag.set_max_mods(4);
  this.set_max_mods = function(count) {
    this.set_value(this._mods['max_mods'], count);
  }

  // this sets the constant mods by attribute name
  // Use:
  // BatchTag.set_constant_mods(['Cyano (C)', 'Cys->Dha (C)']);
  this.set_constant_mods = function(values) {
    this._set_mods(values, "const")
  }

  // this sets the variable mods by attribute name
  // BatchTag.set_variable_mods(['Cyano (C)', 'Cys->Dha (C)']);
  this.set_variable_mods = function(values) {
    this._set_mods(values, "variable")
  }

  this._set_mods = function(values, key) {
    // first need to blank all mods in that key
    this._blank_select_box(this._mods[key])

    // now need to set all the values
    this._set_select_multiple(this._mods[key], values)
  }

  // -------------
  //  BLANK UTILS
  // -------------

  this._blank_select_box = function(attr) {
    // blanks
    for (var i = 0; i < attr.length; i++) {
      attr[i].selected = false;
    }
  }

  // -------------
  //     UTILS
  // -------------

  // finds the HTML object type and sets the value
  this.set_value = function(attr, value) {
    if (attr.type === "select-one") {
     this._set_select_box(attr, value);
    }
    else if (attr.type === "text") {
      this._set_text_value(attr, value);
    }
    else if (attr.type === "checkbox") {
      this._set_checkbox(attr, value);
    }
    else if (typeof attr.length == 'number'
             && typeof attr.item == 'function')
    {
      for (var i = 0; i < attr.length; i++) {
        var tmpAttr = attr[i];
        var tmpValue = value[i];
        this.set_value(tmpAttr, tmpValue);
      }
      // this._set_checkbox(attr, value)
    }
  }

  // This toggles the selection for a given HTML "select-one" box
  this._set_select_box = function(attr, value) {
    // Iterate over entries in box
    for (var i = 0; i < attr.length; i++) {
      // Check if default value is desired value
      if (attr[i].value == value) {
        attr[i].selected = true;
      }
    }
  }

  // This sets the selection for a given HTML "select-multiple" box
  this._set_select_multiple = function(attr, values) {
    // Iterate over values and call this._set_select_box()
    for (var i = 0; i < values.length; i++) {
      // All the options are listed 0->6, need to check for numeric operties
      var value = values[i];
      this._set_select_box(attr, value)
    }
  }

  // This sets the HTML text value for a given attribute
  this._set_text_value = function(attr, value) {
    attr.value = value;
  }

  // This sets the HTML checkstate for a checkbox
  this._set_checkbox = function(attr, value) {
    if (value) {
      attr.checked = true;
    }
    else {
      attr.checked = false;
    }
  }
}

// Injects an option list onto the webpage
function InjectOptions() {

  // -------------
  //     UTILS
  // -------------

  // This gets the currently selected item from a "select-one" element.
  this._get_selected = function(attr) {
    // Iterate over entries in box
    for (var i = 0; i < attr.length; i++) {
      // Check if default value is desired value
      if (attr[i].selected == true) {
        // return attr[i]
        return attr[i]
      }
    }
  }
  // Inject a new element with preset options
  // document.c
  //document.appendChild(this.newElement);

  // -------------
  //   NEW ELE
  // -------------

  // Create a new element
  this.presetOptions = document.createElement("presetOptions");
  this.presetOptions.appendChild(document.createTextNode("Custom Lists"));
  this.presetOptions.appendChild(document.createElement("br"));
  var newSelect = document.createElement('select');
  // Need to set, since inside the event listener, will be missing
  var this_ = this;
  newSelect.addEventListener("change", function (e) {
    // Grab the currently selected item
    var propertyName = this_._get_selected(newSelect).innerHTML;
    // Grab element function and call
    var func = functions[propertyName];
    func();
  });
  this.presetOptions.appendChild(newSelect);
  // Grab parent's location
  var ele = document.getElementsByName("parent_mass_convert")[0];
  var parent = ele.offsetParent;
  // Add new separator and add element
  for (var i = 0; i < 5; i++) {
    parent.appendChild(document.createElement("br"));
  }
  parent.appendChild(this.presetOptions);
  // Populate new element
  for (var propertyName in functions) {
    // Create option
    var opt = document.createElement("option");
    opt.value = i;
    opt.innerHTML = propertyName;
    newSelect.appendChild(opt);
  }
}

var batch_tag = new BatchTag();
var inject = new InjectOptions();
batch_tag.constants();
