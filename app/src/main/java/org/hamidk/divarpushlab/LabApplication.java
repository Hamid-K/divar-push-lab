package org.hamidk.divarpushlab;

import android.app.Application;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.util.Log;

import com.onesignal.OneSignal;
import com.onesignal.OSPermissionSubscriptionState;
import com.onesignal.OSSubscriptionState;

/** Starts the original OneSignal SDK generation only for a configured lab app. */
public final class LabApplication extends Application {
    public static final String KEY_ONESIGNAL_PLAYER_ID = "onesignal_player_id";
    public static final String KEY_ONESIGNAL_SUBSCRIBED = "onesignal_subscribed";
    public static final String KEY_ONESIGNAL_PUSH_TOKEN_PRESENT = "onesignal_push_token_present";

    @Override
    public void onCreate() {
        super.onCreate();
        try {
            ApplicationInfo app = getPackageManager().getApplicationInfo(
                    getPackageName(), PackageManager.GET_META_DATA);
            String oneSignalAppId = app.metaData == null ? null
                    : app.metaData.getString("onesignal_app_id");
            String senderId = app.metaData == null ? null
                    : app.metaData.getString("onesignal_google_project_number");
            if (oneSignalAppId != null && !oneSignalAppId.isEmpty()
                    && senderId != null && senderId.matches("(str:)?[0-9]+")) {
                OneSignal.startInit(this).init();
                OneSignal.addSubscriptionObserver(changes -> {
                    OSSubscriptionState to = changes.getTo();
                    if (to != null) saveSubscription(to);
                });
                OSPermissionSubscriptionState state = OneSignal.getPermissionSubscriptionState();
                if (state != null && state.getSubscriptionStatus() != null) {
                    saveSubscription(state.getSubscriptionStatus());
                }
                Log.i("DivarPushLab", "OneSignal 3.15.3 lab transport initialized.");
            }
        } catch (PackageManager.NameNotFoundException missing) {
            Log.e("DivarPushLab", "Could not read lab OneSignal metadata.", missing);
        }
    }

    private void saveSubscription(OSSubscriptionState subscription) {
        String playerId = subscription.getUserId();
        boolean tokenPresent = subscription.getPushToken() != null
                && !subscription.getPushToken().isEmpty();
        boolean subscribed = subscription.getSubscribed();
        getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE).edit()
                .putString(KEY_ONESIGNAL_PLAYER_ID, playerId == null ? "" : playerId)
                .putBoolean(KEY_ONESIGNAL_PUSH_TOKEN_PRESENT, tokenPresent)
                .putBoolean(KEY_ONESIGNAL_SUBSCRIBED, subscribed).apply();
        Log.i("DivarPushLab", "OneSignal state saved: subscribed=" + subscribed
                + ", push token present=" + tokenPresent + ".");
    }
}
