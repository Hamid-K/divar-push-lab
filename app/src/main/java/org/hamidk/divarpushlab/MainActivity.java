package org.hamidk.divarpushlab;

import android.Manifest;
import android.app.Activity;
import android.app.NotificationManager;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.FirebaseApp;
import com.google.firebase.messaging.FirebaseMessaging;

/** Setup and observation screen. It never invokes the marker pipeline. */
public final class MainActivity extends Activity {
    private static final int NOTIFICATION_PERMISSION_REQUEST = 33;
    private final Handler uiHandler = new Handler(Looper.getMainLooper());
    private final Runnable statusPoll = new Runnable() {
        @Override
        public void run() {
            if (status != null) refreshStatus();
            uiHandler.postDelayed(this, 500);
        }
    };

    private TextView cloudState;
    private TextView installationId;
    private TextView permissionState;
    private TextView status;
    private Button copyId;
    private Button allowNotifications;
    private boolean cloudConfigured;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        int pad = Math.round(20 * getResources().getDisplayMetrics().density);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setPadding(pad, pad, pad, pad);
        column.setBackgroundColor(Color.rgb(17, 26, 43));

        TextView title = new TextView(this);
        title.setText("Cloud push delivery lab");
        title.setTextSize(25);
        title.setTypeface(null, Typeface.BOLD);
        title.setTextColor(Color.WHITE);
        column.addView(title, matchWrap());

        TextView explanation = new TextView(this);
        explanation.setText("FCM data message → Android notification → your tap → fixed local marker → precompiled in-app handler → cleanup. No Divar code, downloaded executable, or privilege escalation is present.");
        explanation.setTextSize(15);
        explanation.setTextColor(Color.rgb(193, 205, 222));
        explanation.setPadding(0, pad / 2, 0, pad);
        column.addView(explanation, matchWrap());

        cloudState = bodyText();
        column.addView(cloudState, matchWrap());

        installationId = bodyText();
        installationId.setTextIsSelectable(true);
        installationId.setPadding(0, pad / 2, 0, 0);
        column.addView(installationId, matchWrap());

        Button refreshId = new Button(this);
        refreshId.setText("Refresh cloud registration");
        refreshId.setOnClickListener(view -> registerWithFcm());
        column.addView(refreshId, matchWrap());

        copyId = new Button(this);
        copyId.setText("Copy registered FID");
        copyId.setOnClickListener(view -> copyInstallationId());
        column.addView(copyId, matchWrap());

        permissionState = bodyText();
        permissionState.setPadding(0, pad / 2, 0, 0);
        column.addView(permissionState, matchWrap());

        allowNotifications = new Button(this);
        allowNotifications.setText("Allow Android notifications");
        allowNotifications.setOnClickListener(view -> requestNotificationPermission());
        column.addView(allowNotifications, matchWrap());

        Button refreshStatus = new Button(this);
        refreshStatus.setText("Refresh lab status");
        refreshStatus.setOnClickListener(view -> refreshStatus());
        column.addView(refreshStatus, matchWrap());

        status = bodyText();
        status.setTextSize(18);
        status.setTypeface(null, Typeface.BOLD);
        status.setTextColor(Color.rgb(177, 227, 206));
        status.setPadding(0, pad / 2, 0, 0);
        column.addView(status, matchWrap());

        TextView footer = new TextView(this);
        footer.setText("Cloud target: Firebase Installation ID (FID)\nHost marker: 127.0.0.1:18765  •  Emulator alias: 10.0.2.2\nLogcat tag: DivarPushLab");
        footer.setTextSize(13);
        footer.setTextColor(Color.rgb(158, 173, 196));
        footer.setPadding(0, pad, 0, 0);
        column.addView(footer, matchWrap());

        ScrollView scroll = new ScrollView(this);
        scroll.addView(column);
        setContentView(scroll);

        cloudConfigured = FirebaseApp.initializeApp(this) != null;
        refreshPermissionUi();
        refreshInstallationIdUi();
        refreshStatus();
        if (cloudConfigured) {
            registerWithFcm();
        } else {
            cloudState.setText("Cloud push is not configured. Add a fresh lab app/google-services.json and rebuild.");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (permissionState != null) refreshPermissionUi();
        if (installationId != null) refreshInstallationIdUi();
        if (status != null) refreshStatus();
        uiHandler.removeCallbacks(statusPoll);
        uiHandler.postDelayed(statusPoll, 500);
    }

    @Override
    protected void onPause() {
        uiHandler.removeCallbacks(statusPoll);
        super.onPause();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                           int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == NOTIFICATION_PERMISSION_REQUEST) refreshPermissionUi();
    }

    private void registerWithFcm() {
        if (!cloudConfigured) {
            cloudState.setText("Cloud push is not configured. Add app/google-services.json and rebuild.");
            return;
        }
        cloudState.setText("Registering this lab installation with FCM...");
        FirebaseMessaging.getInstance().register().addOnCompleteListener(this, task -> {
            if (task.isSuccessful()) {
                cloudState.setText("FCM registration succeeded. The registered FID is shown below when its callback arrives.");
                installationId.postDelayed(this::refreshInstallationIdUi, 1200);
                installationId.postDelayed(this::refreshInstallationIdUi, 4200);
            } else {
                String reason = task.getException() == null ? "unknown error"
                        : task.getException().getClass().getSimpleName();
                cloudState.setText("FCM registration failed (" + reason + "). Check the lab Firebase config and emulator Google APIs.");
            }
        });
    }

    private void refreshInstallationIdUi() {
        String fid = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabFirebaseMessagingService.KEY_FID, "");
        copyId.setEnabled(fid != null && !fid.isEmpty());
        if (fid == null || fid.isEmpty()) {
            installationId.setText("No registered Firebase Installation ID yet.");
        } else {
            String suffix = fid.substring(Math.max(0, fid.length() - 4));
            installationId.setText("Registered FID: ••••" + suffix
                    + "\nUse Copy registered FID to target this emulator.");
        }
    }

    private void copyInstallationId() {
        String fid = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabFirebaseMessagingService.KEY_FID, "");
        if (fid == null || fid.isEmpty()) return;
        ClipboardManager clipboard = getSystemService(ClipboardManager.class);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("Lab FCM FID", fid));
            Toast.makeText(this, "Registered FID copied", Toast.LENGTH_SHORT).show();
        }
    }

    private void requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},
                    NOTIFICATION_PERMISSION_REQUEST);
        } else {
            refreshPermissionUi();
        }
    }

    private void refreshPermissionUi() {
        NotificationManager manager = getSystemService(NotificationManager.class);
        boolean runtimeGranted = Build.VERSION.SDK_INT < 33
                || checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                == PackageManager.PERMISSION_GRANTED;
        boolean enabled = manager != null && manager.areNotificationsEnabled();
        if (runtimeGranted && enabled) {
            permissionState.setText("Android notifications are allowed. A qualifying FCM message can appear in the notification shade.");
        } else if (!runtimeGranted) {
            permissionState.setText("Android notification permission is needed before the cloud message can be shown.");
        } else {
            permissionState.setText("Notifications are disabled in Android settings for this app.");
        }
        allowNotifications.setVisibility(Build.VERSION.SDK_INT >= 33 && !runtimeGranted
                ? View.VISIBLE : View.GONE);
    }

    private void refreshStatus() {
        String latest = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabPipeline.KEY_STATUS, "No cloud message has reached the lab yet.");
        if (latest.startsWith("PASS:")) {
            status.setTextColor(Color.rgb(132, 235, 174));
        } else if (latest.startsWith("STOPPED:") || latest.startsWith("Rejected")) {
            status.setTextColor(Color.rgb(255, 180, 152));
        } else {
            status.setTextColor(Color.rgb(177, 227, 206));
        }
        status.setText(latest);
    }

    private TextView bodyText() {
        TextView result = new TextView(this);
        result.setTextSize(15);
        result.setTextColor(Color.rgb(193, 205, 222));
        return result;
    }

    private static LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
    }
}
