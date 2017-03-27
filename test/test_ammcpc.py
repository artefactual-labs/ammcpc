from __future__ import print_function, unicode_literals
import json
import os
import sys
from unittest import TestCase
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

sys.path.insert(0, os.path.abspath('..'))
from ammcpc.ammcpc import MediaConchPolicyCheckerCommand


HERE = os.path.dirname(os.path.realpath(__file__))
# For the purposes of the fails.mkv and passes.mkv files, both policy files
# behave the same. At some point MediaConch switched over to the more readable
# .xml policy file format but retaned backwards-compatible support for the .xsl
# format.
POLICY_XSL_NAME = 'NYULib_MKVFFV1_MODIFIED.xsl'
POLICY_XSL_PATH = os.path.join(HERE, 'policies', POLICY_XSL_NAME)
POLICY_XML_NAME = 'NYULib_MKVFFV1_MODIFIED.xml'
POLICY_XML_PATH = os.path.join(HERE, 'policies', POLICY_XML_NAME)
FILE_FAILS_PATH = os.path.join(HERE, 'files', 'fails.mkv')
FILE_PASSES_PATH = os.path.join(HERE, 'files', 'passes.mkv')


class Capturing(list):
    """Context manager to capture stdout and stderr from a method call. Needed
    for testing because crucial behaviour of the ``check`` method involves
    printing to stdout/stderr. Adapted from
    http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    """

    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio = StringIO()
        sys.stderr = self._stringioerr = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        self.extend(self._stringioerr.getvalue().splitlines())
        del self._stringio
        del self._stringioerr
        sys.stdout = self._stdout
        sys.stderr = self._stderr


class TestMediaConchPolicyCheckerCommand(TestCase):
    """Test MediaConchPolicyCheckerCommand class."""

    def test_check_bad_file(self):
        """Expect a policy check on a failing file to return a 0 exit code and
        print to stdout a JSON object with a 'eventOutcomeInformation' attribute
        whose value is 'fail'.
        """
        policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path=POLICY_XSL_PATH)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_FAILS_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'fail'
        with open(POLICY_XSL_PATH) as filei:
            assert output['policy'] == filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path=POLICY_XML_PATH)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_FAILS_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'fail'
        with open(POLICY_XML_PATH) as filei:
            assert output['policy'] == filei.read()

    def test_check_bad_file_str_pol(self):
        """Same as ``test_check_bad_file`` except that the policy is passed as
        a string.
        """
        with open(POLICY_XSL_PATH) as filei:
            policy = filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy=policy, policy_file_name=POLICY_XSL_NAME)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_FAILS_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'fail'
        assert output['policy'] == policy
        with open(POLICY_XML_PATH) as filei:
            policy = filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy=policy, policy_file_name=POLICY_XML_NAME)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_FAILS_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'fail'
        assert output['policy'] == policy

    def test_check_good_file(self):
        """Expect a policy check on a passing file to return a 0 exit code and
        print to stdout a JSON object with a 'eventOutcomeInformation' attribute
        whose value is 'pass'.
        """
        policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path=POLICY_XSL_PATH)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_PASSES_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'pass'
        with open(POLICY_XSL_PATH) as filei:
            assert output['policy'] == filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path=POLICY_XML_PATH)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_PASSES_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'pass'
        with open(POLICY_XML_PATH) as filei:
            assert output['policy'] == filei.read()

    def test_check_good_file_str_pol(self):
        """Same as ``test_check_good_file`` except that the policy is passed as
        a string.
        """
        with open(POLICY_XSL_PATH) as filei:
            policy = filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy=policy, policy_file_name=POLICY_XSL_NAME)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_PASSES_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'pass'
        assert output['policy'] == policy
        with open(POLICY_XML_PATH) as filei:
            policy = filei.read()
        policy_checker = MediaConchPolicyCheckerCommand(
            policy=policy, policy_file_name=POLICY_XML_NAME)
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_PASSES_PATH)
        output = json.loads(output[0])
        assert exitcode == 0
        assert output['eventOutcomeInformation'] == 'pass'
        assert output['policy'] == policy

    def test_no_policy(self):
        """Expect a 1 exit code and a fail outcome when the policy file does
        not exist.
        """
        policy_checker = MediaConchPolicyCheckerCommand(
            policy_file_path='fake/policy/path')
        with Capturing() as output:
            exitcode = policy_checker.check(FILE_PASSES_PATH)
        output = json.loads(output[0])
        assert exitcode == 1
        assert output['eventOutcomeInformation'] == 'fail'
        assert output['eventOutcomeDetailNote'] == 'There is no policy file at fake/policy/path'
