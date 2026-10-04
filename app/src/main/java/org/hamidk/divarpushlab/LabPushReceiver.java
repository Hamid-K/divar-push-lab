package org.hamidk.divarpushlab;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Runs the fixed marker path only after the user taps this app's notification. */
public final class LabPushReceiver extends BroadcastReceiver {
    public static final String ACTION = "org.hamidk.divarpushlab.CLOUD_NOTIFICATION_TAP";
    public static final String EXTRA_NONCE = "nonce";
    public static final String NONCE = "divar-lab";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || !ACTION.equals(intent.getAction())
                || !NONCE.equals(intent.getStringExtra(EXTRA_NONCE))) {
            LabPipeline.record(context, "Rejected notification tap: action or nonce mismatch.");
            return;
        }

        LabPipeline.record(context, "Android notification tapped; starting fixed marker pipeline.");
        PendingResult pending = goAsync();
        Context app = context.getApplicationContext();
        new Thread(() -> {
            try {
                LabPipeline.run(app);
            } finally {
                pending.finish();
            }
        }, "lab-push-pipeline").start();
    }
}
