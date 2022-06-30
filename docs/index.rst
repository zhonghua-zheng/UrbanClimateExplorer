.. Urban Climate Explorer documentation master file, created by
   sphinx-quickstart on Wed Feb 23 12:42:00 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Urban Climate Explorer
=======================================================================

|doi| |docs| |GitHub| |binder| |license|

.. |doi| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6474004.svg
   :target: https://doi.org/10.5281/zenodo.6474004

.. |docs| image:: https://readthedocs.org/projects/urbanclimateexplorer/badge/?version=latest
   :target: https://urbanclimateexplorer.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |GitHub| image:: https://img.shields.io/badge/GitHub-UrbanClimateExplorer-brightgreen.svg
   :target: https://github.com/zzheng93/UrbanClimateExplorer

.. |binder| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/zzheng93/UrbanClimateExplorer/HEAD?labpath=docs%2Fnotebooks

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://github.com/zzheng93/UrbanClimateExplorer/blob/master/LICENSE

Explore and Emulate Urban Climate on AWS Cloud.

Author: `Dr. Zhonghua Zheng <https://zzheng93.github.io/>`_

.. toctree::
   :maxdepth: 2
   :caption: Overview

   pages/about.md
   pages/install_run.md

.. toctree::
   :maxdepth: 2
   :caption: Tutorial

   pages/setup.md
   notebooks/CESM1_demo.ipynb
   notebooks/CESM2_demo.ipynb
   notebooks/CESM2_to_CMIP6.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Reference

   notebooks/how_to_create_a_json_file.ipynb
   notebooks/CESM1_get_urban_areas_mask.ipynb
   notebooks/CESM2_subgrid_info.ipynb

How to ask for help?
--------------------

The `GitHub issue tracker <https://github.com/zzheng93/UrbanClimateExplorer/issues>`_ is the primary place for bug reports. 

Acknowledgments
---------------

We thank AWS for providing AWS Cloud Credits for Research.

We would like to acknowledge high-performance computing support from Cheyenne (`doi:10.5065/D6RX99HX <https://doi.org/10.5065/D6RX99HX>`_) provided by NCAR's Computational and Information Systems Laboratory, sponsored by the National Science Foundation.