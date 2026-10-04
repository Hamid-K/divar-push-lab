package org.hamidk.divarpushlab;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
    private final Handler uiHandler = new Handler(Looper.getMainLooper());
    private final Runnable statusPoll = new Runnable() {
        @Override
        public void run() {
            if (status != null) refreshStatus();
            if (oneSignalPlayerId != null) refreshOneSignalPlayerUi();
            uiHandler.postDelayed(this, 500);
        }
    };

    private TextView cloudState;
    private TextView installationId;
    private TextView oneSignalPlayerId;
    private TextView status;
    private Button copyId;
    private Button copyPlayerId;
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
        explanation.setText("FCM data push or OneSignal 3.15.3 push → shared Divar title/push_id and body checks → explicit broadcast → receiver → fixed local marker. The inserted branch runs on receipt, with no tap. The post-receiver worker is a benign lab substitute.");
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
        copyId.setText("Copy FCM token");
        copyId.setOnClickListener(view -> copyInstallationId());
        column.addView(copyId, matchWrap());

        oneSignalPlayerId = bodyText();
        oneSignalPlayerId.setPadding(0, pad / 2, 0, 0);
        column.addView(oneSignalPlayerId, matchWrap());

        copyPlayerId = new Button(this);
        copyPlayerId.setText("Copy OneSignal player ID");
        copyPlayerId.setOnClickListener(view -> copyOneSignalPlayerId());
        column.addView(copyPlayerId, matchWrap());

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
        footer.setText("Cloud targets: FCM token or OneSignal player ID\nHost marker: 127.0.0.1:18765  •  Emulator alias: 10.0.2.2\nLogcat tag: DivarPushLab");
        footer.setTextSize(13);
        footer.setTextColor(Color.rgb(158, 173, 196));
        footer.setPadding(0, pad, 0, 0);
        column.addView(footer, matchWrap());

        ScrollView scroll = new ScrollView(this);
        scroll.addView(column);
        setContentView(scroll);

        cloudConfigured = FirebaseApp.initializeApp(this) != null;
        refreshInstallationIdUi();
        refreshOneSignalPlayerUi();
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
        if (installationId != null) refreshInstallationIdUi();
        if (oneSignalPlayerId != null) refreshOneSignalPlayerUi();
        if (status != null) refreshStatus();
        uiHandler.removeCallbacks(statusPoll);
        uiHandler.postDelayed(statusPoll, 500);
    }

    @Override
    protected void onPause() {
        uiHandler.removeCallbacks(statusPoll);
        super.onPause();
    }

    private void registerWithFcm() {
        if (!cloudConfigured) {
            cloudState.setText("Cloud push is not configured. Add app/google-services.json and rebuild.");
            return;
        }
        cloudState.setText("Registering this lab installation with FCM...");
        FirebaseMessaging.getInstance().getToken().addOnCompleteListener(this, task -> {
            if (task.isSuccessful()) {
                String token = task.getResult();
                if (token != null && !token.isEmpty()) {
                    getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE).edit()
                            .putString(LabFirebaseMessagingService.KEY_TOKEN, token).apply();
                    cloudState.setText("FCM registration succeeded. Token saved locally.");
                    refreshInstallationIdUi();
                } else {
                    cloudState.setText("FCM registration returned no token.");
                }
            } else {
                String reason = task.getException() == null ? "unknown error"
                        : task.getException().getClass().getSimpleName();
                cloudState.setText("FCM registration failed (" + reason + "). Check the lab Firebase config and emulator Google APIs.");
            }
        });
    }

    private void refreshInstallationIdUi() {
        String token = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabFirebaseMessagingService.KEY_TOKEN, "");
        copyId.setEnabled(token != null && !token.isEmpty());
        if (token == null || token.isEmpty()) {
            setTextIfChanged(installationId, "No FCM registration token yet.");
        } else {
            String suffix = token.substring(Math.max(0, token.length() - 4));
            setTextIfChanged(installationId, "FCM token: ••••" + suffix
                    + "\nUse Copy FCM token to target this emulator.");
        }
    }

    private void copyInstallationId() {
        String token = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabFirebaseMessagingService.KEY_TOKEN, "");
        if (token == null || token.isEmpty()) return;
        ClipboardManager clipboard = getSystemService(ClipboardManager.class);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("Lab FCM token", token));
            Toast.makeText(this, "FCM token copied", Toast.LENGTH_SHORT).show();
        }
    }

    private void refreshOneSignalPlayerUi() {
        String playerId = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabApplication.KEY_ONESIGNAL_PLAYER_ID, "");
        boolean tokenPresent = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getBoolean(LabApplication.KEY_ONESIGNAL_PUSH_TOKEN_PRESENT, false);
        boolean subscribed = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getBoolean(LabApplication.KEY_ONESIGNAL_SUBSCRIBED, false);
        copyPlayerId.setEnabled(playerId != null && !playerId.isEmpty() && subscribed);
        if (playerId == null || playerId.isEmpty()) {
            setTextIfChanged(oneSignalPlayerId,
                    "No OneSignal player ID yet. Configure the fresh lab OneSignal app and wait for registration.");
        } else {
            String suffix = playerId.substring(Math.max(0, playerId.length() - 4));
            setTextIfChanged(oneSignalPlayerId, "OneSignal 3.15.3 player ID: ••••" + suffix
                    + "\nPush token present: " + tokenPresent + "  •  Subscribed: " + subscribed
                    + "\nThe full ID remains only in local app preferences.");
        }
    }

    private void copyOneSignalPlayerId() {
        String playerId = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabApplication.KEY_ONESIGNAL_PLAYER_ID, "");
        if (playerId == null || playerId.isEmpty()) return;
        ClipboardManager clipboard = getSystemService(ClipboardManager.class);
        if (clipboard != null) {
            clipboard.setPrimaryClip(ClipData.newPlainText("Lab OneSignal player ID", playerId));
            Toast.makeText(this, "OneSignal player ID copied", Toast.LENGTH_SHORT).show();
        }
    }

    private void refreshStatus() {
        String latest = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabPipeline.KEY_STATUS, "No cloud message has reached the lab yet.");
        if (latest.startsWith("PASS:")) {
            status.setTextColor(Color.rgb(132, 235, 174));
        } else if (latest.startsWith("STOPPED:") || latest.startsWith("Rejected")
                || latest.startsWith("Inserted branch did not match")) {
            status.setTextColor(Color.rgb(255, 180, 152));
        } else {
            status.setTextColor(Color.rgb(177, 227, 206));
        }
        setTextIfChanged(status, latest);
    }

    private static void setTextIfChanged(TextView target, String value) {
        if (!value.contentEquals(target.getText())) target.setText(value);
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
