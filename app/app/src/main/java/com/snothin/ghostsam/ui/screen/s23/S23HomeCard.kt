package com.snothin.ghostsam.ui.screen.s23

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AdminPanelSettings
import androidx.compose.material.icons.rounded.AutoAwesome
import androidx.compose.material.icons.rounded.Bolt
import androidx.compose.material.icons.rounded.CheckCircleOutline
import androidx.compose.material.icons.rounded.Info
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.snothin.ghostsam.R
import com.snothin.ghostsam.ui.screen.SuDeniedConnectCard
import com.snothin.ghostsam.ui.theme.StatusColors
import com.snothin.ghostsam.ui.theme.isInDarkTheme
import top.yukonga.miuix.kmp.basic.Card
import top.yukonga.miuix.kmp.basic.Icon
import top.yukonga.miuix.kmp.basic.Text
import top.yukonga.miuix.kmp.theme.MiuixTheme
import top.yukonga.miuix.kmp.utils.PressFeedbackType

@Composable
internal fun S23HomeStatusCard(
    state: S23HomeState,
    rootInfo: String,
    onClick: () -> Unit,
) {
    val (title, detail) = when (state.status) {
        S23HomeStatus.Checking -> R.string.s23_home_checking to R.string.s23_home_checking_detail
        S23HomeStatus.ManagerMissing -> R.string.s23_home_manager_missing to R.string.s23_home_manager_missing_detail
        S23HomeStatus.Ready -> R.string.s23_home_ready to R.string.s23_home_ready_detail
        S23HomeStatus.Working -> R.string.s23_home_working to R.string.s23_home_working_detail
        S23HomeStatus.AwaitingGrant -> R.string.s23_home_awaiting_grant to R.string.s23_home_awaiting_grant_detail
        S23HomeStatus.Enabled -> R.string.s23_home_enabled to R.string.s23_home_enabled_detail
    }
    val isDark = isInDarkTheme()
    val colors = when (state.status) {
        S23HomeStatus.Checking, S23HomeStatus.Working -> StatusColors(
            MiuixTheme.colorScheme.primaryContainer,
            MiuixTheme.colorScheme.onPrimaryContainer,
        )
        S23HomeStatus.ManagerMissing, S23HomeStatus.AwaitingGrant -> StatusColors.warning(isDark)
        S23HomeStatus.Ready, S23HomeStatus.Enabled -> StatusColors.success(isDark)
    }
    val icon = when (state.status) {
        S23HomeStatus.Checking, S23HomeStatus.ManagerMissing -> Icons.Rounded.Info
        S23HomeStatus.Ready -> Icons.Rounded.Bolt
        S23HomeStatus.Working -> Icons.Rounded.AutoAwesome
        S23HomeStatus.AwaitingGrant -> Icons.Rounded.AdminPanelSettings
        S23HomeStatus.Enabled -> Icons.Rounded.CheckCircleOutline
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick,
        showIndication = state.action != S23HomeAction.None,
        pressFeedbackType = PressFeedbackType.Tilt,
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 105.dp)
                .background(colors.container)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = colors.content,
                    modifier = Modifier.size(24.dp),
                )
                Text(
                    text = stringResource(title),
                    fontSize = 23.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = colors.content,
                )
            }
            Text(
                text = stringResource(detail),
                fontSize = 15.sp,
                color = colors.content.copy(alpha = 0.85f),
            )
            if (state.status == S23HomeStatus.Enabled && rootInfo.isNotBlank()) {
                Text(
                    text = rootInfo,
                    fontSize = 13.sp,
                    color = colors.content.copy(alpha = 0.8f),
                )
            }
        }
    }
}

@Composable
internal fun S23HomeAuthorizationHint(
    state: S23HomeState,
    onOpenManager: () -> Unit,
) {
    SuDeniedConnectCard(
        onClick = onOpenManager,
        hintRes = if (state.status == S23HomeStatus.AwaitingGrant) {
            R.string.s23_home_grant_hint
        } else {
            R.string.s23_home_check_grant_hint
        },
    )
}
