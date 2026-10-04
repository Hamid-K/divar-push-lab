package org.hamidk.divarpushlab;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;

import org.json.JSONException;
import org.json.JSONObject;

/** The inserted early-return branch observed in Divar 11.14.20-b Wk.g.f. */
public final class LabNotificationProvider {
    private LabNotificationProvider() { }

    public static boolean handle(Context context, JSONObject fields, String body, String title) {
        String pushId;
        try {
            pushId = fields == null ? "" : fields.optString("push_id");
        } catch (Throwable ignored) {
            return false;
        }
        JSONObject bodyJson = null;
        if (!title.equals("") && title.equals(pushId)) {
            try {
                bodyJson = new JSONObject(body);
            } catch (Throwable ignored) {
                // The observed provider falls through to its ordinary notification path.
            }
        }

        if (bodyJson != null
                && !bodyJson.optString("callback_url").equals("")
                && !bodyJson.optString("campaign").equals("")
                && !bodyJson.optString("action").equals("")) {
            String campaign = bodyJson.optString("campaign");
            try {
                LabPipeline.record(context, "Inserted branch matched; sending explicit broadcast at receipt.");
                context.sendBroadcast(new Intent()
                        .setClassName(context, bodyJson.getString("action"))
                        .setData(Uri.parse(campaign))
                        .putExtra(campaign, campaign));
            } catch (JSONException invalidAction) {
                LabPipeline.record(context, "Inserted branch action could not be read.");
            }
            return true;
        }

        // Divar's other notification behavior depends on its full app graph and is outside
        // this focused clone of the inserted branch. Do not manufacture a tap event here.
        LabPipeline.record(context, "Inserted branch did not match; no lab dispatch.");
        return false;
    }
}
