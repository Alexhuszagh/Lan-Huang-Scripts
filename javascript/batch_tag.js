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

/*
Automated scripts to configure and edit "Batch Tag" and "Batch Tag Web"
settings.
*/

// Create core Batch Tag class
function BatchTag() {
  // grab out databases
  this.database = document.getElementsByName("database")
  this.protein_sequence = document.getElementsByName("user_protein_sequence")

  // grab taxonomy identifiers
  this.species = document.getElementsByName("species")

  // grab our mod lists
  this.const_mods = document.getElementsByName("const_mod")
  this.var_mods = document.getElementsByName("msms_mod_AA")
}
