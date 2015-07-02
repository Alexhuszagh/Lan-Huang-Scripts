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
// @name            Protein Prospector Scripts -- Batch Tag
// @namespace       https://github.com/Alexhuszagh/
// @version         0.0.1
// @author          Alex Huszagh <ahuszagh@gmail.com>
// @description     Protein Prospector scripts increase user efficiency by repeating repetitive clicks. Programmed in the spirit of DRY for data analysis.
// @domain          http://lanhuang.ucsf.edu/
// @match           http://prospector2.ucsf.edu/prospector/cgi-bin/msform.cgi?form=batchtag*
// @match           http://lanhuang.ucsf.edu:18181/prospector/cgi-bin/msform.cgi?form=batchtag*
// @Copyright       2015+, Alex Huszagh
// @require         https://raw.githubusercontent.com/Alexhuszagh/Lan-Huang-Scripts/master/javascript/batch_tag.js?token=<USERTOKEN>
// @run-at          document-idle
// ==/UserScript==

// ESLint settings
/*eslint no-undef:0 */

var inject = new InjectOptions("parent_mass_convert");
inject.init();
