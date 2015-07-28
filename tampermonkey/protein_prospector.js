/* Copyright (C) 2015 The Regents of the University of California.
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

// ==UserScript==
// @id              Protein Prospector Scripts
// @name            Protein Prospector Scripts
// @namespace       https://github.com/Alexhuszagh/
// @version         0.0.3
// @author          Alex Huszagh <ahuszagh@gmail.com>
// @description     Protein Prospector scripts increase user efficiency by repeating repetitive clicks. Programmed in the spirit of DRY for data analysis.
// @domain          http://lanhuang.ucsf.edu/
// @domain          http://prospector.ucsf.edu/
// @domain          http://prospector2.ucsf.edu/
// @match           http://lanhuang.ucsf.edu:18181/prospector/cgi-bin/msform.cgi*
// @match           http://prospector2.ucsf.edu/prospector/cgi-bin/msform.cgi*
// @Copyright       2015+, Alex Huszagh
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/batch_tag.js
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/search_compare.js
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/inject.js
// @downloadURL     https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/tampermonkey/protein_prospector.js
// @updateURL       https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/tampermonkey/protein_prospector.js
// @grant           unsafeWindow
// @run-at          document-idle
// ==/UserScript==

// ESLint settings
/*eslint no-undef:0, no-redeclare:0 */
/*global document:true*/

// Grab the header for the form
var header = document.getElementsByClassName("form_name")[0];
var text = header.innerText || header.textContent;
// The textContext keeps the newline featsures on the top & bottom
var trimmed = text.trim();

var InjectOptions = InjectOptions || unsafeWindow.InjectOptions;
// Check to see current document loaded
if (trimmed.substring(0, 9) === "Batch-Tag") {
  var batchTagFunctions = batchTagFunctions || unsafeWindow.batchTagFunctions;
  var inject = new InjectOptions("parent_mass_convert",
                                 batchTagFunctions, "br");
  inject.init();
}
else if (trimmed === "Search Compare") {
  var searchCompareFunctions = searchCompareFunctions || unsafeWindow.searchCompareFunctions;
  var inject = new InjectOptions("save_params", searchCompareFunctions,
                                 "nbsp");
  inject.init();
}
