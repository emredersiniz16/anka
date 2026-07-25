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
    private static TextView headerView;
    private static TextView middleView;
    private static TextView thoughtView;
    private static Handler mainHandler;

    public static void main(String[] args) {
        Looper.prepareMainLooper();
        mainHandler = new Handler(Looper.getMainLooper());
        
        System.out.println("● [ANKA_OVERLAY]: Siberpunk HUD Başlatılıyor...");

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

            // Ana Dikey Katman (Tam Ekran Artyüz)
            LinearLayout rootLayout = new LinearLayout(context);
            rootLayout.setBackgroundColor(Color.parseColor("#EE050B14")); // Yarı saydam yeşil/siyah
            rootLayout.setOrientation(LinearLayout.VERTICAL);
            rootLayout.setPadding(40, 100, 40, 60);

            // 1. ÜST BAR: ANKA OS | SAAT | PİL
            headerView = new TextView(context);
            headerView.setText("● ANKA OS v1.0  |  SAAT: --:--  |  PİL: %--");
            headerView.setTextColor(Color.GREEN);
            headerView.setTextSize(16);
            if (safeFont != null) headerView.setTypeface(safeFont);
            rootLayout.addView(headerView);

            // Üst Çizgi
            LinearLayout topDivider = new LinearLayout(context);
            topDivider.setBackgroundColor(Color.GREEN);
            LinearLayout.LayoutParams divParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 4);
            divParams.setMargins(0, 15, 0, 40);
            rootLayout.addView(topDivider, divParams);

            // 2. ORTA BÖLÜM: KUANTUM TOZU & MOD
            middleView = new TextView(context);
            middleView.setText("\nKUANTUM TOZU: ---  |  MOD: YÜKLENİYOR...");
            middleView.setTextColor(Color.GREEN);
            middleView.setTextSize(18);
            if (safeFont != null) middleView.setTypeface(safeFont);
            rootLayout.addView(middleView);

            // Esnek Boşluk (Aşağıya İtici)
            LinearLayout spacer = new LinearLayout(context);
            LinearLayout.LayoutParams spacerParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            rootLayout.addView(spacer, spacerParams);

            // 3. ALT BÖLÜM: SİNEK DÜŞÜNCELERİ KUTUSU
            LinearLayout thoughtBox = new LinearLayout(context);
            thoughtBox.setOrientation(LinearLayout.VERTICAL);
            thoughtBox.setBackgroundColor(Color.parseColor("#3300FF00")); // Yarı saydam yeşil kutu
            thoughtBox.setPadding(30, 20, 30, 20);

            TextView thoughtTitle = new TextView(context);
            thoughtTitle.setText(">_ SİNEK DÜŞÜNCELERİ:");
            thoughtTitle.setTextColor(Color.GREEN);
            thoughtTitle.setTextSize(16);
            if (safeFont != null) thoughtTitle.setTypeface(safeFont);
            thoughtBox.addView(thoughtTitle);

            thoughtView = new TextView(context);
            thoughtView.setText("Sistem başlatılıyor...");
            thoughtView.setTextColor(Color.GREEN);
            thoughtView.setTextSize(14);
            if (safeFont != null) thoughtView.setTypeface(safeFont);
            thoughtBox.addView(thoughtView);

            rootLayout.addView(thoughtBox);

            windowManager.addView(rootLayout, params);
            System.out.println("● [ANKA_OVERLAY]: HUD tasarımı başarıyla ekrana çakıldı!");

            // Canlı Dinleyiciyi Başlat
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
                            String line;
                            String time = "--:--", battery = "--", dust = "0", mode = "--", thought = "--";

                            while ((line = reader.readLine()) != null) {
                                if (line.startsWith("TIME:")) time = line.substring(6).trim();
                                else if (line.startsWith("BATTERY:")) battery = line.substring(8).trim();
                                else if (line.startsWith("DUST:")) dust = line.substring(5).trim();
                                else if (line.startsWith("MODE:")) mode = line.substring(5).trim();
                                else if (line.startsWith("THOUGHT:")) thought = line.substring(8).trim();
                            }
                            reader.close();

                            final String headerText = "● ANKA OS v1.0  |  SAAT: " + time + "  |  PİL: %" + battery;
                            final String middleText = "\nKUANTUM TOZU: " + dust + "  |  MOD: " + mode;
                            final String thoughtText = thought;

                            mainHandler.post(new Runnable() {
                                @Override
                                int run() { // Lambda/Runnable güncellemesi
                                    return 0;
                                }
                            });

                            mainHandler.post(new Runnable() {
                                @Override
                                public void run() {
                                    if (headerView != null) headerView.setText(headerText);
                                    if (middleView != null) middleView.setText(middleText);
                                    if (thoughtView != null) thoughtView.setText(thoughtText);
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
