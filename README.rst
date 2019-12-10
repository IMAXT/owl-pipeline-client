
.. image:: https://img.shields.io/badge/python-3.6%20%7C%203.7-blue
   :class: badge

.. image:: https://anaconda.org/eddie0uk/owl-pipeline-client/badges/version.svg
   :class: badge
   :target: https://anaconda.org/eddie0uk/owl-pipeline-client

.. image:: https://img.shields.io/pypi/v/owl-pipeline-client.svg
   :class: badge
   :target: https://pypi.org/project/owl-pipeline-client

.. image:: https://anaconda.org/eddie0uk/owl-pipeline-client/badges/latest_release_date.svg
   :class: badge
   :target: https://anaconda.org/eddie0uk/owl-pipeline-client

Client for submitting Owl pipelines either to the IMAXT server or locally using Dask.

Owl is a framework for submitting jobs (a.k.a. pipelines) in a remote cluster.
The Owl server runs jobs in Kubernetes using Dask. The Owl client authenticates
with the remote server and submits the jobs as specified in a pipeline
definition file.
