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
import android.widget.LinearLayout;
import android.widget.ScrollView;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.File;
import java.io.FileWriter;

public class AnkaOverlay {
    private static TextView headerView;
    private static TextView middleView;
    private static TextView consoleView;
    private static Handler mainHandler;
    private static WindowManager windowManager;
    private static WindowManager.LayoutParams rootParams;
    private static Context appContext;
    
    private static LinearLayout modalLayout = null;
    private static TextView inputDisplay;
    private static StringBuilder currentMessage = new StringBuilder();

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
            Typeface safeFont = Typeface.MONOSPACE;

            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = activityThreadClass.getMethod("systemMain").invoke(null);
            appContext = (Context) activityThreadClass.getMethod("getSystemContext").invoke(activityThread);

            windowManager = (WindowManager) appContext.getSystemService(Context.WINDOW_SERVICE);

            int windowType = 2038;
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

            LinearLayout rootLayout = new LinearLayout(appContext);
            rootLayout.setBackgroundColor(Color.parseColor("#EE050B14"));
            rootLayout.setOrientation(LinearLayout.VERTICAL);
            rootLayout.setPadding(30, 80, 30, 40);

            // 1. ÜST BAR
            headerView = new TextView(appContext);
            headerView.setText("● ANKA OS v1.0  |  SAAT: --:--  |  PİL: %--");
            headerView.setTextColor(Color.GREEN);
            headerView.setTextSize(15);
            if (safeFont != null) headerView.setTypeface(safeFont);
            rootLayout.addView(headerView);

            LinearLayout topDivider = new LinearLayout(appContext);
            topDivider.setBackgroundColor(Color.GREEN);
            LinearLayout.LayoutParams divParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 3);
            divParams.setMargins(0, 10, 0, 30);
            rootLayout.addView(topDivider, divParams);

            // 2. ORTA BÖLÜM (TOZ VE MOD)
            middleView = new TextView(appContext);
            middleView.setText("KUANTUM TOZU: ---  |  MOD: YÜKLENİYOR...");
            middleView.setTextColor(Color.GREEN);
            middleView.setTextSize(15);
            if (safeFont != null) middleView.setTypeface(safeFont);
            rootLayout.addView(middleView);

            // 3. DEV TERMİNAL EKRANI
            ScrollView scroll = new ScrollView(appContext);
            LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            scrollParams.setMargins(0, 40, 0, 40);

            consoleView = new TextView(appContext);
            consoleView.setText(">_ BAĞLANTI BEKLENİYOR...");
            consoleView.setTextColor(Color.GREEN);
            consoleView.setTextSize(16);
            consoleView.setLineSpacing(0, 1.3f);
            if (safeFont != null) consoleView.setTypeface(safeFont);
            
            scroll.addView(consoleView);
            rootLayout.addView(scroll, scrollParams);

            // 4. DOKUNMATİK BUTONLAR
            LinearLayout btnRow = new LinearLayout(appContext);
            btnRow.setOrientation(LinearLayout.HORIZONTAL);
            btnRow.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams btnRowParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            btnRowParams.setMargins(0, 0, 0, 20);

            TextView btnMod = createSafeCyberButton(appContext, "⚡ MOD", safeFont, "CMD_MOD");
            TextView btnScan = createSafeCyberButton(appContext, "🔍 TARA", safeFont, "CMD_SCAN");
            
            final TextView btnSohbet = new TextView(appContext);
            btnSohbet.setText("💬 SOHBET");
            btnSohbet.setTextColor(Color.GREEN);
            btnSohbet.setBackgroundColor(Color.parseColor("#44003300"));
            btnSohbet.setTextSize(13);
            btnSohbet.setGravity(Gravity.CENTER);
            btnSohbet.setPadding(20, 25, 20, 25);
            if (safeFont != null) btnSohbet.setTypeface(safeFont);
            LinearLayout.LayoutParams pSohbet = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
            pSohbet.setMargins(6, 0, 6, 0);
            btnSohbet.setLayoutParams(pSohbet);

            btnSohbet.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    try {
                        if (event.getAction() == MotionEvent.ACTION_DOWN) {
                            btnSohbet.setBackgroundColor(Color.parseColor("#8800FF00"));
                            toggleChatModal();
                        } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                            btnSohbet.setBackgroundColor(Color.parseColor("#44003300"));
                        }
                    } catch (Throwable ignored) {}
                    return true;
                }
            });

            btnRow.addView(btnMod);
            btnRow.addView(btnScan);
            btnRow.addView(btnSohbet);
            rootLayout.addView(btnRow, btnRowParams);

            windowManager.addView(rootLayout, rootParams);

            startStatePoller();

        } catch (Throwable t) {
            t.printStackTrace();
        }

        Looper.loop();
    }

    private static void toggleChatModal() {
        try {
            if (modalLayout != null) {
                windowManager.removeView(modalLayout);
                modalLayout = null;
                return;
            }

            modalLayout = new LinearLayout(appContext);
            modalLayout.setOrientation(LinearLayout.VERTICAL);
            modalLayout.setBackgroundColor(Color.parseColor("#F5050B14"));
            modalLayout.setPadding(40, 40, 40, 40);
            modalLayout.setGravity(Gravity.CENTER);

            Typeface safeFont = Typeface.MONOSPACE;

            TextView title = new TextView(appContext);
            title.setText("💬 SİNEK ÖZEL MESAJ KUTUSU");
            title.setTextColor(Color.GREEN);
            title.setTextSize(16);
            if (safeFont != null) title.setTypeface(safeFont);
            title.setGravity(Gravity.CENTER);
            title.setPadding(0, 0, 0, 20);
            modalLayout.addView(title);

            inputDisplay = new TextView(appContext);
            inputDisplay.setText("Yazmak için harflere dokun...");
            inputDisplay.setTextColor(Color.parseColor("#00FF00"));
            inputDisplay.setBackgroundColor(Color.parseColor("#33003300"));
            inputDisplay.setTextSize(15);
            inputDisplay.setPadding(20, 20, 20, 20);
            if (safeFont != null) inputDisplay.setTypeface(safeFont);
            
            LinearLayout.LayoutParams dispParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 120);
            dispParams.setMargins(0, 0, 0, 20);
            modalLayout.addView(inputDisplay, dispParams);

            addKeyboardRow(new String[]{"A", "B", "C", "D", "E", "F", "G", "H", "İ"});
            addKeyboardRow(new String[]{"J", "K", "L", "M", "N", "O", "P", "R", "S"});
            addKeyboardRow(new String[]{"Ş", "T", "U", "Ü", "V", "Y", "Z", "BOŞLUK", "SİL"});
            addKeyboardRow(new String[]{"KAPAT", "GÖNDER"});

            WindowManager.LayoutParams modalParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                rootParams.type,
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            );
            modalParams.gravity = Gravity.BOTTOM;

            windowManager.addView(modalLayout, modalParams);

        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    private static void addKeyboardRow(String[] keys) {
        LinearLayout row = new LinearLayout(appContext);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        rowParams.setMargins(0, 5, 0, 5);

        for (final String key : keys) {
            final TextView btn = new TextView(appContext);
            btn.setText(key);
            btn.setTextColor(Color.GREEN);
            btn.setBackgroundColor(Color.parseColor("#44004400"));
            btn.setTextSize(12);
            btn.setGravity(Gravity.CENTER);
            btn.setPadding(10, 18, 10, 18);

            LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
            btnParams.setMargins(3, 0, 3, 0);
            btn.setLayoutParams(btnParams);

            btn.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    try {
                        if (event.getAction() == MotionEvent.ACTION_DOWN) {
                            btn.setBackgroundColor(Color.parseColor("#8800FF00"));
                            handleKeyClick(key);
                        } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                            btn.setBackgroundColor(Color.parseColor("#44004400"));
                        }
                    } catch (Throwable ignored) {}
                    return true;
                }
            });

            row.addView(btn);
        }
        modalLayout.addView(row, rowParams);
    }

    private static void handleKeyClick(String key) {
        if (key.equals("SİL")) {
            if (currentMessage.length() > 0) {
                currentMessage.deleteCharAt(currentMessage.length() - 1);
            }
        } else if (key.equals("BOŞLUK")) {
            currentMessage.append(" ");
        } else if (key.equals("KAPAT")) {
            if (modalLayout != null) {
                windowManager.removeView(modalLayout);
                modalLayout = null;
                currentMessage.setLength(0);
            }
            try {
                File f = new File("/data/local/tmp/anka_chat_display.txt");
                if (f.exists()) f.delete();
            } catch (Exception ignored) {}
        } else if (key.equals("GÖNDER")) {
            String msg = currentMessage.toString().trim();
            if (!msg.isEmpty()) {
                sendSinekMessage(msg);
                currentMessage.setLength(0); // Yazıyı temizle ama KLAVYEYİ KAPATMA!
            }
        } else {
            currentMessage.append(key.toLowerCase());
        }

        if (inputDisplay != null) {
            inputDisplay.setText(currentMessage.length() > 0 ? currentMessage.toString() : "Yazmak için harflere dokun...");
        }
    }

    private static void sendSinekMessage(String msg) {
        try {
            File chatFile = new File("/data/local/tmp/anka_chat_in.txt");
            FileWriter writer = new FileWriter(chatFile, false);
            writer.write(msg);
            writer.close();
            
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter cmdWriter = new FileWriter(cmdFile, false);
            cmdWriter.write("SOHBET: " + msg);
            cmdWriter.close();

            File chatDisplay = new File("/data/local/tmp/anka_chat_display.txt");
            FileWriter dispWriter = new FileWriter(chatDisplay, false);
            dispWriter.write("💬 SEN: " + msg + "\n\n🪰 SİNEK: Zihnim işliyor, bekle...");
            dispWriter.close();
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

        return btn;
    }

    private static void sendAnkaCommand(String cmd) {
        try {
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter writer = new FileWriter(cmdFile, false);
            writer.write(cmd);
            writer.close();
            
            File chatDisplay = new File("/data/local/tmp/anka_chat_display.txt");
            if (chatDisplay.exists()) chatDisplay.delete();
        } catch (Throwable ignored) {}
    }

    private static void startStatePoller() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (true) {
                    try {
                        String time = "--:--", battery = "--", dust = "0", mode = "--", sysThought = "--";
                        
                        File stateFile = new File("/data/local/tmp/anka_state.txt");
                        if (stateFile.exists()) {
                            BufferedReader reader = new BufferedReader(new FileReader(stateFile));
                            String line;
                            while ((line = reader.readLine()) != null) {
                                if (line.startsWith("TIME:")) time = line.substring(5).trim();
                                else if (line.startsWith("BATTERY:")) battery = line.substring(8).trim();
                                else if (line.startsWith("DUST:")) dust = line.substring(5).trim();
                                else if (line.startsWith("MODE:")) mode = line.substring(5).trim();
                                else if (line.startsWith("THOUGHT:")) sysThought = line.substring(8).trim();
                            }
                            reader.close();
                        }

                        boolean isChatActive = false;
                        String chatContent = "";
                        try {
                            File chatDisplay = new File("/data/local/tmp/anka_chat_display.txt");
                            if (chatDisplay.exists() && chatDisplay.length() > 0) {
                                BufferedReader cr = new BufferedReader(new FileReader(chatDisplay));
                                String cLine;
                                while ((cLine = cr.readLine()) != null) {
                                    chatContent += cLine + "\n";
                                }
                                cr.close();
                                isChatActive = true;
                            }
                        } catch (Exception ignored) {}

                        final String headerText = "● ANKA OS v1.0  |  SAAT: " + time + "  |  PİL: %" + battery;
                        final String middleText = "KUANTUM TOZU: " + dust + "  |  MOD: " + mode;
                        
                        final String finalConsole;
                        if (isChatActive) {
                            finalConsole = "==================================\n" +
                                           " SİNEK İLE SİBER BAĞLANTI AKTİF \n" +
                                           "==================================\n\n" + 
                                           chatContent;
                        } else {
                            finalConsole = ">_ SİSTEM DURUM RAPORU:\n\n" + sysThought;
                        }

                        mainHandler.post(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    if (headerView != null) headerView.setText(headerText);
                                    if (middleView != null) middleView.setText(middleText);
                                    if (consoleView != null) consoleView.setText(finalConsole);
                                } catch (Throwable ignored) {}
                            }
                        });
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
