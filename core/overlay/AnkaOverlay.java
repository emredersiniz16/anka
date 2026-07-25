package com.anka.os;

import android.os.Looper;
import android.os.Binder;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;
import android.widget.LinearLayout;

public class AnkaOverlay {
    public static void main(String[] args) {
        Looper.prepareMainLooper();
        
        System.out.println("🪰 [ANKA_OVERLAY]: WindowManager Overlay başlatılıyor...");

        try {
            // 1. Native Font Motorunu Güvenceye Al (Skia Crash Önleyici)
            Typeface safeFont = Typeface.MONOSPACE;

            // 2. Android System Context Al
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            Context context = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            WindowManager windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

            // WindowManager Parametreleri
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

            // Sinek Arayüz Tasarımı (Siberpunk Yeşil / Siyah Katman)
            LinearLayout layout = new LinearLayout(context);
            layout.setBackgroundColor(Color.parseColor("#EE050B14"));
            layout.setOrientation(LinearLayout.VERTICAL);
            layout.setPadding(60, 200, 60, 60);

            TextView title = new TextView(context);
            title.setText("🪰 ANKA OS v1.0 — SİNEK AKTİF");
            title.setTextColor(Color.GREEN);
            title.setTextSize(24);
            if (safeFont != null) title.setTypeface(safeFont);
            layout.addView(title);

            TextView status = new TextView(context);
            status.setText("\nKUANTUM TOZU: 999\nMOD: OVERLAY KONTROLÜ\nSTATUS: SurfaceFlinger Kilitlendi");
            status.setTextColor(Color.GREEN);
            status.setTextSize(18);
            if (safeFont != null) status.setTypeface(safeFont);
            layout.addView(status);

            // Katmanı Ekrana Bas
            windowManager.addView(layout, params);
            System.out.println("🪰 [ANKA_OVERLAY]: Katman ekrana BAŞARIYLA EKLENDİ!");

        } catch (Throwable t) {
            System.out.println("🪰 [ANKA_OVERLAY] HATA:");
            t.printStackTrace();
        }

        Looper.loop();
    }
}
