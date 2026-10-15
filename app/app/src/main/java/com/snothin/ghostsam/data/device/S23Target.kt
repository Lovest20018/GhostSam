package com.snothin.ghostsam.data.device

/** Scope of the dedicated S23 build; independent of Android runtime for testing. */
internal object S23Target {
    const val MODEL = "SM-S9110"
    const val DISPLAY = "BP4A.251205.006.S9110ZCS8FZI1"
    const val RELEASE = "5.15.189-android13-8-3251900-abS9110ZCS8FZI1"
    const val KMI = "android13-5.15"
    const val SDK = 36

    fun matches(model: String, display: String, release: String, sdk: Int): Boolean =
        model == MODEL && display == DISPLAY && release == RELEASE && sdk == SDK
}
