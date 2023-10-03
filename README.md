COREutils
=========

<p
    <a href='https://coreutils.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/coreutils/badge/?version=latest' alt='Documentation Status' />
    </a>
</p>

<br>

COREutils is a python package allowing the construction of objects representing the core of a nuclear reactor (at the assembly level, assuming that the pin level is spatially homogenised). The resulting object can then be used to generate the input for other codes (like FRENETIC or FreeFEM++).

The COREutils package is composed of the following sub-packages:

* *core*, where the geometrical, neutronic and thermal-hydraulic parameters are read from an input file in .json format and used to build the core object
* *frenetic*, where the core object is used to build the neutronic and thermal-hydraulic input.
* *freefem*, where the core object is used to build the neutronic input.
* *tools*, which contains some classes for plotting and saving the core object.

The structure of the code should enable to easily extend its functionality by writing an interface class to translate the core object and its physical properties to the input of other codes.

---

## 🔧 Installation

To install COREutils, run the following commands:

`git clone https://github.com/nicoloabrate/COREutils`

---

## ⚖️ License

This package comes with the MIT license.

---

## 📘 Documentation

The documentation can be found inside the package itself. The documentation can be compiled locally by the user in HTML or LaTeX formats by running the following instructions inside the main COREutils directory,

`pip install -r docs/requirements.txt`

For HTML:

`sphinx-build -b html docs docs_html`

For PDF:

`sphinx-build -b latex docs docs_tex`

An online, up-to-date version of the documentation is hosted by [ReadTheDocs](https://coreutils.readthedocs.io/en/latest/?badge=latest).

---

## 📞 Contacts

* [**Nicolò Abrate**](http://www.denerg.polito.it/personale/scheda/(nominativo)/nicolo.abrate) - nicolo.abrate@polito.it

---
