package com.snothin.ghostsam.data.device

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class S23TargetTest {
    @Test
    fun acceptsTheSuppliedFirmware() {
        assertTrue(S23Target.matches(S23Target.MODEL, S23Target.DISPLAY, S23Target.RELEASE, 36))
    }

    @Test
    fun rejectsOtherModelsAndFirmwareEvenWithTheSameKernelFamily() {
        assertFalse(S23Target.matches("SM-S9160", S23Target.DISPLAY, S23Target.RELEASE, 36))
        assertFalse(S23Target.matches("SM-S911B", S23Target.DISPLAY, S23Target.RELEASE, 36))
        assertFalse(S23Target.matches(S23Target.MODEL, "BP4A.251205.006.S9110ZCS8FZH1", S23Target.RELEASE, 36))
        assertFalse(S23Target.matches(S23Target.MODEL, S23Target.DISPLAY, "5.15.189-android13-8", 36))
        assertFalse(S23Target.matches(S23Target.MODEL, S23Target.DISPLAY, S23Target.RELEASE, 35))
        assertFalse(S23Target.matches(S23Target.MODEL, S23Target.DISPLAY, "", 36))
    }
}
