package com.anka.os;

import android.os.Looper;
import android.os.Handler;
import android.os.Binder;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;
import android.widget.LinearLayout;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;

public class AnkaOverlay {
    private static TextView statusView;
    private static Handler mainHandler;

    public static void main(String[] args) {
        Looper.prepareMainLooper();
        mainHandler = new Handler(Looper.getMainLooper());
        
        System.out.println("● [ANKA_OVERLAY]: Canlı Overlay Başlatılıyor...");

        try {
            Typeface safeFont = Typeface.MONOSPACE;

            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            Context context = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            WindowManager windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

            WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                2010, // TYPE_SYSTEM_ERROR
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                WindowManager.LayoutParams.FLAG_FULLSCREEN,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.LEFT;
            params.token = new Binder();

            LinearLayout layout = new LinearLayout(context);
            layout.setBackgroundColor(Color.parseColor("#EE050B14"));
            layout.setOrientation(LinearLayout.VERTICAL);
            layout.setPadding(60, 200, 60, 60);

            TextView title = new TextView(context);
            title.setText("● ANKA OS v1.0 — SİNEK AKTİF");
            title.setTextColor(Color.GREEN);
            title.setTextSize(22);
            if (safeFont != null) title.setTypeface(safeFont);
            layout.addView(title);

            statusView = new TextView(context);
            statusView.setText("\nKUANTUM TOZU: Yükleniyor...\nMOD: BAŞLATILIYOR...");
            statusView.setTextColor(Color.GREEN);
            statusView.setTextSize(16);
            if (safeFont != null) statusView.setTypeface(safeFont);
            layout.addView(statusView);

            windowManager.addView(layout, params);
            System.out.println("● [ANKA_OVERLAY]: Katman eklendi, canlı veri dinleyici başlatılıyor!");

            // C Çekirdeğinden gelen canlı verileri her 500ms'de bir oku ve ekrana bas
            startStatePoller();

        } catch (Throwable t) {
            System.out.println("● [ANKA_OVERLAY] HATA:");
            t.printStackTrace();
        }

        Looper.loop();
    }

    private static void startStatePoller() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (true) {
                    try {
                        File stateFile = new File("/data/local/tmp/anka_state.txt");
                        if (stateFile.exists()) {
                            BufferedReader reader = new BufferedReader(new FileReader(stateFile));
                            StringBuilder builder = new StringBuilder();
                            String line;
                            while ((line = reader.readLine()) != null) {
                                builder.append(line).append("\n");
                            }
                            reader.close();

                            final String newText = "\n" + builder.toString();

                            // UI Güncellemesini Ana Ekran Thread'inde Yap
                            mainHandler.post(new Runnable() {
                                @Override
                                public void run() {
                                    if (statusView != null) {
                                        statusView.setText(newText);
                                    }
                                }
                            });
                        }
                    } catch (Exception ignored) {
                    }

                    try {
                        Thread.sleep(500);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }).start();
    }
}
