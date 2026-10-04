package org.hamidk.divarpushlab;

import android.util.Log;

import com.onesignal.NotificationExtenderService;
import com.onesignal.OSNotificationPayload;
import com.onesignal.OSNotificationReceivedResult;

/** Original 3.15.3 SDK callback and normalization into the same provider branch. */
public final class LabOneSignalExtenderService extends NotificationExtenderService {
    @Override
    protected boolean onNotificationProcessing(OSNotificationReceivedResult received) {
        OSNotificationPayload payload = received == null ? null : received.payload;
        if (payload != null && payload.body != null && payload.title != null) {
            Log.i("DivarPushLab", "OneSignal extender received normalized payload.");
            // SDK 3.15.3 has already parsed raw.custom.a into additionalData,
            // raw.alert into body, and raw.title into title.
            LabNotificationProvider.handle(this, payload.additionalData,
                    payload.body, payload.title);
        }
        // Lab-only compatibility shim: stock OneSignal 3.15.3 creates a
        // PendingIntent without the mutability flag required on Android 12+.
        // Suppress only its notification display after the cloned provider
        // has run on receipt. The sampled app's normal display path is not cloned.
        return true;
    }
}
