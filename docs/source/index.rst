.. Documentation master file
   It contains a hidden root toctree directive so that Sphinx
   has an internal index of all of the pages and doesn't
   produce a plethora of warnings about most documents not being in
   a toctree.
   See http://sphinx-doc.org/tutorial.html#defining-document-structure

.. _contents:

.. image:: images/Mantid_Logo_Transparent.png
   :alt: The logo for the Mantid Project
   :align: center

====================
Mantid Documentation
====================

.. toctree::
   :hidden:
   :glob:
   :maxdepth: 1

   algorithms/index
   algorithms/*
   concepts/index
   interfaces/index
   fitfunctions/*
   fitminimizers/index
   api/index
   release/index


This is the documentation for Mantid |release|.

**Sections:**

.. image:: images/mantid.png
   :alt: A preying mantis with arms upraised
   :width: 200px
   :align: right

* `Algorithms <algorithms/index.html>`_

  `List of algorithms available in Mantid for loading, processing and saving data.`

* `Concepts <concepts/index.html>`_

  `The basic ideas and principles behind Mantid`

* `Interfaces <interfaces/index.html>`_

  `List of interfaces containing the tools used for a specific neutron or muon technique`

* `Fit Functions <fitfunctions/index.html>`_

  `Functions to fit to your data`

* `Fit Minimizers <fitminimizers/index.html>`_

  `Algorithms for determining the fit of the functions`

* `API <api/index.html>`_
    - `Python <api/python/index.html>`_

      `Reference pages documenting the Python API available from Mantid`

    - `C++ <http://doxygen.mantidproject.org/>`_ (Doxygen)

      `Reference pages containing the C++ developer documentation`

* `Release Notes <release/index.html>`_

  `Details of new or changed features in all previous releases`
