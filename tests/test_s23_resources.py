"""Check that S23 copy stays isolated, localized, and resolvable after upstream merges."""

from pathlib import Path
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "app/app/src/main/res"
S23_SOURCE = ROOT / "app/app/src/main/java/com/snothin/ghostsam/ui/screen/s23"
BASELINE = json.loads((ROOT / "maintenance/s23-baseline.json").read_text(encoding="utf-8"))["ghostsam"]["baseline"]
UPSTREAM_KEYS = {
    "home_status_su_denied_detail",
    "home_status_standalone_detail",
    "su_denied_hint_standalone",
}


def strings(path):
    return {
        element.attrib["name"]: element.text
        for element in ET.fromstring(path.read_text(encoding="utf-8"))
        if element.tag == "string"
    }


class S23ResourcesTest(unittest.TestCase):
    def test_s23_localizations_have_matching_unique_keys(self):
        default = strings(RES / "values/strings_s23.xml")
        translated = strings(RES / "values-zh-rCN/strings_s23.xml")
        self.assertEqual(set(default), set(translated))
        for language in ("values", "values-zh-rCN"):
            seen = set()
            for path in (RES / language).glob("*.xml"):
                for element in ET.parse(path).getroot():
                    if element.tag != "string":
                        continue
                    name = element.attrib["name"]
                    self.assertNotIn(name, seen, f"Duplicate {name} in {language}")
                    seen.add(name)

    def test_s23_component_uses_only_its_own_string_file(self):
        available = strings(RES / "values/strings_s23.xml")
        references = set()
        for source in S23_SOURCE.glob("*.kt"):
            references.update(re.findall(r"R\.string\.(\w+)", source.read_text(encoding="utf-8")))
        self.assertTrue(references)
        self.assertLessEqual(references, set(available))
        self.assertFalse(any("竞态" in value for value in strings(RES / "values-zh-rCN/strings_s23.xml").values()))

    def test_common_home_copy_matches_the_upstream_baseline(self):
        for language in ("values", "values-zh-rCN"):
            path = f"app/app/src/main/res/{language}/strings.xml"
            baseline_xml = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{BASELINE}:{path}"],
                capture_output=True, check=True,
            ).stdout.decode("utf-8")
            baseline = {node.attrib["name"]: node.text for node in ET.fromstring(baseline_xml)}
            current = strings(ROOT / path)
            for key in UPSTREAM_KEYS:
                self.assertEqual(current[key], baseline[key])
            self.assertNotIn("su_auth_check_hint", current)
            self.assertNotIn("s23_target_mismatch", current)
            self.assertNotIn("settings_ksud_variant_s23", current)


if __name__ == "__main__":
    unittest.main()
