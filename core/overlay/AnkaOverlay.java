package com.anka.os;

import android.os.Looper;
import android.os.Handler;
import android.os.Binder;
import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.MotionEvent;
import android.view.WindowManager;
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
    private static EditText chatInput;
    private static LinearLayout chatBoxArea;
    private static LinearLayout rootLayout;
    private static WindowManager windowManager;
    private static WindowManager.LayoutParams rootParams;
    private static Handler mainHandler;

    public static void main(String[] args) {
        // Çökme Koruması: Genel Istisna Yakalayıcı
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override
            public void uncaughtException(Thread t, Throwable e) {
                System.out.println("● [ANKA_OVERLAY HATA YAKALANDI]: " + e.getMessage());
            }
        });

        Looper.prepareMainLooper();
        mainHandler = new Handler(Looper.getMainLooper());

        try {
            Typeface safeFont = Typeface.MONOSPACE;

            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            final Context context = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            windowManager = (WindowManager) context.getSystemService(Context.WINDOW_SERVICE);

            int windowType = 2038; // TYPE_APPLICATION_OVERLAY
            try {
                if (android.os.Build.VERSION.SDK_INT < 26) {
                    windowType = 2010;
                }
            } catch (Throwable ignored) {}

            rootParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.MATCH_PARENT,
                windowType,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN |
                WindowManager.LayoutParams.FLAG_FULLSCREEN,
                PixelFormat.TRANSLUCENT
            );
            rootParams.gravity = Gravity.TOP | Gravity.LEFT;
            rootParams.token = new Binder();

            // Ana Dikey Katman
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

            // 3. SİNEK İLE CANLI SOHBET GİRDİ KUTUSU
            chatBoxArea = new LinearLayout(context);
            chatBoxArea.setOrientation(LinearLayout.HORIZONTAL);
            chatBoxArea.setVisibility(View.GONE); // Varsayılan gizli
            chatBoxArea.setPadding(0, 10, 0, 10);

            chatInput = new EditText(context);
            chatInput.setHint("Sinek'e mesaj yaz...");
            chatInput.setHintTextColor(Color.parseColor("#8800FF00"));
            chatInput.setTextColor(Color.GREEN);
            chatInput.setBackgroundColor(Color.parseColor("#33003300"));
            chatInput.setTextSize(14);
            chatInput.setPadding(20, 15, 20, 15);
            chatInput.setFocusable(true);
            chatInput.setFocusableInTouchMode(true);
            if (safeFont != null) chatInput.setTypeface(safeFont);

            LinearLayout.LayoutParams inputParams = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
            chatBoxArea.addView(chatInput, inputParams);

            TextView btnSend = new TextView(context);
            btnSend.setText("GÖNDER");
            btnSend.setTextColor(Color.BLACK);
            btnSend.setBackgroundColor(Color.GREEN);
            btnSend.setTextSize(13);
            btnSend.setGravity(Gravity.CENTER);
            btnSend.setPadding(25, 15, 25, 15);
            if (safeFont != null) btnSend.setTypeface(safeFont);

            btnSend.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    try {
                        String msg = chatInput.getText().toString().trim();
                        if (!msg.isEmpty()) {
                            sendSinekMessage(msg);
                            chatInput.setText("");
                            if (thoughtView != null) {
                                thoughtView.setText("💬 SEN: " + msg + "\n🪰 Sinek düşünüyor...");
                            }
                        }
                        toggleKeyboardFocus(false);
                        chatBoxArea.setVisibility(View.GONE);
                    } catch (Throwable ignored) {}
                }
            });

            chatBoxArea.addView(btnSend);
            rootLayout.addView(chatBoxArea);

            // 4. DOKUNMATİK BUTONLAR
            LinearLayout btnRow = new LinearLayout(context);
            btnRow.setOrientation(LinearLayout.HORIZONTAL);
            btnRow.setGravity(Gravity.CENTER);

            TextView btnMod = createSafeCyberButton(context, "⚡ MOD", safeFont, "CMD_MOD");
            TextView btnScan = createSafeCyberButton(context, "🔍 TARA", safeFont, "CMD_SCAN");
            TextView btnSohbet = createSafeCyberButton(context, "💬 SOHBET", safeFont, "CMD_SOHBET");

            btnSohbet.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    try {
                        if (chatBoxArea.getVisibility() == View.GONE) {
                            chatBoxArea.setVisibility(View.VISIBLE);
                            toggleKeyboardFocus(true);
                            chatInput.requestFocus();
                        } else {
                            chatBoxArea.setVisibility(View.GONE);
                            toggleKeyboardFocus(false);
                        }
                    } catch (Throwable ignored) {}
                }
            });

            btnRow.addView(btnMod);
            btnRow.addView(btnScan);
            btnRow.addView(btnSohbet);
            rootLayout.addView(btnRow);

            // 5. ALT DÜŞÜNCE KUTUSU (SİNEK'İN CEVAP ALANI)
            LinearLayout thoughtBox = new LinearLayout(context);
            thoughtBox.setOrientation(LinearLayout.VERTICAL);
            thoughtBox.setBackgroundColor(Color.parseColor("#3300FF00"));
            thoughtBox.setPadding(25, 15, 25, 15);

            TextView thoughtTitle = new TextView(context);
            thoughtTitle.setText(">_ SİNEK DÜŞÜNCELERİ & SOHBET:");
            thoughtTitle.setTextColor(Color.GREEN);
            thoughtTitle.setTextSize(15);
            if (safeFont != null) thoughtTitle.setTypeface(safeFont);
            thoughtBox.addView(thoughtTitle);

            thoughtView = new TextView(context);
            thoughtView.setText("Sinek sohbet moduna hazır. '💬 SOHBET' butonuna basıp yazabilirsin!");
            thoughtView.setTextColor(Color.GREEN);
            thoughtView.setTextSize(13);
            if (safeFont != null) thoughtView.setTypeface(safeFont);
            thoughtBox.addView(thoughtView);

            rootLayout.addView(thoughtBox);

            windowManager.addView(rootLayout, rootParams);

            startStatePoller();

        } catch (Throwable t) {
            t.printStackTrace();
        }

        Looper.loop();
    }

    private static void toggleKeyboardFocus(boolean focusable) {
        try {
            if (focusable) {
                rootParams.flags &= ~WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
            } else {
                rootParams.flags |= WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;
            }
            if (windowManager != null && rootLayout != null) {
                windowManager.updateViewLayout(rootLayout, rootParams);
            }
        } catch (Throwable ignored) {}
    }

    private static TextView createSafeCyberButton(Context context, String text, Typeface font, final String cmd) {
        final TextView btn = new TextView(context);
        btn.setText(text);
        btn.setTextColor(Color.GREEN);
        btn.setBackgroundColor(Color.parseColor("#44003300"));
        btn.setTextSize(13);
        btn.setGravity(Gravity.CENTER);
        btn.setPadding(20, 25, 20, 25);
        if (font != null) btn.setTypeface(font);

        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        p.setMargins(6, 0, 6, 0);
        btn.setLayoutParams(p);

        if (!cmd.equals("CMD_SOHBET")) {
            btn.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    try {
                        if (event.getAction() == MotionEvent.ACTION_DOWN) {
                            btn.setBackgroundColor(Color.parseColor("#8800FF00"));
                            sendAnkaCommand(cmd);
                        } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                            btn.setBackgroundColor(Color.parseColor("#44003300"));
                        }
                    } catch (Throwable ignored) {}
                    return true;
                }
            });
        }

        return btn;
    }

    private static void sendAnkaCommand(String cmd) {
        try {
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter writer = new FileWriter(cmdFile, false);
            writer.write(cmd);
            writer.close();
        } catch (Throwable ignored) {}
    }

    private static void sendSinekMessage(String msg) {
        try {
            File chatFile = new File("/data/local/tmp/anka_chat_in.txt");
            FileWriter writer = new FileWriter(chatFile, false);
            writer.write(msg);
            writer.close();
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
