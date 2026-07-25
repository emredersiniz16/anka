package com.anka.os;

import android.os.Looper;
import android.os.Handler;

public class AnkaOverlay {
    public static void main(String[] args) {
        // Android Ana Döngüsünü (Main Looper) Hazırla
        Looper.prepareMainLooper();
        
        System.out.println("🪰 [ANKA_OVERLAY]: app_process uyanıyor...");
        System.out.println("🪰 [ANKA_OVERLAY]: SurfaceControl / Overlay katmanı devreye alınıyor.");

        // Arka plan durum kontrol döngüsü
        Handler handler = new Handler(Looper.myLooper());
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                System.out.println("🪰 [ANKA_OVERLAY]: Sinek Overlay canlı tutuluyor...");
                handler.postDelayed(this, 5000);
            }
        }, 1000);

        // Zygote döngüsünü kilitle (Kapanmasını önler)
        Looper.loop();
    }
}
