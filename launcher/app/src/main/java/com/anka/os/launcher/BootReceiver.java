package com.anka.os.launcher;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/**
 * Boot alıcı: Cihaz açıldığında AnkaService'i başlatır.
 */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action) ||
            "android.intent.action.LOCKED_BOOT_COMPLETED".equals(action)) {
            Intent serviceIntent = new Intent(context, AnkaService.class);
            context.startForegroundService(serviceIntent);
        }
    }
}
