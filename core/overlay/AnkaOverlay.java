package com.anka.os;

import android.os.Looper;
import android.os.Handler;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.MotionEvent;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.widget.TextView;
import android.widget.EditText;
import android.widget.LinearLayout;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.io.FileWriter;

public class AnkaOverlay {
    private static TextView headerView;
    private static TextView middleView;
    private static TextView thoughtView;
    private static Handler mainHandler;
    
    // Klavye yönetimi için global değişkenler
    private static WindowManager windowManager;
    private static WindowManager.LayoutParams params;
    private static LinearLayout rootLayout;
    private static LinearLayout inputLayout;
    private static EditText chatInput;

    public static void main(String[] args) {
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override
            public void uncaughtException(Thread t, Throwable e) {
                System.out.println("● [ANKA_OVERLAY] Istisna yakalandi: " + e.getMessage());
            }
        });

        Looper.prepareMainLooper();
        mainHandler = new Handler(Looper.getMainLooper());

        try {
            final Typeface safeFont = Typeface.MONOSPACE;

            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            final Context context = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

            int windowType = 2038;
            try {
                if (android.os.Build.VERSION.SDK_INT < 26) windowType = 2010;
            } catch (Throwable ignored) {}

            params = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                windowType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | // Varsayılan olarak klavye odaklanmaz
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                WindowManager.LayoutParams.FLAG_FULLSCREEN,
                PixelFormat.TRANSLUCENT
            );
            params.gravity = Gravity.TOP | Gravity.LEFT;

            rootLayout = new LinearLayout(context);
            rootLayout.setBackgroundColor(Color.parseColor("#EE050B14"));
            rootLayout.setOrientation(LinearLayout.VERTICAL);
            rootLayout.setPadding(30, 80, 30, 40);

            // 1. ÜST BAR
            headerView = new TextView(context);
            headerView.setText("● ANKA OS v1.0  |  SAAT: --:--  |  PİL: %--");
            headerView.setTextColor(Color.GREEN);
            headerView.setTextSize(15);
            if (safeFont != null) headerView.setTypeface(safeFont);
            rootLayout.addView(headerView);

            // Üst Çizgi
            LinearLayout topDivider = new LinearLayout(context);
            topDivider.setBackgroundColor(Color.GREEN);
            LinearLayout.LayoutParams divParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 3);
            divParams.setMargins(0, 10, 0, 30);
            rootLayout.addView(topDivider, divParams);

            // 2. ORTA BÖLÜM
            middleView = new TextView(context);
            middleView.setText("\nKUANTUM TOZU: ---  |  MOD: YÜKLENİYOR...");
            middleView.setTextColor(Color.GREEN);
            middleView.setTextSize(17);
            if (safeFont != null) middleView.setTypeface(safeFont);
            rootLayout.addView(middleView);

            // Esnek Boşluk
            LinearLayout spacer = new LinearLayout(context);
            LinearLayout.LayoutParams spacerParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            rootLayout.addView(spacer, spacerParams);

            // 3. DOKUNMATİK BUTONLAR
            LinearLayout btnRow = new LinearLayout(context);
            btnRow.setOrientation(LinearLayout.HORIZONTAL);
            btnRow.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams btnRowParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            btnRowParams.setMargins(0, 0, 0, 20);

            TextView btnMod = createSafeCyberButton(context, "⚡ MOD", safeFont, "CMD_MOD");
            TextView btnScan = createSafeCyberButton(context, "🔍 TARA", safeFont, "CMD_SCAN");
            TextView btnSohbet = createSafeCyberButton(context, "💬 SOHBET", safeFont, "CMD_SOHBET");

            btnRow.addView(btnMod);
            btnRow.addView(btnScan);
            btnRow.addView(btnSohbet);
            rootLayout.addView(btnRow, btnRowParams);

            // 4. ALT DÜŞÜNCE KUTUSU
            LinearLayout thoughtBox = new LinearLayout(context);
            thoughtBox.setOrientation(LinearLayout.VERTICAL);
            thoughtBox.setBackgroundColor(Color.parseColor("#3300FF00"));
            thoughtBox.setPadding(25, 15, 25, 15);

            TextView thoughtTitle = new TextView(context);
            thoughtTitle.setText(">_ SİNEK DÜŞÜNCELERİ:");
            thoughtTitle.setTextColor(Color.GREEN);
            thoughtTitle.setTextSize(15);
            if (safeFont != null) thoughtTitle.setTypeface(safeFont);
            thoughtBox.addView(thoughtTitle);

            thoughtView = new TextView(context);
            thoughtView.setText("Sistem çevrimiçi. Dokunmatik sensörler aktif.");
            thoughtView.setTextColor(Color.GREEN);
            thoughtView.setTextSize(13);
            if (safeFont != null) thoughtView.setTypeface(safeFont);
            thoughtBox.addView(thoughtView);

            rootLayout.addView(thoughtBox);

            // 5. GİZLİ SOHBET GİRİŞ ALANI (Sadece SOHBET tuşuna basınca açılır)
            inputLayout = new LinearLayout(context);
            inputLayout.setOrientation(LinearLayout.HORIZONTAL);
            inputLayout.setBackgroundColor(Color.parseColor("#EE001100"));
            inputLayout.setPadding(10, 10, 10, 10);
            inputLayout.setVisibility(View.GONE); // Başlangıçta gizli
            LinearLayout.LayoutParams inputLayoutParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            inputLayoutParams.setMargins(0, 10, 0, 0);

            chatInput = new EditText(context);
            chatInput.setHint("Sinek'e komut ver...");
            chatInput.setHintTextColor(Color.parseColor("#5500FF00"));
            chatInput.setTextColor(Color.GREEN);
            chatInput.setTextSize(14);
            if (safeFont != null) chatInput.setTypeface(safeFont);
            LinearLayout.LayoutParams editParams = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
            chatInput.setLayoutParams(editParams);

            TextView btnSend = new TextView(context);
            btnSend.setText("GÖNDER");
            btnSend.setTextColor(Color.BLACK);
            btnSend.setBackgroundColor(Color.GREEN);
            btnSend.setPadding(20, 20, 20, 20);
            if (safeFont != null) btnSend.setTypeface(safeFont);
            
            btnSend.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    String msg = chatInput.getText().toString();
                    if (!msg.trim().isEmpty()) {
                        // Mesajı dosyaya SOHBET: <mesaj> formatında yaz
                        sendAnkaCommand("SOHBET: " + msg);
                        chatInput.setText(""); // Kutuyu temizle
                    }
                    
                    // İşlem bitince klavyeyi kapat ve kutuyu gizle
                    inputLayout.setVisibility(View.GONE);
                    params.flags |= WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE; // Odak kilidini geri koy
                    windowManager.updateViewLayout(rootLayout, params);
                    
                    try {
                        InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
                        if (imm != null) imm.hideSoftInputFromWindow(chatInput.getWindowToken(), 0);
                    } catch (Exception ignored) {}
                }
            });

            inputLayout.addView(chatInput);
            inputLayout.addView(btnSend);
            rootLayout.addView(inputLayout, inputLayoutParams);

            windowManager.addView(rootLayout, params);

            startStatePoller();

        } catch (Throwable t) {
            t.printStackTrace();
        }

        Looper.loop();
    }

    private static TextView createSafeCyberButton(final Context context, String text, Typeface font, final String cmd) {
        final TextView btn = new TextView(context);
        btn.setText(text);
        btn.setTextColor(Color.GREEN);
        btn.setBackgroundColor(Color.parseColor("#44003300"));
        btn.setTextSize(13);
        btn.setGravity(Gravity.CENTER);
        btn.setPadding(20, 25, 20, 25);
        btn.setClickable(true); 
        if (font != null) btn.setTypeface(font);

        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        p.setMargins(6, 0, 6, 0);
        btn.setLayoutParams(p);

        btn.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                try {
                    if (event.getAction() == MotionEvent.ACTION_DOWN) {
                        btn.setBackgroundColor(Color.parseColor("#8800FF00"));
                        
                        if (cmd.equals("CMD_SOHBET")) {
                            // SOHBET tuşuna basıldığında klavye odaklanmasını aç ve kutuyu göster
                            mainHandler.post(new Runnable() {
                                @Override
                                public void run() {
                                    if (inputLayout.getVisibility() == View.GONE) {
                                        inputLayout.setVisibility(View.VISIBLE);
                                        params.flags &= ~WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE; // Klavyeye izin ver
                                        windowManager.updateViewLayout(rootLayout, params);
                                        chatInput.requestFocus();
                                    } else {
                                        // Zaten açıksa kapat (Toggle mantığı)
                                        inputLayout.setVisibility(View.GONE);
                                        params.flags |= WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
                                        windowManager.updateViewLayout(rootLayout, params);
                                    }
                                }
                            });
                        } else {
                            sendAnkaCommand(cmd);
                        }
                        
                    } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                        btn.setBackgroundColor(Color.parseColor("#44003300"));
                    }
                } catch (Throwable ignored) {}
                return true; 
            }
        });

        return btn;
    }

    private static void sendAnkaCommand(String cmd) {
        try {
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter writer = new FileWriter(cmdFile, false);
            writer.write(cmd + "\n");
            writer.flush();
            writer.close();
            Runtime.getRuntime().exec("chmod 666 /data/local/tmp/anka_cmd.txt");
        } catch (Throwable ignored) {}
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
                                if (line.startsWith("TIME:")) time = line.substring(5).trim();
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
                                public void run() {
                                    try {
                                        if (headerView != null) headerView.setText(headerText);
                                        if (middleView != null) middleView.setText(middleText);
                                        if (thoughtView != null) thoughtView.setText(thoughtText);
                                    } catch (Throwable ignored) {}
                                }
                            });
                        }
                    } catch (Exception ignored) {}

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
