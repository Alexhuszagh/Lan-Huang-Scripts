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
 * Automated scripts to add DOM settings elements bound to functions into
 * a Protein Prospector page.. Can be configured into a TamperMonkey
 * script.
*/

// ESLint settings
/*eslint no-underscore-dangle:0, curly: 2*/
/*global location document:true*/

function InjectOptions(elementName, functions, spacer) {   //eslint-disable-line no-unused-vars
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
    presetOptions.appendChild(document.createElement(spacer));

    return presetOptions;
  };

  this._addSelect = function(configurations) {
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
      var func = configurations[propertyName];
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
    for (var propertyName in configurations) {
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
    for (var i = 0, len = ele.length; i < len; i++) {
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
    var newSelect = this._addSelect(functions);
    this.presetOptions.appendChild(newSelect);
    // Grab parent"s location
    var ele = document.getElementsByName(elementName)[0];
    var parent = ele.offsetParent;
    // Add new separator and add element
    for (var i = 0; i < 5; i++) {
      parent.appendChild(document.createElement(spacer));
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
/*
 * Covered in the TamperMonkey script, which then will inject these
 * into the DOM.
*/
// var inject = new InjectOptions("parent_mass_convert", batchTagFunctions);
// inject.init();
