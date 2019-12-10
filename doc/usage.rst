
.. _owl_client_usage:

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

Running pipelines
-----------------

Currently there are two modes of running a pipeline. For production purposes
a pipeline will be submitted to the IMAXT server and run there. For
development, pipelines can be run in the local computer.

Submitting pipelines
''''''''''''''''''''

Submitting pipelines requires a pipeline definition file in YAML format.
See the documentation of the individual pipelines
for detailed instructions.

.. code-block:: sh

    owl submit pipedef.yaml

Running pipelines locally
'''''''''''''''''''''''''

In order to run a pipeline locally, the code (referenced in the pipeline
definition file) must be installed in the local machine.
See the documentation of the individual pipelines
for detailed instructions.

.. code-block:: sh

    owl execute pipedef.yaml

For debugging purposes, add the ``--debug`` option. This will run the
pipeline in a single thread, allowing the use of ``breakpoint()`` and
the python debugger.
Note however that this will run much slower as there is no parallelization.


Submitting pipelines to other schedulers
''''''''''''''''''''''''''''''''''''''''

Future releases will be able to submit pipelines in HPC environments
like HTCondor and SLURM.
