"""Packaging failures that could silently reintroduce the old driver."""

import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify-s23-apk.py"
SPEC = importlib.util.spec_from_file_location("verify_s23_apk", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def elf(elf_type, size):
    data = bytearray(size)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<HH", data, 16, elf_type, 183)
    return bytes(data)


class S23ApkTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ksud = self.root / "ksud"
        self.module = self.root / "dfr.ko"
        self.apk = self.root / "app.apk"
        self.ksud.write_bytes(elf(3, 64) + b"(uapi: 5)")
        self.module.write_bytes(elf(1, 4096))
        self.entries = {
            checker.KSUD_ASSET: self.ksud.read_bytes(),
            checker.DFR_ASSET: self.module.read_bytes(),
            "lib/arm64-v8a/libgsdfr_app.so": b"jni",
        }

    def check(self):
        with zipfile.ZipFile(self.apk, "w") as archive:
            for name, data in self.entries.items():
                archive.writestr(name, data)
        return checker.verify(self.apk, self.ksud, self.module)

    def test_accepts_matching_build_inputs(self):
        self.assertEqual(set(self.check()), {checker.KSUD_ASSET, checker.DFR_ASSET})

    def test_rejects_old_daemon_even_when_input_was_rebuilt(self):
        self.entries[checker.KSUD_ASSET] = elf(3, 64) + b"(uapi: 2)"
        with self.assertRaisesRegex(ValueError, "differs"):
            self.check()

    def test_rejects_old_daemon_in_build_input(self):
        self.ksud.write_bytes(elf(3, 64) + b"(uapi: 2)")
        with self.assertRaisesRegex(ValueError, "UAPI 5"):
            self.check()

    def test_rejects_extra_kmi_or_variant(self):
        for name in (
            "assets/payloads/ksud/ksud-next",
            "assets/payloads/dirtyfrag/dfr_lkm-android16-6.12.ko",
        ):
            with self.subTest(name=name):
                self.entries[name] = b"extra"
                with self.assertRaisesRegex(ValueError, "payload set"):
                    self.check()
                del self.entries[name]

    def test_rejects_missing_module(self):
        del self.entries[checker.DFR_ASSET]
        with self.assertRaisesRegex(ValueError, "payload set"):
            self.check()

    def test_rejects_companion_and_missing_jni(self):
        self.entries["assets/companion/companion.apk"] = b"extra"
        with self.assertRaisesRegex(ValueError, "companion"):
            self.check()
        del self.entries["assets/companion/companion.apk"]
        del self.entries["lib/arm64-v8a/libgsdfr_app.so"]
        with self.assertRaisesRegex(ValueError, "JNI"):
            self.check()

    def test_rejects_wrong_architecture(self):
        data = bytearray(self.module.read_bytes())
        struct.pack_into("<H", data, 18, 62)
        self.module.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "AArch64"):
            self.check()


if __name__ == "__main__":
    unittest.main()
