"""ammcpc --- Archivematica (AM) MediaConch (MC) Policy Checker (PC)

This command-line application (and python module) is a simple wrapper around
the MediaConch tool which takes a file and a MediaConch policy file as input
and prints to stdout a JSON object indicating, in a way that Archivematica
likes, whether the file passes the policy check.

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

"""

import json
import os
import subprocess
import sys
import tempfile
import uuid
from collections import namedtuple

from lxml import etree

__version__ = "0.3.0"

SUCCESS_CODE = 0
ERROR_CODE = 1
NS = "{https://mediaarea.net/mediaconch}"


class MediaConchException(Exception):
    pass


Parse = namedtuple("Parse", "etree_el stdout")


class MediaConchPolicyCheckerCommand:
    """MC Policy Checker Command runs
    ``mediaconch -mc -fx -p <path_to_policy_xsl_file> <target>``,
    parses the returned XML, and prints out a JSON report summarizing the
    results of the policy check.

    Initialize with the path to a policy file then call ``check``::

        >>> checker = MediaConchPolicyCheckerCommand('/path/to/policy')
        >>> checker.check('/path/to/file-to-be-checked')
    """

    def __init__(self, policy_file_path=None, policy=None, policy_file_name=None):
        self._policy_file_path = policy_file_path
        self._policy = policy
        self._policy_file_name = policy_file_name
        self.policy_file_name = None

    def check(self, target):
        """Return 0 if MediaConch can successfully assess whether the file at
        `target` passes the policy checks that are relevant to it, given its
        purpose and the state of the FPR. Parse the XML output by MediaConch
        and print a JSON representation of that output.
        """
        try:
            self._validate()
            parse = self._parse_mediaconch_output(target)
            policy_checks = _get_policy_checks(parse.etree_el)
            info, detail = self._get_evt_out_inf_detail(policy_checks)
            stdout = parse.stdout.decode("utf8")
            print(
                json.dumps(
                    {
                        "eventOutcomeInformation": info,
                        "eventOutcomeDetailNote": detail,
                        "policy": self.policy,
                        "policyFileName": self.policy_file_name,
                        "stdout": stdout,
                    }
                )
            )
            return SUCCESS_CODE
        except MediaConchException as exc:
            return self._error(exc)

    def _validate(self):
        if self._policy_file_path:
            if not os.path.isfile(self._policy_file_path):
                raise MediaConchException(
                    f"There is no policy file at {self._policy_file_path}"
                )
            self.policy_file_name = os.path.basename(self._policy_file_path)
            with open(self._policy_file_path) as filei:
                self.policy = filei.read()
        elif self._policy and self._policy_file_name:
            self.policy_file_name = self._policy_file_name
            self.policy = self._policy
        else:
            raise MediaConchException(
                "You must supply the path to a MediaConch policy file or"
                " the text of the policy and its name as strings."
            )

    def _parse_mediaconch_output(self, target):
        """Run ``mediaconch -mc -fx -p <path_to_policy_xsl_file>
        <target>`` against the file at ``path_to_target`` and return an lxml
        etree parse of the output.
        """
        try:
            if self._policy_file_path:
                args = [
                    "mediaconch",
                    "-mc",
                    "-fx",
                    "-p",
                    self._policy_file_path,
                    target,
                ]
                output = subprocess.check_output(args)
            else:
                ext = os.path.splitext(self.policy_file_name)[1]
                pfp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                try:
                    pfp.write(self._policy.encode("utf8"))
                    pfp.close()
                    args = ["mediaconch", "-mc", "-fx", "-p", pfp.name, target]
                    output = subprocess.check_output(args)
                finally:
                    if not pfp.closed:
                        pfp.close()
                    os.unlink(pfp.name)
        except subprocess.CalledProcessError:
            raise MediaConchException(
                "MediaConch failed when running: {}".format(" ".join(args))
            )
        try:
            return Parse(etree_el=etree.fromstring(output), stdout=output)
        except etree.XMLSyntaxError:
            raise MediaConchException(
                "The MediaConch command failed when attempting to parse the"
                f" XML output by MediaConch:\n\n {output}"
            )

    def _get_evt_out_inf_detail(self, policy_checks):
        """Return a 2-tuple of info and detail.
        - info: 'pass' or 'fail'
        - detail: human-readable string indicating which policy checks
        passed or failed. If the policy check as a whole passed, just return
        the passed check names; if it failed, just return the failed ones.
        """
        if policy_checks["mc_version"] == "0.3":
            return self._get_evt_out_inf_detail_v_0_3(policy_checks)
        return self._get_evt_out_inf_detail_v_0_1(policy_checks)

    def _get_evt_out_inf_detail_v_0_3(self, policy_checks):
        failed_policy_checks = set()
        passed_policy_checks = set()
        info = "fail"
        if policy_checks["root_policy"][1] == "pass":
            info = "pass"
        for name, outcome in policy_checks["policies"]:
            if outcome == "pass":
                passed_policy_checks.add(name)
            else:
                failed_policy_checks.add("failed policy/rule: %s" % name)
        prefix = (
            "MediaConch policy check result against policy file"
            f" {self.policy_file_name}:"
        )
        if info == "fail":
            return ("fail", "{} {}".format(prefix, "; ".join(failed_policy_checks)))
        if passed_policy_checks:
            return (
                "pass",
                "{} All policy checks passed: {}".format(
                    prefix, "; ".join(passed_policy_checks)
                ),
            )
        return (
            "pass",
            f"{prefix} No checks passed, but none failed" " either.",
        )

    def _get_evt_out_inf_detail_v_0_1(self, policy_checks):
        failed_policy_checks = set()
        passed_policy_checks = set()
        for name, (out, fie, act, rea) in policy_checks["policy_checks"].items():
            if out == "pass":
                passed_policy_checks.add(name)
            else:
                failed_policy_checks.add(
                    f'The check "{name}" failed; the actual value for the'
                    f' field "{fie}" was "{act}"; the reason was'
                    f' "{rea}".'
                )
        prefix = (
            "MediaConch policy check result against policy file"
            f" {self.policy_file_name}:"
        )
        if failed_policy_checks:
            return ("fail", "{} {}".format(prefix, " ".join(failed_policy_checks)))
        if passed_policy_checks:
            return (
                "pass",
                "{} All policy checks passed: {}".format(
                    prefix, "; ".join(passed_policy_checks)
                ),
            )
        return (
            "pass",
            f"{prefix} No checks passed, but none failed" " either.",
        )

    def _error(self, exc):
        try:
            pfn = self.policy_file_name
            pol = self.policy
        except AttributeError:
            pfn = pol = None
        print(
            json.dumps(
                {
                    "eventOutcomeInformation": "fail",
                    "eventOutcomeDetailNote": str(exc),
                    "policy": pol,
                    "policyFileName": pfn,
                    "stdout": None,
                }
            ),
            file=sys.stderr,
        )
        return ERROR_CODE


def _get_policy_check_name(policy_check_el):
    return policy_check_el.attrib.get("name", "Unnamed Check %s" % uuid.uuid4())


def _parse_policy_check_test(policy_check_el):
    """Return a 3-tuple parse of the <test> element of the policy <check>
    element.

    - El1 is outcome ("pass" or "fail" or other?)
    - El2 is the relevant field (i.e., attribute of the file)
    - El3 is the actual value of the relevant attribute/field.
    - El4 is the reason for the failure.
    """
    test_el = policy_check_el.find("%stest" % NS)
    if test_el is None:
        return None
    field = "no field"
    context_el = policy_check_el.find("%scontext" % NS)
    if context_el is not None:
        field = context_el.attrib.get("field", "no field")
    return (
        test_el.attrib.get("outcome", "no outcome"),
        field,
        test_el.attrib.get("actual", "no actual value"),
        test_el.attrib.get("reason", "no reason"),
    )


def _get_policy_checks_v_0_3(doc):
    policy_checks = {"mc_version": "0.3", "policies": []}
    root_policy = doc.find(f".{NS}media/{NS}policy")
    if root_policy is None:
        raise MediaConchException("Unable to find a root policy")
    policy_checks["root_policy"] = (
        root_policy.attrib.get("name", "No root policy name"),
        root_policy.attrib.get("outcome", "No root policy outcome"),
    )
    for el_tname in ("policy", "rule"):
        path = f".//{NS}{el_tname}"
        for policy_el in doc.iterfind(path):
            policy_name = _get_policy_check_name(policy_el)
            policy_checks["policies"].append(
                (policy_name, policy_el.attrib.get("outcome", "no outcome"))
            )
    return policy_checks


def _get_policy_checks_v_0_1(doc):
    policy_checks = {"mc_version": "0.1", "policy_checks": {}}
    path = f".{NS}media/{NS}policyChecks/{NS}check"
    for policy_check_el in doc.iterfind(path):
        policy_check_name = _get_policy_check_name(policy_check_el)
        parse = _parse_policy_check_test(policy_check_el)
        if parse:
            policy_checks["policy_checks"][policy_check_name] = parse
    return policy_checks


def _get_policy_checks(doc):
    """Get all of the policy check names and outcomes from the policy check
    output file parsed as ``doc``.
    """
    mc_xml_vrsn = doc.attrib.get("version", "No identifiable MediaConch XML version")
    if mc_xml_vrsn == "0.3":
        return _get_policy_checks_v_0_3(doc)
    elif mc_xml_vrsn == "0.1":
        return _get_policy_checks_v_0_1(doc)
    else:
        raise MediaConchException(
            "Unable to parse MediaConch XML files with version" f' "{mc_xml_vrsn}"'
        )


def main():
    target = sys.argv[1]
    policy = sys.argv[2]
    policy_checker = MediaConchPolicyCheckerCommand(policy_file_path=policy)
    sys.exit(policy_checker.check(target))
