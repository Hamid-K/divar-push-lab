package org.hamidk.divarpushlab;

import android.content.Context;
import android.os.Process;
import android.util.Base64;
import android.util.Log;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicBoolean;

/** Benign, fixed-data illustration of a notification-to-stage boundary. */
public final class LabPipeline {
    public static final String PREFS = "lab";
    public static final String KEY_STATUS = "status";
    private static final String TAG = "DivarPushLab";
    private static final String EXPECTED_URL = "http://10.0.2.2:18765/marker";
    private static final byte XOR_KEY = 0x68;
    private static final AtomicBoolean RUNNING = new AtomicBoolean(false);

    private LabPipeline() { }

    public static void run(Context context, String campaign) {
        if (!RUNNING.compareAndSet(false, true)) {
            Log.i(TAG, "Ignored concurrent synthetic event.");
            return;
        }

        File marker = new File(context.getFilesDir(), "lab-marker.txt");
        boolean handled = false;
        String failureMessage = null;
        try {
            record(context, "Receiver equality check matched; benign worker started at receipt.");
            String decoded = decodeCampaign(campaign);
            if (!EXPECTED_URL.equals(decoded)) {
                throw new IllegalStateException("Decoded endpoint failed the local allowlist");
            }
            Log.i(TAG, "Decoded endpoint matched the fixed emulator-host allowlist.");

            JSONObject response = fetchMarker(decoded);
            if (response.length() != 2
                    || !"lab-marker".equals(response.optString("kind"))
                    || !"benign".equals(response.optString("message"))) {
                throw new IllegalStateException("Marker response failed the exact schema check");
            }
            Log.i(TAG, "Received fixed marker from host mock server.");

            try (FileOutputStream output = new FileOutputStream(marker, false)) {
                output.write("divar-lab:benign\n".getBytes(StandardCharsets.UTF_8));
            }
            Log.i(TAG, "Wrote fixed non-executable marker in app-private storage.");
            PrecompiledMarkerHandler.handle(marker);
            handled = true;
        } catch (Exception failure) {
            Log.e(TAG, "Lab pipeline stopped: " + failure.getMessage(), failure);
            failureMessage = failure.getMessage();
        } finally {
            boolean cleaned = !marker.exists() || marker.delete();
            if (!cleaned) {
                Log.w(TAG, "Could not delete marker: " + marker.getAbsolutePath());
            } else {
                Log.i(TAG, "Marker cleanup complete.");
            }
            if (handled && cleaned) {
                record(context, "PASS: fixed marker fetched, written, handled inside UID "
                        + Process.myUid() + ", then cleaned up.");
            } else if (failureMessage != null) {
                record(context, "STOPPED: " + failureMessage);
            } else {
                record(context, "STOPPED: marker cleanup failed.");
            }
            RUNNING.set(false);
        }
    }

    public static void record(Context context, String message) {
        Log.i(TAG, message);
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .edit().putString(KEY_STATUS, message).apply();
    }

    private static String decodeCampaign(String campaign) {
        byte[] decoded = Base64.decode(campaign, Base64.DEFAULT);
        for (int i = 0; i < decoded.length; i++) decoded[i] ^= XOR_KEY;
        return new String(decoded, StandardCharsets.UTF_8);
    }

    private static JSONObject fetchMarker(String endpoint) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(endpoint).openConnection();
        connection.setRequestMethod("GET");
        connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(3000);
        connection.setReadTimeout(3000);
        try {
            if (connection.getResponseCode() != 200) {
                throw new IllegalStateException("Local marker server returned HTTP "
                        + connection.getResponseCode());
            }
            try (InputStream input = connection.getInputStream()) {
                ByteArrayOutputStream body = new ByteArrayOutputStream();
                byte[] chunk = new byte[128];
                int count;
                while ((count = input.read(chunk)) != -1) {
                    if (body.size() + count > 512) {
                        throw new IllegalStateException("Marker response exceeded 512 bytes");
                    }
                    body.write(chunk, 0, count);
                }
                return new JSONObject(body.toString(StandardCharsets.UTF_8.name()));
            }
        } finally {
            connection.disconnect();
        }
    }
}
