# Android.mk — NDK Kuantum Motoru Derleme Kuralları
# ===================================================

LOCAL_PATH := $(call my-dir)

# 🪰 Kuantum Kütüphanesi (.so)
include $(CLEAR_VARS)

LOCAL_MODULE := libanka_quantum
LOCAL_MODULE_CLASS := SHARED_LIBRARIES

# Kaynak dosyalar
LOCAL_SRC_FILES := \
    quantum_dust.c \
    collapse_engine.c \
    sinek_fsm.c

# Include yolları
LOCAL_C_INCLUDES := \
    $(LOCAL_PATH) \
    $(LOCAL_PATH)/.. \
    $(LOCAL_PATH)/../hal \
    $(LOCAL_PATH)/../utils

# Compiler flags
LOCAL_CFLAGS := \
    -Os \
    -fPIC \
    -DHAVE_OPENSSL \
    -Wall \
    -Wextra

# Linker flags
LOCAL_LDLIBS := \
    -ldl \
    -llog \
    -lpthread \
    -lcrypto \
    -lssl

LOCAL_SDK_VERSION := 21

include $(BUILD_SHARED_LIBRARY)
