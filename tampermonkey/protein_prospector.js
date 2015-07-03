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

/*
 * In order to use this script, you need to change the user token to your
 * own from the GitHub repository. To get your user token, go to the
 * Lan Huang Scripts repoistory, click "raw" and copy everything after
 * "token=". Just copy that into these scripts and replace <USERTOKEN>
 * with your the value.
*/

// ==UserScript==
// @id              Protein Prospector Scripts
// @name            Protein Prospector Scripts
// @namespace       https://github.com/Alexhuszagh/
// @version         0.0.1
// @author          Alex Huszagh <ahuszagh@gmail.com>
// @description     Protein Prospector scripts increase user efficiency by repeating repetitive clicks. Programmed in the spirit of DRY for data analysis.
// @domain          http://lanhuang.ucsf.edu/
// @domain          http://prospector.ucsf.edu/
// @domain          http://prospector2.ucsf.edu/
// @match           http://lanhuang.ucsf.edu:18181/prospector/cgi-bin/msform.cgi*
// @match           http://prospector2.ucsf.edu/prospector/cgi-bin/msform.cgi*
// @Copyright       2015+, Alex Huszagh
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/batch_tag.js?token=<USERTOKEN>
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/search_compare.js?token=<USERTOKEN>
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/inject.js?token=<USERTOKEN>
// @grant           unsafeWindow
// @run-at          document-idle
// ==/UserScript==

// ESLint settings
/*eslint no-undef:0, no-redeclare:0 */
/*global document:true*/

// Grab the header for the form
var innerText = document.getElementsByClassName("form_name")[0].innerText;

// Grab functions
if (typeof batchTagFunctions === "undefined") {
  batchTagFunctions = unsafeWindow.batchTagFunctions;
  searchCompareFunctions = unsafeWindow.searchCompareFunctions;
}

// Check to see
if (innerText.substring(0, 9) === "Batch-Tag") {
  var inject = new InjectOptions("parent_mass_convert",
                                 batchTagFunctions);
  inject.init();
}
else if (innerText.substring(0, 14) === "Search Compare") {
  var inject = new InjectOptions(null, searchCompareFunctions);
  inject.init();
}
