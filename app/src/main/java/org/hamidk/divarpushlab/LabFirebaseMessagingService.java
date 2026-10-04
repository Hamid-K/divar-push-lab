package org.hamidk.divarpushlab;

import android.util.Log;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.Map;

/** The observed Divar FCM source routing, using a fresh lab Firebase project. */
public final class LabFirebaseMessagingService extends FirebaseMessagingService {
    public static final String KEY_TOKEN = "fcm_token";
    private static final String TAG = "DivarPushLab";

    @Override
    public void onNewToken(String token) {
        if (token == null || token.isEmpty()) {
            Log.w(TAG, "FCM registration callback returned an empty token.");
            return;
        }
        getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE).edit()
                .putString(KEY_TOKEN, token).apply();
        Log.i(TAG, "FCM registration token saved locally for test targeting.");
    }

    @Override
    public void onMessageReceived(RemoteMessage message) {
        Map<String, String> data = message.getData();
        String source = data.containsKey("source") ? data.get("source") : "";
        if ("webengage".equals(source)) {
            // Divar hands this case to the WebEngage SDK. The lab has no WebEngage project.
            LabPipeline.record(this, "WebEngage source delegated; lab has no WebEngage SDK.");
            return;
        }
        if (!"divar".equals(source) && !"default".equals(source)) {
            LabPipeline.record(this, "FCM source ignored by observed Divar routing.");
            return;
        }

        JSONObject fields = new JSONObject();
        try {
            for (Map.Entry<String, String> entry : data.entrySet()) {
                fields.put(entry.getKey(), entry.getValue());
            }
        } catch (JSONException invalidData) {
            LabPipeline.record(this, "FCM data could not be normalized to JSON.");
            return;
        }
        LabNotificationProvider.handle(this, fields,
                fields.optString("body"), fields.optString("title"));
    }
}
