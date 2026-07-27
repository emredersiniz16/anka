package com.anka.os;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.File;
import java.io.FileWriter;

public class AnkaChatModal {
    private static LinearLayout modalLayout = null;
    private static TextView inputDisplay;
    private static StringBuilder currentMessage = new StringBuilder();

    public static void toggleModal(Context context, WindowManager wm, WindowManager.LayoutParams baseParams) {
        try {
            if (modalLayout != null) {
                wm.removeView(modalLayout);
                modalLayout = null;
                return;
            }

            modalLayout = new LinearLayout(context);
            modalLayout.setOrientation(LinearLayout.VERTICAL);
            modalLayout.setBackgroundColor(Color.parseColor("#F5050B14")); // Koyu siberpunk yarı şeffaf arkaplan
            modalLayout.setPadding(40, 40, 40, 40);
            modalLayout.setGravity(Gravity.CENTER);

            Typeface safeFont = Typeface.MONOSPACE;

            // Başlık
            TextView title = new TextView(context);
            title.setText("💬 SİNEK ÖZEL MESAJ KUTUSU");
            title.setTextColor(Color.GREEN);
            title.setTextSize(16);
            if (safeFont != null) title.setTypeface(safeFont);
            title.setGravity(Gravity.CENTER);
            title.setPadding(0, 0, 0, 20);
            modalLayout.addView(title);

            // Yazılan Mesajın Göründüğü Ekran
            inputDisplay = new TextView(context);
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

            // Sanal Klavye Tuşları (Sıralı Harf Satırları)
            addKeyboardRow(context, new String[]{"A", "B", "C", "D", "E", "F", "G", "H", "İ"});
            addKeyboardRow(context, new String[]{"J", "K", "L", "M", "N", "O", "P", "R", "S"});
            addKeyboardRow(context, new String[]{"Ş", "T", "U", "Ü", "V", "Y", "Z", "BOŞLUK", "SİL"});
            addKeyboardRow(context, new String[]{"KAPAT", "GÖNDER"});

            WindowManager.LayoutParams modalParams = new WindowManager.LayoutParams(
                WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                baseParams.type,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                android.graphics.PixelFormat.TRANSLUCENT
            );
            modalParams.gravity = Gravity.BOTTOM; // Ekranın alt kısmında yükselir

            wm.addView(modalLayout, modalParams);

        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    private static void addKeyboardRow(Context context, String[] keys) {
        LinearLayout row = new LinearLayout(context);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        rowParams.setMargins(0, 5, 0, 5);

        for (final String key : keys) {
            final TextView btn = new TextView(context);
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

            btn.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    handleKeyClick(key);
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
                // Kapatma mantığı ana sınıftan yönetilecek
                currentMessage.setLength(0);
            }
        } else if (key.equals("GÖNDER")) {
            String msg = currentMessage.toString().trim();
            if (!msg.isEmpty()) {
                sendSinekMessage(msg);
                currentMessage.setLength(0);
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
        } catch (Throwable ignored) {}
    }
}
