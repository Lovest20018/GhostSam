package com.snothin.ghostsam.ui.screen.s23

internal enum class S23HomeStatus {
    Checking,
    ManagerMissing,
    Ready,
    Working,
    AwaitingGrant,
    Enabled,
}

internal enum class S23HomeAction {
    None,
    Run,
    OpenManager,
    ShowProgress,
}

internal data class S23HomeState(
    val status: S23HomeStatus,
    val action: S23HomeAction,
) {
    val showAuthorizationHint: Boolean
        get() = status == S23HomeStatus.Ready || status == S23HomeStatus.AwaitingGrant
}

/** S23 presentation rules only. A failed su probe does not prove that the module is absent. */
internal fun resolveS23HomeState(
    running: Boolean,
    managerInstalled: Boolean,
    suProbeDone: Boolean,
    suAvailable: Boolean,
    kernelLoaded: Boolean,
): S23HomeState = when {
    running -> S23HomeState(S23HomeStatus.Working, S23HomeAction.ShowProgress)
    !managerInstalled -> S23HomeState(S23HomeStatus.ManagerMissing, S23HomeAction.None)
    !suProbeDone -> S23HomeState(S23HomeStatus.Checking, S23HomeAction.None)
    suAvailable -> S23HomeState(S23HomeStatus.Enabled, S23HomeAction.OpenManager)
    kernelLoaded -> S23HomeState(S23HomeStatus.AwaitingGrant, S23HomeAction.OpenManager)
    else -> S23HomeState(S23HomeStatus.Ready, S23HomeAction.Run)
}
