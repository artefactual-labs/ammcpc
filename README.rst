================================================================================
  ammcpc --- Archivematica (AM) MediaConch (MC) Policy Checker (PC)
================================================================================

This command-line application and python module is a simple wrapper around the
MediaConch tool which takes a file and a MediaConch policy file as input and
prints to stdout a JSON object indicating, in a way that Archivematica likes,
whether the file passes the policy check.


.. class:: no-web no-pdf

|build|
|coverage|


Install with Pip::

    $ pip install ammcpc

Install from source::

    $ python setup.py install

Command-line usage::

    $ ammcpc <PATH_TO_FILE> <PATH_TO_POLICY>

Python usage with a policy file path::

    >>> from ammcpc import MediaConchPolicyCheckerCommand
    >>> policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path='/path/to/my-policy.xml')
    >>> exitcode = policy_checker.check('/path/to/file.mkv')

Python usage with a policy as a string::

    >>> policy_checker = MediaConchPolicyCheckerCommand(
            policy='<?xml><policy> ... </policy>',
            policy_file_name='my-policy.xml')
    >>> exitcode = policy_checker.check('/path/to/file.mkv')

System dependencies:

- MediaConch version 16.12

To run the tests, make sure tox is installed, then::

    $ tox


.. |build|  image:: https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml/badge.svg
    :target: https://github.com/artefactual-labs/ammcpc/actions/workflows/test.yml
    :alt: Build status of the master branch

.. |coverage|  image:: https://codecov.io/gh/artefactual-labs/ammcpc/branch/master/graph/badge.svg?token=8iFP6qzL6Q
    :target: https://codecov.io/gh/artefactual-labs/ammcpc
    :alt: Test coverage of the master branch
