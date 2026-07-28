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
    private static LinearLayout rootLayout;
    private static TextView headerView;
    private static TextView middleView;
    private static TextView consoleView;
    private static ScrollView scrollView;
    private static Handler mainHandler;
    private static WindowManager windowManager;
    private static WindowManager.LayoutParams rootParams;
    private static Context appContext;
    
    private static LinearLayout modalLayout = null;
    private static int lastChatLength = 0;

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

            rootLayout = new LinearLayout(appContext);
            rootLayout.setBackgroundColor(Color.parseColor("#EE050B14"));
            rootLayout.setOrientation(LinearLayout.VERTICAL);
            rootLayout.setPadding(30, 80, 30, 100); 

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

            middleView = new TextView(appContext);
            middleView.setText("KUANTUM TOZU: ---  |  MOD: YÜKLENİYOR...");
            middleView.setTextColor(Color.GREEN);
            middleView.setTextSize(15);
            if (safeFont != null) middleView.setTypeface(safeFont);
            rootLayout.addView(middleView);

            // TERMİNAL VE KAYDIRMA ALANI
            scrollView = new ScrollView(appContext);
            scrollView.setNestedScrollingEnabled(true);
            LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            scrollParams.setMargins(0, 20, 0, 10);

            consoleView = new TextView(appContext);
            consoleView.setText(">_ BAĞLANTI BEKLENİYOR...");
            consoleView.setTextColor(Color.GREEN);
            consoleView.setTextSize(16);
            consoleView.setLineSpacing(0, 1.3f);
            if (safeFont != null) consoleView.setTypeface(safeFont);
            
            scrollView.addView(consoleView);
            rootLayout.addView(scrollView, scrollParams);

            // ==========================================
            // SCROLL KONTROL BUTONLARI (▲ YUKARI / ▼ AŞAĞI)
            // ==========================================
            LinearLayout scrollBtnRow = new LinearLayout(appContext);
            scrollBtnRow.setOrientation(LinearLayout.HORIZONTAL);
            scrollBtnRow.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams sbParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            sbParams.setMargins(0, 0, 0, 10);

            TextView btnUp = createScrollButton("▲ YUKARI ÇIK", -1);
            TextView btnDown = createScrollButton("▼ EN AŞAĞI İN", 1);
            scrollBtnRow.addView(btnUp);
            scrollBtnRow.addView(btnDown);
            rootLayout.addView(scrollBtnRow, sbParams);

            // ALT AKSİYON BUTONLARI (MOD, TARA, SOHBET)
            LinearLayout btnRow = new LinearLayout(appContext);
            btnRow.setOrientation(LinearLayout.HORIZONTAL);
            btnRow.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams btnRowParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            btnRowParams.setMargins(0, 0, 0, 10);

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

    private static TextView createScrollButton(String text, final int direction) {
        final TextView btn = new TextView(appContext);
        btn.setText(text);
        btn.setTextColor(Color.GREEN);
        btn.setBackgroundColor(Color.parseColor("#22003300"));
        btn.setTextSize(12);
        btn.setGravity(Gravity.CENTER);
        btn.setPadding(10, 15, 10, 15);

        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        p.setMargins(4, 0, 4, 0);
        btn.setLayoutParams(p);

        btn.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    btn.setBackgroundColor(Color.parseColor("#8800FF00"));
                    if (scrollView != null) {
                        scrollView.post(new Runnable() {
                            @Override
                            public void run() {
                                if (direction < 0) {
                                    scrollView.fullScroll(View.FOCUS_UP);
                                } else {
                                    scrollView.fullScroll(View.FOCUS_DOWN);
                                }
                            }
                        });
                    }
                } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                    btn.setBackgroundColor(Color.parseColor("#22003300"));
                }
                return true;
            }
        });
        return btn;
    }

    private static void toggleChatModal() {
        try {
            if (modalLayout != null) {
                windowManager.removeView(modalLayout);
                modalLayout = null;
                return;
            }

            Typeface safeFont = Typeface.MONOSPACE;

            modalLayout = new LinearLayout(appContext);
            modalLayout.setOrientation(LinearLayout.VERTICAL);
            modalLayout.setBackgroundColor(Color.parseColor("#F8050B14"));
            modalLayout.setPadding(15, 25, 15, 25);
            modalLayout.setGravity(Gravity.CENTER);

            final TextView inputDisplay = new TextView(appContext);
            inputDisplay.setHint("Mesajını yaz...");
            inputDisplay.setHintTextColor(Color.parseColor("#5500FF00"));
            inputDisplay.setTextColor(Color.parseColor("#00FF00"));
            inputDisplay.setBackgroundColor(Color.parseColor("#33003300"));
            inputDisplay.setTextSize(16);
            inputDisplay.setPadding(20, 25, 20, 25);
            
            LinearLayout.LayoutParams dispParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            dispParams.setMargins(0, 0, 0, 20);
            modalLayout.addView(inputDisplay, dispParams);

            addKeyboardRow(new String[]{"Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "Ğ", "Ü"}, inputDisplay);
            addKeyboardRow(new String[]{"A", "S", "D", "F", "G", "H", "J", "K", "L", "Ş", "İ"}, inputDisplay);
            addKeyboardRow(new String[]{"Z", "X", "C", "V", "B", "N", "M", "Ö", "Ç"}, inputDisplay);

            LinearLayout actionRow = new LinearLayout(appContext);
            actionRow.setOrientation(LinearLayout.HORIZONTAL);
            actionRow.setGravity(Gravity.CENTER);
            LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            rowParams.setMargins(0, 6, 0, 6);

            actionRow.addView(createActionBtn("KAPAT", 1.2f, "#AA0000", "#FFFFFF", inputDisplay));
            actionRow.addView(createActionBtn("BOŞLUK", 2.0f, "#2200FF00", "#00FF00", inputDisplay));
            actionRow.addView(createActionBtn("SİL", 1.0f, "#88003300", "#00FF00", inputDisplay));
            actionRow.addView(createActionBtn("GÖNDER", 1.5f, "#00FF00", "#000000", inputDisplay));

            modalLayout.addView(actionRow, rowParams);

            WindowManager.LayoutParams modalParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                rootParams.type,
                WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN | WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
            );
            modalParams.gravity = Gravity.BOTTOM;

            windowManager.addView(modalLayout, modalParams);

        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    private static void addKeyboardRow(String[] keys, final TextView inputDisplay) {
        LinearLayout row = new LinearLayout(appContext);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        rowParams.setMargins(0, 4, 0, 4);

        for (final String key : keys) {
            final TextView btn = new TextView(appContext);
            btn.setText(key);
            btn.setTextColor(Color.GREEN);
            btn.setBackgroundColor(Color.parseColor("#33003300"));
            btn.setTextSize(15);
            btn.setGravity(Gravity.CENTER);
            btn.setPadding(0, 35, 0, 35);

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
                            handleKeyClick(key, inputDisplay);
                        } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                            btn.setBackgroundColor(Color.parseColor("#33003300"));
                        }
                    } catch (Throwable ignored) {}
                    return true;
                }
            });

            row.addView(btn);
        }
        modalLayout.addView(row, rowParams);
    }

    private static TextView createActionBtn(final String text, float weight, final String bgColor, String textColor, final TextView inputDisplay) {
        final TextView btn = new TextView(appContext);
        btn.setText(text);
        btn.setTextColor(Color.parseColor(textColor));
        btn.setBackgroundColor(Color.parseColor(bgColor));
        btn.setTextSize(14);
        btn.setTypeface(Typeface.DEFAULT_BOLD);
        btn.setGravity(Gravity.CENTER);
        btn.setPadding(0, 35, 0, 35);

        LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, weight);
        btnParams.setMargins(5, 0, 5, 0);
        btn.setLayoutParams(btnParams);

        btn.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    btn.setBackgroundColor(Color.WHITE);
                    handleKeyClick(text, inputDisplay);
                } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                    btn.setBackgroundColor(Color.parseColor(bgColor));
                }
                return true;
            }
        });
        return btn;
    }

    private static StringBuilder currentMessage = new StringBuilder();

    private static void handleKeyClick(String key, TextView inputDisplay) {
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
        } else if (key.equals("GÖNDER")) {
            String msg = currentMessage.toString().trim();
            if (!msg.isEmpty()) {
                sendSinekMessage(msg);
                currentMessage.setLength(0);
                if (modalLayout != null) {
                    windowManager.removeView(modalLayout);
                    modalLayout = null;
                }
            }
        } else {
            currentMessage.append(key.toLowerCase());
        }

        if (inputDisplay != null) {
            inputDisplay.setText(currentMessage.length() > 0 ? currentMessage.toString() : "");
        }
    }

    private static void sendSinekMessage(String msg) {
        try {
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter cmdWriter = new FileWriter(cmdFile, false);
            cmdWriter.write("SOHBET: " + msg);
            cmdWriter.close();

            File chatIn = new File("/data/local/tmp/anka_chat_in.txt");
            FileWriter inWriter = new FileWriter(chatIn, false);
            inWriter.write(msg);
            inWriter.close();
            osChmod(chatIn);
        } catch (Throwable ignored) {}
    }

    private static void osChmod(File f) {
        try {
            Runtime.getRuntime().exec("chmod 666 " + f.getAbsolutePath());
        } catch (Exception ignored) {}
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

        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
        p.setMargins(6, 0, 6, 0);
        btn.setLayoutParams(p);

        btn.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                if (event.getAction() == MotionEvent.ACTION_DOWN) {
                    btn.setBackgroundColor(Color.parseColor("#8800FF00"));
                    sendAnkaCommand(cmd);
                } else if (event.getAction() == MotionEvent.ACTION_UP || event.getAction() == MotionEvent.ACTION_CANCEL) {
                    btn.setBackgroundColor(Color.parseColor("#44003300"));
                }
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
            lastChatLength = 0;
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
                                StringBuilder sb = new StringBuilder();
                                while ((cLine = cr.readLine()) != null) {
                                    sb.append(cLine.replace("\\n", "\n")).append("\n");
                                }
                                cr.close();
                                chatContent = sb.toString();
                                isChatActive = true;
                            }
                        } catch (Exception ignored) {}

                        final String headerText = "● ANKA OS v1.0  |  SAAT: " + time + "  |  PİL: %" + battery;
                        final String middleText = "KUANTUM TOZU: " + dust + "  |  MODE: " + mode;
                        
                        final String finalConsole;
                        if (isChatActive) {
                            finalConsole = "==================================\n" +
                                           " SİNEK İLE SİBER BAĞLANTI AKTİF \n" +
                                           "==================================\n\n" + 
                                           chatContent;
                        } else {
                            finalConsole = ">_ SİSTEM DURUM RAPORU:\n\n" + sysThought;
                        }

                        final int currentLen = finalConsole.length();

                        mainHandler.post(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    if (headerView != null) headerView.setText(headerText);
                                    if (middleView != null) middleView.setText(middleText);
                                    
                                    if (consoleView != null && lastChatLength != currentLen) {
                                        consoleView.setText(finalConsole);
                                        if (scrollView != null) {
                                            scrollView.post(new Runnable() {
                                                @Override
                                                public void run() {
                                                    scrollView.fullScroll(View.FOCUS_DOWN);
                                                }
                                            });
                                        }
                                        lastChatLength = currentLen;
                                    }
                                } catch (Throwable ignored) {}
                            }
                        });
                    } catch (Exception ignored) {}

                    try {
                        Thread.sleep(300);
                    } catch (InterruptedException e) {
                        break;
                    }
                }
            }
        }).start();
    }
}
