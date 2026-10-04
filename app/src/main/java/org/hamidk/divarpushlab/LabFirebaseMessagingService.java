package org.hamidk.divarpushlab;

import android.Manifest;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

/** Accepts only the lab's data-only FCM envelope and posts a real notification. */
public final class LabFirebaseMessagingService extends FirebaseMessagingService {
    public static final String KEY_FID = "registered_fid";
    public static final String DATA_ACTION = "lab_action";
    public static final String DATA_NONCE = "lab_nonce";
    public static final String ACTION_VALUE = "deliver_marker";

    private static final String TAG = "DivarPushLab";
    private static final String CHANNEL_ID = "cloud_marker_lab";
    private static final int NOTIFICATION_ID = 2001;
    private static final int TAP_REQUEST_CODE = 2001;

    @Override
    public void onRegistered(String installationId) {
        if (installationId == null || installationId.isEmpty()) {
            Log.w(TAG, "FCM registration callback returned an empty installation ID.");
            return;
        }
        getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE).edit()
                .putString(KEY_FID, installationId).apply();
        Log.i(TAG, "FCM installation registered; identifier saved locally for test targeting.");
    }

    @Override
    public void onMessageReceived(RemoteMessage message) {
        Map<String, String> data = message.getData();
        if (message.getNotification() != null || data.size() != 2
                || !ACTION_VALUE.equals(data.get(DATA_ACTION))
                || !LabPushReceiver.NONCE.equals(data.get(DATA_NONCE))) {
            LabPipeline.record(this, "Rejected FCM message: expected exact data-only action and nonce.");
            return;
        }

        NotificationManager manager = getSystemService(NotificationManager.class);
        if (manager == null) {
            LabPipeline.record(this, "FCM data accepted, but notification service is unavailable.");
            return;
        }
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            LabPipeline.record(this, "FCM data accepted, but notification permission is missing.");
            return;
        }
        if (!manager.areNotificationsEnabled()) {
            LabPipeline.record(this, "FCM data accepted, but notifications are disabled.");
            return;
        }

        NotificationChannel channel = new NotificationChannel(CHANNEL_ID,
                "Cloud marker lab", NotificationManager.IMPORTANCE_DEFAULT);
        channel.setDescription("Benign lab notifications from a fresh Firebase test project");
        manager.createNotificationChannel(channel);

        Intent tapIntent = new Intent(this, LabPushReceiver.class);
        tapIntent.setAction(LabPushReceiver.ACTION);
        tapIntent.putExtra(LabPushReceiver.EXTRA_NONCE, LabPushReceiver.NONCE);
        PendingIntent tap = PendingIntent.getBroadcast(this, TAP_REQUEST_CODE, tapIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notification = new Notification.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Cloud lab message received")
                .setContentText("Tap to run the fixed, benign marker step")
                .setContentIntent(tap)
                .setAutoCancel(true)
                .setOnlyAlertOnce(true)
                .setCategory(Notification.CATEGORY_STATUS)
                .build();
        try {
            manager.notify(NOTIFICATION_ID, notification);
            LabPipeline.record(this, "FCM data gate accepted; Android notification posted. Tap it to continue.");
        } catch (SecurityException permissionRace) {
            LabPipeline.record(this, "FCM data accepted, but Android denied notification display.");
            Log.w(TAG, "Notification permission changed while posting", permissionRace);
        }
    }
}
