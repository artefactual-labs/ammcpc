import json
import os
from unittest import mock

import pytest

from ammcpc.ammcpc import MediaConchPolicyCheckerCommand

HERE = os.path.dirname(os.path.realpath(__file__))
# For the purposes of the fails.mkv and passes.mkv files, both policy files
# behave the same. At some point MediaConch switched over to the more readable
# .xml policy file format but retaned backwards-compatible support for the .xsl
# format.
POLICY_XSL_NAME = "NYULib_MKVFFV1_MODIFIED.xsl"
POLICY_XSL_PATH = os.path.join(HERE, "policies", POLICY_XSL_NAME)
POLICY_XML_NAME = "NYULib_MKVFFV1_MODIFIED.xml"
POLICY_XML_PATH = os.path.join(HERE, "policies", POLICY_XML_NAME)
FILE_FAILS_PATH = os.path.join(HERE, "files", "fails.mkv")
FILE_PASSES_PATH = os.path.join(HERE, "files", "passes.mkv")

# These fixtures (policies and MKV files) validate as expected up until
# mediaconch 18.03-2, but they fail in newer versions. These variables mock the
# expected output so the tests do not depend on mediaconch being installed.
XSL_FAILED_CHECK_OUTPUT = """
<MediaConch xmlns="https://mediaarea.net/mediaconch" xmlns:mi="https://mediaarea.net/mediainfo" version="0.1">
  <media ref="/fails.mkv">
    <policyChecks>
      <name>Preservation Master File Recommendations - Matroska/FFV1 (NYU Libraries)</name>
      <description/>
      <check name="General Format equals Matroska">
        <context field="Format" value="Matroska"/>
        <test tracktype="General" actual="Matroska" outcome="pass"/>
      </check>
      <check name="Video Format is FFV1">
        <context field="Format" value="FFV1"/>
        <test tracktype="Video" trackid="1" actual="FFV1" outcome="pass"/>
      </check>
      <check name="Video CodecID equals FFV1">
        <context field="CodecID" value="V_MS/VFW/FOURCC / FFV1"/>
        <test tracktype="Video" trackid="1" actual="V_MS/VFW/FOURCC / FFV1" outcome="pass"/>
      </check>
      <check name="Video Width equals 720 (pixels)">
        <context field="Width" value="720"/>
        <test tracktype="Video" trackid="1" actual="720" outcome="pass"/>
      </check>
      <check name="Video Height equals 486 (pixels)">
        <context field="Height" value="486"/>
        <test tracktype="Video" trackid="1" actual="540" outcome="fail" reason="is not equal"/>
      </check>
      <check name="Video DisplayAspectRatio equals 4:3 (1.333)">
        <context field="DisplayAspectRatio" value="1.333"/>
        <test tracktype="Video" trackid="1" actual="1.333" outcome="pass"/>
      </check>
      <check name="Video FrameRate equals 29.97 fps (29.970)">
        <context field="FrameRate" value="29.970"/>
        <test tracktype="Video" trackid="1" actual="29.970" outcome="pass"/>
      </check>
      <check name="Video Standard equals NTSC">
        <context field="Standard" value="NTSC"/>
      </check>
      <check name="Video ColorSpace equals YUV">
        <context field="ColorSpace" value="YUV"/>
        <test tracktype="Video" trackid="1" actual="YUV" outcome="pass"/>
      </check>
      <check name="Video ChromaSubsampling equals 4:2:0">
        <context field="ChromaSubsampling" value="4:2:0"/>
        <test tracktype="Video" trackid="1" actual="4:4:4" outcome="fail" reason="is not equal"/>
      </check>
      <check name="Video BitDepth equals 8 (bits)">
        <context field="BitDepth" value="8"/>
        <test tracktype="Video" trackid="1" actual="8" outcome="pass"/>
      </check>
      <check name="Audio Format equals PCM">
        <context field="Format" value="PCM"/>
        <test tracktype="Audio" trackid="2" actual="PCM" outcome="pass"/>
      </check>
      <check name="Audio Channels are greater or equal than 1">
        <context field="Channels" value="1"/>
        <test tracktype="Audio" trackid="2" actual="2" outcome="pass"/>
      </check>
      <check name="Audio SamplingRate is greater or equal than 48 kHz (48000)">
        <context field="SamplingRate" value="48000"/>
        <test tracktype="Audio" trackid="2" actual="48000" outcome="pass"/>
      </check>
      <check name="Audio BitDepth is greater or equal than 16-bit">
        <context field="BitDepth" value="16"/>
        <test tracktype="Audio" trackid="2" actual="16" outcome="pass"/>
      </check>
    </policyChecks>
  </media>
</MediaConch>
""".strip()  # noqa: E501
XML_FAILED_CHECK_OUTPUT = """
<MediaConch xmlns="https://mediaarea.net/mediaconch" xmlns:mmt="https://mediaarea.net/micromediatrace" xmlns:mi="https://mediaarea.net/mediainfo" version="0.3">
  <media ref="/fails.mkv">
    <policy name="NYULib_MKVFFV1_MODIFIED" type="and" rules_run="13" fail_count="2" pass_count="11" outcome="fail">
      <description>Attempt to re-implement the NYULibraries_MKVFFV1.xsl policy file of MediaConch XML v. 0.1 as a v. 0.3 .xml policy</description>
      <rule name="General Format equals Matroska" value="Format" tracktype="General" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='General'][*]/mi:Format='Matroska'" outcome="pass"/>
      <rule name="Video Format is FFV1" value="Format" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Format='FFV1'" outcome="pass"/>
      <rule name="Video CodecID equals FFV1" value="CodecID" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:CodecID='V_MS/VFW/FOURCC / FFV1'" outcome="pass"/>
      <rule name="Video Width equals 720 (pixels)" value="Width" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Width='720'" outcome="pass"/>
      <rule name="Video Height equals 486 (pixels)" value="Height" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Height='486'" actual="540" outcome="fail"/>
      <rule name="Video DisplayAspectRatio equals 4:3 (1.333)" value="DisplayAspectRatio" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:DisplayAspectRatio='1.333'" outcome="pass"/>
      <rule name="Video ColorSpace equals YUV" value="ColorSpace" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:ColorSpace='YUV'" outcome="pass"/>
      <rule name="Video ChromaSubsampling equals 4:2:0" value="ChromaSubsampling" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:ChromaSubsampling='4:2:0'" actual="4:4:4" outcome="fail"/>
      <rule name="Video BitDepth equals 8 (bits)" value="BitDepth" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:BitDepth='8'" outcome="pass"/>
      <rule name="Audio Format equals PCM" value="Format" tracktype="Audio" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:Format='PCM'" outcome="pass"/>
      <rule name="Audio Channels are greater or equal than 1" value="Channels" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:Channels&gt;='1'" outcome="pass"/>
      <rule name="Audio SamplingRate is greater or equal than 48 kHz (48000)" value="SamplingRate" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:SamplingRate&gt;='48000'" outcome="pass"/>
      <rule name="Audio BitDepth is greater or equal than 16-bit" value="BitDepth" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:BitDepth&gt;='16'" outcome="pass"/>
    </policy>
  </media>
</MediaConch>
""".strip()  # noqa: E501
XSL_PASSED_CHECK_OUTPUT = """
<MediaConch xmlns="https://mediaarea.net/mediaconch" xmlns:mi="https://mediaarea.net/mediainfo" version="0.1">
  <media ref="/passes.mkv">
    <policyChecks>
      <name>Preservation Master File Recommendations - Matroska/FFV1 (NYU Libraries)</name>
      <description/>
      <check name="General Format equals Matroska">
        <context field="Format" value="Matroska"/>
        <test tracktype="General" actual="Matroska" outcome="pass"/>
      </check>
      <check name="Video Format is FFV1">
        <context field="Format" value="FFV1"/>
        <test tracktype="Video" trackid="1" actual="FFV1" outcome="pass"/>
      </check>
      <check name="Video CodecID equals FFV1">
        <context field="CodecID" value="V_MS/VFW/FOURCC / FFV1"/>
        <test tracktype="Video" trackid="1" actual="V_MS/VFW/FOURCC / FFV1" outcome="pass"/>
      </check>
      <check name="Video Width equals 720 (pixels)">
        <context field="Width" value="720"/>
        <test tracktype="Video" trackid="1" actual="720" outcome="pass"/>
      </check>
      <check name="Video Height equals 486 (pixels)">
        <context field="Height" value="486"/>
        <test tracktype="Video" trackid="1" actual="486" outcome="pass"/>
      </check>
      <check name="Video DisplayAspectRatio equals 4:3 (1.333)">
        <context field="DisplayAspectRatio" value="1.333"/>
        <test tracktype="Video" trackid="1" actual="1.333" outcome="pass"/>
      </check>
      <check name="Video FrameRate equals 29.97 fps (29.970)">
        <context field="FrameRate" value="29.970"/>
        <test tracktype="Video" trackid="1" actual="29.970" outcome="pass"/>
      </check>
      <check name="Video Standard equals NTSC">
        <context field="Standard" value="NTSC"/>
        <test tracktype="Video" trackid="1" actual="NTSC" outcome="pass"/>
      </check>
      <check name="Video ColorSpace equals YUV">
        <context field="ColorSpace" value="YUV"/>
        <test tracktype="Video" trackid="1" actual="YUV" outcome="pass"/>
      </check>
      <check name="Video ChromaSubsampling equals 4:2:0">
        <context field="ChromaSubsampling" value="4:2:0"/>
        <test tracktype="Video" trackid="1" actual="4:2:0" outcome="pass"/>
      </check>
      <check name="Video BitDepth equals 8 (bits)">
        <context field="BitDepth" value="8"/>
        <test tracktype="Video" trackid="1" actual="8" outcome="pass"/>
      </check>
      <check name="Audio Format equals PCM">
        <context field="Format" value="PCM"/>
        <test tracktype="Audio" trackid="2" actual="PCM" outcome="pass"/>
      </check>
      <check name="Audio Channels are greater or equal than 1">
        <context field="Channels" value="1"/>
        <test tracktype="Audio" trackid="2" actual="4" outcome="pass"/>
      </check>
      <check name="Audio SamplingRate is greater or equal than 48 kHz (48000)">
        <context field="SamplingRate" value="48000"/>
        <test tracktype="Audio" trackid="2" actual="48000" outcome="pass"/>
      </check>
      <check name="Audio BitDepth is greater or equal than 16-bit">
        <context field="BitDepth" value="16"/>
        <test tracktype="Audio" trackid="2" actual="16" outcome="pass"/>
      </check>
    </policyChecks>
  </media>
</MediaConch>
""".strip()  # noqa: E501
XML_PASSED_CHECK_OUTPUT = """
<MediaConch xmlns="https://mediaarea.net/mediaconch" xmlns:mmt="https://mediaarea.net/micromediatrace" xmlns:mi="https://mediaarea.net/mediainfo" version="0.3">
  <media ref="/passes.mkv">
    <policy name="NYULib_MKVFFV1_MODIFIED" type="and" rules_run="13" fail_count="0" pass_count="13" outcome="pass">
      <description>Attempt to re-implement the NYULibraries_MKVFFV1.xsl policy file of MediaConch XML v. 0.1 as a v. 0.3 .xml policy</description>
      <rule name="General Format equals Matroska" value="Format" tracktype="General" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='General'][*]/mi:Format='Matroska'" outcome="pass"/>
      <rule name="Video Format is FFV1" value="Format" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Format='FFV1'" outcome="pass"/>
      <rule name="Video CodecID equals FFV1" value="CodecID" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:CodecID='V_MS/VFW/FOURCC / FFV1'" outcome="pass"/>
      <rule name="Video Width equals 720 (pixels)" value="Width" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Width='720'" outcome="pass"/>
      <rule name="Video Height equals 486 (pixels)" value="Height" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:Height='486'" outcome="pass"/>
      <rule name="Video DisplayAspectRatio equals 4:3 (1.333)" value="DisplayAspectRatio" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:DisplayAspectRatio='1.333'" outcome="pass"/>
      <rule name="Video ColorSpace equals YUV" value="ColorSpace" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:ColorSpace='YUV'" outcome="pass"/>
      <rule name="Video ChromaSubsampling equals 4:2:0" value="ChromaSubsampling" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:ChromaSubsampling='4:2:0'" outcome="pass"/>
      <rule name="Video BitDepth equals 8 (bits)" value="BitDepth" tracktype="Video" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Video'][*]/mi:BitDepth='8'" outcome="pass"/>
      <rule name="Audio Format equals PCM" value="Format" tracktype="Audio" occurrence="*" operator="=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:Format='PCM'" outcome="pass"/>
      <rule name="Audio Channels are greater or equal than 1" value="Channels" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:Channels&gt;='1'" outcome="pass"/>
      <rule name="Audio SamplingRate is greater or equal than 48 kHz (48000)" value="SamplingRate" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:SamplingRate&gt;='48000'" outcome="pass"/>
      <rule name="Audio BitDepth is greater or equal than 16-bit" value="BitDepth" tracktype="Audio" occurrence="*" operator="&gt;=" xpath="mi:MediaInfo/mi:track[@type='Audio'][*]/mi:BitDepth&gt;='16'" outcome="pass"/>
    </policy>
  </media>
</MediaConch>
""".strip()  # noqa: E501


@pytest.fixture
def mediaconch_fails():
    with mock.patch(
        "subprocess.check_output",
        side_effect=[
            XSL_FAILED_CHECK_OUTPUT.encode(),
            XML_FAILED_CHECK_OUTPUT.encode(),
        ],
    ):
        yield


@pytest.fixture
def mediaconch_passes():
    with mock.patch(
        "subprocess.check_output",
        side_effect=[
            XSL_PASSED_CHECK_OUTPUT.encode(),
            XML_PASSED_CHECK_OUTPUT.encode(),
        ],
    ):
        yield


def test_check_bad_file(mediaconch_fails, capsys):
    """Expect a policy check on a failing file to return a 0 exit code and
    print to stdout a JSON object with a 'eventOutcomeInformation'
    attribute whose value is 'fail'.
    """
    policy_checker = MediaConchPolicyCheckerCommand(policy_file_path=POLICY_XSL_PATH)
    exitcode = policy_checker.check(FILE_FAILS_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "fail"
    with open(POLICY_XSL_PATH) as filei:
        assert output["policy"] == filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(policy_file_path=POLICY_XML_PATH)
    exitcode = policy_checker.check(FILE_FAILS_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "fail"
    with open(POLICY_XML_PATH) as filei:
        assert output["policy"] == filei.read()


def test_check_bad_file_str_pol(mediaconch_fails, capsys):
    """Same as ``test_check_bad_file`` except that the policy is passed as
    a string.
    """
    with open(POLICY_XSL_PATH) as filei:
        policy = filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(
        policy=policy, policy_file_name=POLICY_XSL_NAME
    )
    exitcode = policy_checker.check(FILE_FAILS_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "fail"
    assert output["policy"] == policy
    with open(POLICY_XML_PATH) as filei:
        policy = filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(
        policy=policy, policy_file_name=POLICY_XML_NAME
    )
    exitcode = policy_checker.check(FILE_FAILS_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "fail"
    assert output["policy"] == policy


def test_check_good_file(mediaconch_passes, capsys):
    """Expect a policy check on a passing file to return a 0 exit code and
    print to stdout a JSON object with a 'eventOutcomeInformation'
    attribute whose value is 'pass'.
    """
    policy_checker = MediaConchPolicyCheckerCommand(policy_file_path=POLICY_XSL_PATH)
    exitcode = policy_checker.check(FILE_PASSES_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "pass"
    with open(POLICY_XSL_PATH) as filei:
        assert output["policy"] == filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(policy_file_path=POLICY_XML_PATH)
    exitcode = policy_checker.check(FILE_PASSES_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "pass"
    with open(POLICY_XML_PATH) as filei:
        assert output["policy"] == filei.read()


def test_check_good_file_str_pol(mediaconch_passes, capsys):
    """Same as ``test_check_good_file`` except that the policy is passed as
    a string.
    """
    with open(POLICY_XSL_PATH) as filei:
        policy = filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(
        policy=policy, policy_file_name=POLICY_XSL_NAME
    )
    exitcode = policy_checker.check(FILE_PASSES_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "pass"
    assert output["policy"] == policy
    with open(POLICY_XML_PATH) as filei:
        policy = filei.read()
    policy_checker = MediaConchPolicyCheckerCommand(
        policy=policy, policy_file_name=POLICY_XML_NAME
    )
    exitcode = policy_checker.check(FILE_PASSES_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert exitcode == 0
    assert output["eventOutcomeInformation"] == "pass"
    assert output["policy"] == policy


def test_no_policy(capsys, tmp_path):
    """Expect a 1 exit code and a fail outcome when the policy file does
    not exist.
    """
    policy_checker = MediaConchPolicyCheckerCommand(
        policy_file_path=str(tmp_path / "fake" / "policy" / "path")
    )
    exitcode = policy_checker.check(FILE_PASSES_PATH)
    captured = capsys.readouterr()
    output = json.loads(captured.err)
    assert exitcode == 1
    assert output["eventOutcomeInformation"] == "fail"
    assert (
        output["eventOutcomeDetailNote"]
        == f"There is no policy file at {tmp_path}/fake/policy/path"
    )
