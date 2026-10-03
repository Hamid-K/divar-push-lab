package org.hamidk.divarpushlab;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

public final class MainActivity extends Activity {
    private TextView status;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);

        int pad = Math.round(20 * getResources().getDisplayMetrics().density);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setPadding(pad, pad, pad, pad);
        column.setBackgroundColor(Color.rgb(17, 26, 43));

        TextView title = new TextView(this);
        title.setText("Divar push delivery lab");
        title.setTextSize(25);
        title.setTypeface(null, Typeface.BOLD);
        title.setTextColor(Color.WHITE);
        column.addView(title, matchWrap());

        TextView explanation = new TextView(this);
        explanation.setText("Synthetic notification event → fixed local marker → precompiled in-app handler → cleanup. This app contains no Divar code, downloaded executable, or privilege escalation.");
        explanation.setTextSize(15);
        explanation.setTextColor(Color.rgb(193, 205, 222));
        explanation.setPadding(0, pad / 2, 0, pad);
        column.addView(explanation, matchWrap());

        Button simulate = new Button(this);
        simulate.setText("Simulate valid push");
        simulate.setOnClickListener(view -> sendLabEvent(LabPushReceiver.NONCE));
        column.addView(simulate, matchWrap());

        Button reject = new Button(this);
        reject.setText("Run rejected control");
        reject.setOnClickListener(view -> sendLabEvent("invalid-nonce"));
        column.addView(reject, matchWrap());

        Button refresh = new Button(this);
        refresh.setText("Refresh status");
        refresh.setOnClickListener(view -> refreshStatus());
        column.addView(refresh, matchWrap());

        status = new TextView(this);
        status.setTextSize(15);
        status.setTextColor(Color.rgb(177, 227, 206));
        status.setPadding(0, pad, 0, 0);
        column.addView(status, matchWrap());

        TextView footer = new TextView(this);
        footer.setText("Host server: 127.0.0.1:18765  •  Emulator alias: 10.0.2.2\nLogcat tag: DivarPushLab");
        footer.setTextSize(13);
        footer.setTextColor(Color.rgb(158, 173, 196));
        footer.setPadding(0, pad, 0, 0);
        column.addView(footer, matchWrap());

        ScrollView scroll = new ScrollView(this);
        scroll.addView(column);
        setContentView(scroll);
        refreshStatus();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (status != null) refreshStatus();
    }

    private void sendLabEvent(String nonce) {
        Intent event = new Intent(this, LabPushReceiver.class);
        event.setAction(LabPushReceiver.ACTION);
        event.putExtra(LabPushReceiver.EXTRA_NONCE, nonce);
        sendBroadcast(event);
        status.setText("Synthetic event sent. Waiting for the local marker server...");
        status.postDelayed(this::refreshStatus, 1200);
        status.postDelayed(this::refreshStatus, 4200);
    }

    private void refreshStatus() {
        String latest = getSharedPreferences(LabPipeline.PREFS, MODE_PRIVATE)
                .getString(LabPipeline.KEY_STATUS, "No lab event has run yet.");
        status.setText(latest);
    }

    private static LinearLayout.LayoutParams matchWrap() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
    }
}
