#ifndef FLY_ENGINE_H
#define FLY_ENGINE_H

/**
 * @brief Uçuş motorunun durumlarını temsil eden enum yapısı.
 */
typedef enum {
    FLY_IDLE,    // Bekleme durumu
    FLY_THINK,   // Karar verme/Düşünme durumu
    FLY_WAIT,    // Bekleme/Delay durumu
    FLY_GHOST,   // Görünmezlik veya hayalet modu
    FLY_MIRROR   // Yansıma veya taklit modu
} FlyState;

// Global durum değişkeni
extern FlyState current_state; 

/**
 * @brief Fly davranış mantığını güncelleyen ana fonksiyon.
 * Her döngüde çağrılmalıdır.
 */
void update_fly_behavior();

#endif // FLY_ENGINE_H
