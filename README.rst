
Client for submitting Owl pipelines either to the IMAXT server or locally using Dask.

Owl is a framework for submitting jobs (a.k.a. pipelines) in a remote cluster.
The Owl server runs jobs in Kubernetes using Dask. The Owl client authenticates
with the remote server and submits the jobs as specified in a pipeline
definition file.