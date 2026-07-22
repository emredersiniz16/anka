#ifndef ANKA_ENV_H
#define ANKA_ENV_H

/*
 * ANKA OS — Native Python Bridge (TERMUX'A VEDA!)
 * --------------------------------------------------
 * Termux tamamen kaldirildi! Artik dogrudan Magisk/ROM icindeki 
 * gercek "python3" binary'sini kullanir.
 *
 * anka_run_python()      — senkron (waitpid ile bekler)
 * anka_run_python_bg()   — arka plan (beklemez, fork+execvp)
 */

#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>

extern char **environ;

// Artik Termux yolu yok. Sistemde kurulu yerel Python3 aranacak.
#define ANKA_PY "python3"

/*
 * Python3'u fork+execvp ile calistir (sh tamamen bypass) — SENKRON
 * return: 0 basarili, -1 fork fail, 127 exec fail, diger = python exit code
 */
static int anka_run_python(const char *script_path, char *const args[]) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("[ANKA] fork failed");
        return -1;
    }

    if (pid == 0) {
        /* Child Süreç: Çevre değişkeni (env) bozmak yok, yerel PATH kullanılır */
        char *argv[64];
        int i = 0;
        argv[i++] = (char *)ANKA_PY;
        argv[i++] = (char *)script_path;

        if (args) {
            while (args[i - 2] != NULL && i < 62) {
                argv[i] = args[i - 2];
                i++;
            }
        }
        argv[i] = NULL;

        // execvp sistemin kendi PATH'i uzerinden python3'u bulur
        execvp(ANKA_PY, argv);
        
        // Eger PATH'te bulamazsa, Magisk/Sistem mutlak yollarini zorla dener
        execve("/system/bin/python3", argv, environ);
        execve("/data/adb/modules/python/system/bin/python3", argv, environ);
        
        perror("[ANKA] HATA: python3 bulunamadi! (Magisk Python Modulu kurulu mu?)");
        _exit(127);
    }

    /* Parent: bekle */
    int status;
    waitpid(pid, &status, 0);

    if (WIFEXITED(status))
        return WEXITSTATUS(status);
    return -1;
}

/*
 * Python3'u arka planda calistir (sh bypass) — ASENKRON
 * waitpid yapmaz, hemen doner.
 */
static int anka_run_python_bg(const char *script_path, char *const args[]) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("[ANKA] fork (bg) failed");
        return -1;
    }

    if (pid == 0) {
        /* Child — kendi process grubuna gec */
        setsid();

        char *argv[64];
        int i = 0;
        argv[i++] = (char *)ANKA_PY;
        argv[i++] = (char *)script_path;

        if (args) {
            while (args[i - 2] != NULL && i < 62) {
                argv[i] = args[i - 2];
                i++;
            }
        }
        argv[i] = NULL;

        execvp(ANKA_PY, argv);
        execve("/system/bin/python3", argv, environ);
        
        perror("[ANKA] HATA: python3 (bg) bulunamadi! Lutfen yerel Python kurun.");
        _exit(127);
    }

    /* Parent: bekleme, hemen don */
    fprintf(stderr, "🪰 [ANKA] Kovan Ajani (Python) arka planda baslatildi (PID=%d): %s\n",
            (int)pid, script_path);
    return 0;
}

/*
 * Fallback: system() ile saf cagirilis
 */
static int anka_run_python_system(const char *cmd) {
    pid_t pid = fork();
    if (pid < 0) {
        return -1;
    }
    
    if (pid == 0) {
        char full_cmd[2048];
        snprintf(full_cmd, sizeof(full_cmd), "python3 %s", cmd);
        exit(system(full_cmd));
    }
    
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status))
        return WEXITSTATUS(status);
    return -1;
}

#endif /* ANKA_ENV_H */
