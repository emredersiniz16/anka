package com.anka.os.launcher;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;

/**
 * ANKA OS Launcher — Ana ekran Activity.
 * Sistem tarafından HOME ekranı olarak seçilir.
 * Arka planda AnkaService başlatılır.
 */
public class LauncherActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Tam ekran, durum çubuğu gizli
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        );

        setContentView(R.layout.activity_launcher);

        // Arka plan servisini başlat
        Intent serviceIntent = new Intent(this, AnkaService.class);
        startForegroundService(serviceIntent);
    }

    @Override
    public void onBackPressed() {
        // Geri tuşu launcher'dan çıkmasın
    }
}
