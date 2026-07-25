package com.com.anka.os;

import android.os.Looper;
import android.os.Handler;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;
import android.widget.LinearLayout;

public class AnkaOverlay {
    public static void main(String[] args) {
        Looper.prepareMainLooper();
        
        System.out.println("🪰 [ANKA_OVERLAY]: WindowManager Overlay başlatılıyor...");

        try {
            // Android System Context üzerinden WindowManager Servisini Al
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            Context context = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            WindowManager windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

            // Ekran Kaplama Parametreleri (TYPE_SECURE_SYSTEM_OVERLAY / TYPE_APPLICATION_OVERLAY)
            WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                2038, // TYPE_APPLICATION_OVERLAY
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL |
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.LEFT;

            // Sinek Artyüz Tasarımı (Siberpunk Yeşil / Siyah Katman)
            LinearLayout layout = new LinearLayout(context);
            layout.setBackgroundColor(Color.parseColor("#EE050B14")); // Yarı saydam siberpunk siyah
            layout.setOrientation(LinearLayout.VERTICAL);
            layout.setPadding(50, 150, 50, 50);

            TextView title = new TextView(context);
            title.setText("🪰 ANKA OS v1.0 — SİNEK AKTİF");
            title.setTextColor(Color.GREEN);
            title.setTextSize(22);
            layout.addView(title);

            TextView status = new TextView(context);
            status.setText("\nKUANTUM TOZU: 999\nMOD: OVERLAY KONTROLÜ\nSTATUS: SurfaceFlinger Stabil");
            status.setTextColor(Color.GREEN);
            status.setTextSize(16);
            layout.addView(status);

            // Katmanı Ekrana Bas
            windowManager.addView(layout, params);
            System.out.println("🪰 [ANKA_OVERLAY]: Katman ekrana kilitlendi!");

        } catch (Exception e) {
            System.out.println("🪰 [ANKA_OVERLAY] HATA: " + e.getMessage());
            e.printStackTrace();
        }

        Looper.loop();
    }
}
