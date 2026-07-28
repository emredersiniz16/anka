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
import android.view.inputmethod.InputMethodManager;
import android.widget.TextView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.EditText;

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
    private static EditText inputField = null;
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

            scrollView = new ScrollView(appContext);
            LinearLayout.LayoutParams scrollParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0f);
            scrollParams.setMargins(0, 20, 0, 20);

            consoleView = new TextView(appContext);
            consoleView.setText(">_ BAĞLANTI BEKLENİYOR...");
            consoleView.setTextColor(Color.GREEN);
            consoleView.setTextSize(16);
            consoleView.setLineSpacing(0, 1.3f);
            if (safeFont != null) consoleView.setTypeface(safeFont);
            
            scrollView.addView(consoleView);
            rootLayout.addView(scrollView, scrollParams);

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

    private static void toggleChatModal() {
        try {
            if (modalLayout != null) {
                closeChatModal();
                return;
            }

            Typeface safeFont = Typeface.MONOSPACE;

            modalLayout = new LinearLayout(appContext);
            modalLayout.setOrientation(LinearLayout.VERTICAL);
            modalLayout.setBackgroundColor(Color.parseColor("#F5050B14"));
            modalLayout.setPadding(30, 30, 30, 30);
            modalLayout.setGravity(Gravity.CENTER);

            TextView title = new TextView(appContext);
            title.setText("💬 SİNEK ÖZEL MESAJ KUTUSU");
            title.setTextColor(Color.GREEN);
            title.setTextSize(14);
            if (safeFont != null) title.setTypeface(safeFont);
            title.setGravity(Gravity.CENTER);
            title.setPadding(0, 0, 0, 15);
            modalLayout.addView(title);

            inputField = new EditText(appContext);
            inputField.setHint("Mesajını yaz...");
            inputField.setTextColor(Color.GREEN);
            inputField.setHintTextColor(Color.parseColor("#5500FF00"));
            inputField.setBackgroundColor(Color.parseColor("#33003300"));
            inputField.setTextSize(16);
            inputField.setPadding(30, 30, 30, 30);
            inputField.setFocusable(true);
            inputField.setFocusableInTouchMode(true);
            inputField.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE);
            if (safeFont != null) inputField.setTypeface(safeFont);
            
            LinearLayout.LayoutParams dispParams = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            dispParams.setMargins(0, 0, 0, 20);
            modalLayout.addView(inputField, dispParams);

            // Tıklandığında klavyeyi zorla aç
            inputField.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    if (event.getAction() == MotionEvent.ACTION_UP) {
                        inputField.requestFocus();
                        InputMethodManager imm = (InputMethodManager) appContext.getSystemService(Context.INPUT_METHOD_SERVICE);
                        if (imm != null) imm.showSoftInput(inputField, InputMethodManager.SHOW_IMPLICIT);
                    }
                    return false;
                }
            });

            LinearLayout btnRow = new LinearLayout(appContext);
            btnRow.setOrientation(LinearLayout.HORIZONTAL);
            btnRow.setGravity(Gravity.CENTER);

            TextView btnKapat = new TextView(appContext);
            btnKapat.setText("KAPAT");
            btnKapat.setTextColor(Color.GREEN);
            btnKapat.setBackgroundColor(Color.parseColor("#44004400"));
            btnKapat.setTextSize(14);
            btnKapat.setGravity(Gravity.CENTER);
            btnKapat.setPadding(30, 20, 30, 20);
            if (safeFont != null) btnKapat.setTypeface(safeFont);
            
            LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1.0f);
            btnParams.setMargins(10, 0, 10, 0);

            btnKapat.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    if (event.getAction() == MotionEvent.ACTION_DOWN) closeChatModal();
                    return true;
                }
            });

            TextView btnGonder = new TextView(appContext);
            btnGonder.setText("GÖNDER");
            btnGonder.setTextColor(Color.GREEN);
            btnGonder.setBackgroundColor(Color.parseColor("#44004400"));
            btnGonder.setTextSize(14);
            btnGonder.setGravity(Gravity.CENTER);
            btnGonder.setPadding(30, 20, 30, 20);
            if (safeFont != null) btnGonder.setTypeface(safeFont);

            btnGonder.setOnTouchListener(new View.OnTouchListener() {
                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    if (event.getAction() == MotionEvent.ACTION_DOWN) {
                        String msg = inputField.getText().toString().trim();
                        if (!msg.isEmpty()) {
                            sendSinekMessage(msg);
                            inputField.setText("");
                            hideKeyboard();
                        }
                    }
                    return true;
                }
            });

            btnRow.addView(btnKapat, btnParams);
            btnRow.addView(btnGonder, btnParams);
            modalLayout.addView(btnRow);

            // KLAVYE İÇİN SİHİRLİ PARAMETRELER: FLAG_NOT_TOUCH_MODAL ve softInputMode
            WindowManager.LayoutParams modalParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                rootParams.type,
                WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL | WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH, 
                PixelFormat.TRANSLUCENT
            );
            modalParams.gravity = Gravity.BOTTOM;
            modalParams.softInputMode = WindowManager.LayoutParams.SOFT_INPUT_STATE_VISIBLE | WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE;

            windowManager.addView(modalLayout, modalParams);

            // Odağı hemen al ve klavyeyi fırlat
            inputField.requestFocus();
            mainHandler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    InputMethodManager imm = (InputMethodManager) appContext.getSystemService(Context.INPUT_METHOD_SERVICE);
                    if (imm != null) imm.showSoftInput(inputField, InputMethodManager.SHOW_IMPLICIT);
                }
            }, 200);

        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    private static void hideKeyboard() {
        try {
            if (inputField != null) {
                InputMethodManager imm = (InputMethodManager) appContext.getSystemService(Context.INPUT_METHOD_SERVICE);
                if (imm != null) imm.hideSoftInputFromWindow(inputField.getWindowToken(), 0);
            }
        } catch (Exception ignored) {}
    }

    private static void closeChatModal() {
        try {
            hideKeyboard();
            if (modalLayout != null) {
                windowManager.removeView(modalLayout);
                modalLayout = null;
                inputField = null;
            }
            
            File f = new File("/data/local/tmp/anka_chat_display.txt");
            if (f.exists()) f.delete();
            lastChatLength = 0;
        } catch (Exception e) {}
    }

    private static void sendSinekMessage(String msg) {
        try {
            File cmdFile = new File("/data/local/tmp/anka_cmd.txt");
            FileWriter cmdWriter = new FileWriter(cmdFile, false);
            cmdWriter.write("SOHBET: " + msg);
            cmdWriter.close();

            File chatDisplay = new File("/data/local/tmp/anka_chat_display.txt");
            FileWriter dispWriter = new FileWriter(chatDisplay, true);
            dispWriter.write("💬 SEN: " + msg + "\n\n");
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
