package com.anka.os;

import android.os.Looper;
import android.os.Binder;
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

            // Ekran Kaplama Parametreleri (TYPE_SYSTEM_ERROR - 2010)
            WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                2010, // TYPE_SYSTEM_ERROR: System/Root UID için en üst katman
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                WindowManager.LayoutParams.FLAG_FULLSCREEN,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.LEFT;
            params.token = new Binder(); // WindowManager token hatasını aşmak için eklenen sahte token

            // Sinek Arayüz Tasarımı (Siberpunk Yeşil / Siyah Katman)
            LinearLayout layout = new LinearLayout(context);
            layout.setBackgroundColor(Color.parseColor("#EE050B14")); // Yarı saydam siberpunk siyah
            layout.setOrientation(LinearLayout.VERTICAL);
            layout.setPadding(60, 200, 60, 60);

            TextView title = new TextView(context);
            title.setText("🪰 ANKA OS v1.0 — SİNEK AKTİF");
            title.setTextColor(Color.GREEN);
            title.setTextSize(24);
            layout.addView(title);

            TextView status = new TextView(context);
            status.setText("\nKUANTUM TOZU: 999\nMOD: OVERLAY KONTROLÜ\nSTATUS: SurfaceFlinger Kilitlendi");
            status.setTextColor(Color.GREEN);
            status.setTextSize(18);
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
