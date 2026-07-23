/*
 * core/quantum/sinek_warfare.h
 * ANKA OS: SİNEK TAKTİKSEL SAVAŞ VE KUM HAVUZU (SANDBOX) BAŞLIĞI
 */

#ifndef SINEK_WARFARE_H
#define SINEK_WARFARE_H

#include <stdbool.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief KUM HAVUZU TESTİ: Sistemi dondurup donduramadığımızı test eder.
 * @param sf_pid Hedef servisin (SurfaceFlinger) işlem kimliği.
 * @return Test başarılıysa true, başarısızsa veya riskliyse false döndürür.
 */
bool sinek_sandbox_test(pid_t sf_pid);

/**
 * @brief ANA SAVAŞ FONKSİYONU: MIUI'ı bypass edip ekranı devralmak için 
 *        güvenli SIGSTOP saldırısı başlatır.
 * @return Dondurulan servisin PID'sini döndürür. Başarısızsa -1 veya 0 döner.
 */
int sinek_execute_takeover(void);

/**
 * @brief KAPANIŞ (GERİ ÇEKİLME): Dondurulan MIUI servisini SIGCONT ile uykudan 
 *        uyandırıp sistemi güvenli bir şekilde iade eder.
 * @param sf_pid Uyandırılacak servisin PID'si.
 */
void sinek_retreat(pid_t sf_pid);

#ifdef __cplusplus
}
#endif

#endif /* SINEK_WARFARE_H */
