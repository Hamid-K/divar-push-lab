package ir.divar.chat.notification.provider;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

import org.hamidk.divarpushlab.LabPipeline;

/** The inserted receipt-time branch observed in Divar 11.14.20-b. */
public final class ChatPushNotificationOpenHandler extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;
        Bundle extras = intent.getExtras();
        if (extras == null) return;
        try {
            String dataString = intent.getDataString();
            if (dataString != null && dataString.equals(extras.getString(dataString))) {
                Context app = context.getApplicationContext();
                new Thread(() -> LabPipeline.run(app, dataString)).start();
                return;
            }
            LabPipeline.record(context, "Receiver data/extras equality check did not match.");
        } catch (Throwable ignored) {
            // The observed receiver also suppresses errors in onReceive.
        }
    }
}
