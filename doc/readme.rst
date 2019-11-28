
Installation
============

Owl client requires Python 3.7. Using pip

.. code-block:: sh

    pip install owl-pipeline-client

Usage
=====

Authenticating
--------------

In order to submit pipelines to the server one needs to authenticate.
To do this, run the following command

.. code-block:: sh

    owl login

This will prompt for your username and password. If succesful it will save
your credentials in the file ``~/.owlrc``.

Submitting pipelines
--------------------

Submitting pipelines requires a pipeline definition file in YAML format.
See the documentation of the individual pipelines
for detailed instructions. Submitting

.. code-block:: sh

    owl submit pipedef.yaml

Running pipelines locally
-------------------------

.. code-block:: sh

    owl execute pipedef.yaml

