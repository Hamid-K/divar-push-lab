package org.hamidk.divarpushlab;

import android.os.Process;
import android.system.ErrnoException;
import android.system.Os;
import android.system.OsConstants;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileDescriptor;
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
        if (!"divar-lab:simulated-lpe\n".equals(content)) {
            throw new IllegalStateException("Marker content mismatch");
        }

        int uidBefore = Process.myUid();
        String contextBefore = readSelinuxContext();
        Log.i(TAG, "Running simulated LPE payload... stage marker validated; UID="
                + uidBefore + "; SELinux=" + contextBefore);
        Log.i(TAG, "Simulated LPE boundary probe: read-only open of system-private"
                + " package registry; no file contents are read.");
        probePrivilegedReadBoundary();
        int uidAfter = Process.myUid();
        String contextAfter = readSelinuxContext();
        if (uidBefore != uidAfter || !contextBefore.equals(contextAfter)) {
            throw new IllegalStateException("Process identity changed unexpectedly; simulation stopped");
        }
        Log.i(TAG, "Simulated LPE stage complete; UID unchanged=" + (uidBefore == uidAfter)
                + "; SELinux context unchanged=" + contextBefore.equals(contextAfter)
                + "; app sandbox retained; no exploit or external code executed.");
    }

    private static void probePrivilegedReadBoundary() {
        final String path = "/data/system/packages.xml";
        FileDescriptor descriptor;
        try {
            descriptor = Os.open(path, OsConstants.O_RDONLY, 0);
        } catch (ErrnoException error) {
            if (error.errno == OsConstants.EACCES || error.errno == OsConstants.EPERM) {
                Log.i(TAG, "Simulated LPE boundary probe: privileged read denied (expected);"
                        + " no bytes read.");
                return;
            }
            throw new IllegalStateException("Privileged read probe inconclusive (errno "
                    + error.errno + "); simulation stopped", error);
        }
        try {
            Log.e(TAG, "Simulated LPE boundary probe: privileged file unexpectedly opened;"
                    + " simulation stopped without reading it.");
            throw new IllegalStateException("Unexpected privileged file access; simulation stopped");
        } finally {
            try {
                Os.close(descriptor);
            } catch (ErrnoException closeError) {
                Log.e(TAG, "Could not close privileged read probe descriptor", closeError);
            }
        }
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
