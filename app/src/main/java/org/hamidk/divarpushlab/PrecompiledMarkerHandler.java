package org.hamidk.divarpushlab;

import android.os.Process;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/** Compiled into the APK. It does not load code from the fetched data. */
public final class PrecompiledMarkerHandler {
    private static final String TAG = "DivarPushLab";

    private PrecompiledMarkerHandler() { }

    public static void handle(File marker) throws Exception {
        if (!"lab-marker.txt".equals(marker.getName())) {
            throw new IllegalArgumentException("Unexpected marker filename");
        }
        String content;
        try (InputStream input = new FileInputStream(marker)) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] chunk = new byte[64];
            int count;
            while ((count = input.read(chunk)) != -1) {
                if (bytes.size() + count > 64) throw new IllegalStateException("Marker too large");
                bytes.write(chunk, 0, count);
            }
            content = bytes.toString(StandardCharsets.UTF_8.name());
        } catch (FileNotFoundException missing) {
            throw new IllegalStateException("Expected marker not found", missing);
        }
        if (!"divar-lab:benign\n".equals(content)) {
            throw new IllegalStateException("Marker content mismatch");
        }

        Log.i(TAG, "Precompiled handler consumed fixed marker; UID=" + Process.myUid()
                + "; SELinux=" + readSelinuxContext()
                + "; no external code or native binary executed.");
    }

    private static String readSelinuxContext() {
        try (InputStream input = new FileInputStream("/proc/self/attr/current")) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] chunk = new byte[64];
            int count;
            while ((count = input.read(chunk)) != -1 && bytes.size() < 256) {
                bytes.write(chunk, 0, Math.min(count, 256 - bytes.size()));
            }
            return bytes.toString(StandardCharsets.UTF_8.name()).trim();
        } catch (Exception unavailable) {
            return "unavailable (" + unavailable.getClass().getSimpleName() + ")";
        }
    }
}
