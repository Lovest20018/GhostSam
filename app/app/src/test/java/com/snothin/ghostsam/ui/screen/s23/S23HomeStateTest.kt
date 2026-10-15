package com.snothin.ghostsam.ui.screen.s23

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class S23HomeStateTest {
    private fun state(
        running: Boolean = false,
        managerInstalled: Boolean = true,
        suProbeDone: Boolean = true,
        suAvailable: Boolean = false,
        kernelLoaded: Boolean = false,
    ) = resolveS23HomeState(running, managerInstalled, suProbeDone, suAvailable, kernelLoaded)

    @Test
    fun firstUseOffersExecutionAndConditionalAuthorizationGuidance() {
        val result = state()
        assertEquals(S23HomeStatus.Ready, result.status)
        assertEquals(S23HomeAction.Run, result.action)
        assertTrue(result.showAuthorizationHint)
    }

    @Test
    fun loadedButUnauthorizedSessionOpensManagerInsteadOfExecutingAgain() {
        val result = state(kernelLoaded = true)
        assertEquals(S23HomeStatus.AwaitingGrant, result.status)
        assertEquals(S23HomeAction.OpenManager, result.action)
        assertTrue(result.showAuthorizationHint)
    }

    @Test
    fun grantingSuEnablesHomeEvenWhenSamsungHidesTheModule() {
        val result = state(suAvailable = true)
        assertEquals(S23HomeStatus.Enabled, result.status)
        assertEquals(S23HomeAction.OpenManager, result.action)
        assertFalse(result.showAuthorizationHint)
    }

    @Test
    fun inFlightProbePreventsStartingASecondRun() {
        val result = state(suProbeDone = false, kernelLoaded = true)
        assertEquals(S23HomeStatus.Checking, result.status)
        assertEquals(S23HomeAction.None, result.action)
        assertFalse(result.showAuthorizationHint)
    }

    @Test
    fun anActiveRunAlwaysOpensProgressEvenIfRootAppearsMidRun() {
        val result = state(running = true, suAvailable = true, kernelLoaded = true)
        assertEquals(S23HomeStatus.Working, result.status)
        assertEquals(S23HomeAction.ShowProgress, result.action)
        assertFalse(result.showAuthorizationHint)
    }

    @Test
    fun aMissingManagerPreventsExecution() {
        val result = state(managerInstalled = false)
        assertEquals(S23HomeStatus.ManagerMissing, result.status)
        assertEquals(S23HomeAction.None, result.action)
    }

    @Test
    fun fullRebootWithoutLiveEvidenceOffersANewRun() {
        val before = state(suAvailable = true, kernelLoaded = true)
        val after = state()
        assertEquals(S23HomeAction.OpenManager, before.action)
        assertEquals(S23HomeStatus.Ready, after.status)
        assertEquals(S23HomeAction.Run, after.action)
    }

    @Test
    fun noInputCombinationExecutesWhenLoadedOrAuthorized() {
        for (running in listOf(false, true)) {
            for (managerInstalled in listOf(false, true)) {
                for (suProbeDone in listOf(false, true)) {
                    for (suAvailable in listOf(false, true)) {
                        for (kernelLoaded in listOf(false, true)) {
                            val result = state(running, managerInstalled, suProbeDone, suAvailable, kernelLoaded)
                            if (running || !managerInstalled || !suProbeDone || suAvailable || kernelLoaded) {
                                assertFalse(result.action == S23HomeAction.Run)
                            }
                        }
                    }
                }
            }
        }
    }
}
