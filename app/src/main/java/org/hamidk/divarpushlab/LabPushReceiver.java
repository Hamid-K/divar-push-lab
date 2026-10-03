package org.hamidk.divarpushlab;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** A fixed synthetic push event receiver, exported for the lab's external trigger. */
public final class LabPushReceiver extends BroadcastReceiver {
    public static final String ACTION = "org.hamidk.divarpushlab.SIMULATE_PUSH";
    public static final String EXTRA_NONCE = "nonce";
    public static final String NONCE = "divar-lab";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || !ACTION.equals(intent.getAction())
                || !NONCE.equals(intent.getStringExtra(EXTRA_NONCE))) {
            LabPipeline.record(context, "Rejected synthetic event: action or nonce mismatch.");
            return;
        }

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
