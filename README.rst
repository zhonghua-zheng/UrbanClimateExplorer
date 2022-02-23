Urban Climate Explorer
------------------------------------------------
|docs| |GitHub| |binder| |license|

.. |docs| image:: https://readthedocs.org/projects/pmcpy/badge/?version=latest
   :target: https://pmcpy.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |GitHub| image:: https://img.shields.io/badge/GitHub-pmcpy-brightgreen.svg
   :target: https://github.com/zzheng93/pmcpy

.. |binder| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/zzheng93/pmcpy/HEAD?filepath=docs%2Fnotebooks

.. |license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://github.com/zzheng93/pmcpy/blob/master/LICENSE

Explore and Emulate Urban Climate on AWS Cloud.

How to use it?
--------------
You may reproduce the jupyter notebook example on `Binder <https://mybinder.org/v2/gh/zzheng93/pmcpy/HEAD?filepath=docs%2Fnotebooks>`_.

Please check `online documentation <https://pmcpy.readthedocs.io/en/latest/>`_ for more information.

How to play with it locally?
----------------------------

Step 1: use conda to install the environment::

    $ git clone git@github.com:zzheng93/UrbanClimateExplorer.git
    $ cd ./UrbanClimateExplorer/binder 
    $ conda env create -f environment.yml
    $ conda activate aws_urban

Step 2: launch jupyter::

    $ git clone git@github.com:zzheng93/UrbanClimateExplorer.git
    $ cd ./UrbanClimateExplorer/notebooks 
    $ jupyter notebook

How to ask for help
-------------------
The `GitHub issue tracker <https://github.com/zzheng93/pmcpy/issues>`_ is the primary place for bug reports. 
