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
        // The preserved extender continues the SDK's normal processing after
        // calling the provider. The inserted provider branch itself has returned.
        return false;
    }
}
