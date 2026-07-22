# Application.mk — Android NDK Uygulama Yapılandırması
# ======================================================

# Desteklenen mimariler
APP_ABI := arm64-v8a

# NDK API seviyesi (Android 5.0+)
APP_PLATFORM := android-21

# STL kütüphanesi (c++ destek)
APP_STL := c++_shared

# Optimizasyon
APP_OPTIM := release

# Debug sembollerini koru (daha sonra strip edebilirsin)
APP_DEBUG := false
