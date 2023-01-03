 COREutils
==========

COREutils is a python package allowing the construction of objects representing the core of a nuclear reactor (at the assembly level, assuming that the pin level is spatially homogenised). The resulting object can then be used to generate the input for other codes (like FRENETIC or FreeFEM++).

The COREutils package is composed of the following sub-packages:

* *core*, where the geometrical, neutronic and thermal-hydraulic parameters are read from an input file in .json format and used to build the core object
* *frenetic*, where the core object is used to build the neutronic and thermal-hydraulic input.
* *freefem*, where the core object is used to build the neutronic input.
* *tools*, which contains some classes for plotting and saving the core object.

The structure of the code should enable to easily extend its functionality by writing an interface class to translate the core object and its physical properties to the input of other codes.

## 🔧 Installation

To install COREutils, run the following commands:

`git clone https://nicolo_abrate@bitbucket.org/nemofissiondivision/coreutils.git`

## ⚖️ License

This package comes with the MIT license.

## 📘 Documentation

The package documentation can be found inside COREutils itself.

## 📞 Contacts

* [**Nicolo' Abrate**](http://www.denerg.polito.it/personale/scheda/(nominativo)/nicolo.abrate) - nicolo.abrate@polito.it
