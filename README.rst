================================================================================
  ammcpc --- Archivematica (AM) MediaConch (MC) Policy Checker (PC)
================================================================================

This command-line application is a simple wrapper around the MediaConch tool
which takes a file and a MediaConch policy file as input and prints to stdout a
JSON object indicating, in a way that Archivematica likes, whether the file
passes the policy check.

Install with Pip::

    $ pip install ammcpc

Install from source::

    $ python setup.py install

Usage::

    $ ammcpc <PATH_TO_FILE> <PATH_TO_POLICY>

System dependencies:

- MediaConch version 16.12

To run the tests, make sure pytest is installed, then::

    $ cd test/
    $ pytest

