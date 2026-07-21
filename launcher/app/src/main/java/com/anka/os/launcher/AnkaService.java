package com.anka.os.launcher;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

/**
 * ANKA OS arka plan servisi.
 * Sistem hayatta tutulması için foreground service olarak çalışır.
 * Native anka_os binary'yi başlatır (eğer /system/bin/anka_os varsa).
 */
public class AnkaService extends Service {

    private static final String TAG = "AnkaService";
    private static final String CHANNEL_ID = "anka_os_channel";
    private static final int NOTIF_ID = 1;

    private Process ankaProcess = null;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(NOTIF_ID, buildNotification());
        Log.i(TAG, "AnkaService başladı.");
        launchNativeBinary();
    }

    /** /system/bin/anka_os binary'sini arka planda başlatır. */
    private void launchNativeBinary() {
        try {
            java.io.File bin = new java.io.File("/system/bin/anka_os");
            if (!bin.exists()) {
                Log.w(TAG, "/system/bin/anka_os bulunamadı — native servis atlanıyor.");
                return;
            }
            ProcessBuilder pb = new ProcessBuilder("/system/bin/anka_os");
            pb.redirectErrorStream(true);
            ankaProcess = pb.start();
            Log.i(TAG, "anka_os binary başlatıldı, PID kontrolü aktif.");
        } catch (Exception e) {
            Log.e(TAG, "Native binary başlatılamadı: " + e.getMessage());
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        if (ankaProcess != null) {
            ankaProcess.destroy();
        }
        super.onDestroy();
        Log.i(TAG, "AnkaService durduruldu.");
    }

    private void createNotificationChannel() {
        NotificationChannel channel = new NotificationChannel(
            CHANNEL_ID,
            "Anka OS",
            NotificationManager.IMPORTANCE_LOW
        );
        channel.setDescription("Anka OS arka plan servisi");
        NotificationManager nm = getSystemService(NotificationManager.class);
        if (nm != null) nm.createNotificationChannel(channel);
    }

    private Notification buildNotification() {
        return new Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Anka OS")
            .setContentText("Sistem aktif")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
            .build();
    }
}
