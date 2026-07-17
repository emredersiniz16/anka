#ifndef ANKA_ENV_H
#define ANKA_ENV_H

/*
 * ANKA OS — Termux Python3 Bridge (C header)
 * --------------------------------------------------
 * C kodundan python3 cagirirken /system/bin/sh tamamen bypass.
 * system("python3 ...") YERINE anka_run_python() kullan.
 *
 * anka_run_python()      — senkron (waitpid ile bekler)
 * anka_run_python_bg()   — arka plan (beklemez, fork+execve)
 *
 * Kullanim:
 *   #include "anka_env.h"
 *
 *   // Tek script calistir (bekler):
 *   int rc = anka_run_python("agents/sinek_nexus.py", NULL);
 *
 *   // Arka planda calistir (beklemez):
 *   anka_run_python_bg("agents/sinek_nexus.py", NULL);
 *
 *   // Argumanli:
 *   char *args[] = {"--verbose", NULL};
 *   anka_run_python("script.py", args);
 */

#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>

extern char **environ;

#define TERMUX_PREFIX "/data/data/com.termux/files/usr"
#define TERMUX_HOME   "/data/data/com.termux/files/home"
#define TERMUX_PY     TERMUX_PREFIX "/bin/python3"

/* Termux ortam degiskenlerini set et */
static void anka_set_termux_env(void) {
    setenv("PATH", TERMUX_PREFIX "/bin:/system/bin:/system/xbin", 1);
    setenv("LD_LIBRARY_PATH", TERMUX_PREFIX "/lib", 1);
    setenv("PREFIX", TERMUX_PREFIX, 1);
    setenv("HOME", TERMUX_HOME, 1);
    setenv("TMPDIR", TERMUX_PREFIX "/tmp", 1);
    setenv("LANG", "en_US.UTF-8", 1);
}

/*
 * Python3'u fork+execve ile calistir (sh tamamen bypass) — SENKRON
 * return: 0 basarili, -1 fork fail, 127 exec fail, diger = python exit code
 */
static int anka_run_python(const char *script_path, char *const args[]) {
    anka_set_termux_env();

    pid_t pid = fork();
    if (pid < 0) {
        perror("[ANKA] fork failed");
        return -1;
    }

    if (pid == 0) {
        /* Child */
        char *argv[64];
        int i = 0;
        argv[i++] = (char *)TERMUX_PY;
        argv[i++] = (char *)script_path;

        if (args) {
            while (args[i - 2] != NULL && i < 62) {
                argv[i] = args[i - 2];
                i++;
            }
        }
        argv[i] = NULL;

        execve(TERMUX_PY, argv, environ);
        perror("[ANKA] execve python3 failed");
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
 * waitpid yapmaz, hemen doner. system("... &") yerine kullan.
 * return: 0 basarili fork, -1 fork fail
 */
static int anka_run_python_bg(const char *script_path, char *const args[]) {
    anka_set_termux_env();

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
        argv[i++] = (char *)TERMUX_PY;
        argv[i++] = (char *)script_path;

        if (args) {
            while (args[i - 2] != NULL && i < 62) {
                argv[i] = args[i - 2];
                i++;
            }
        }
        argv[i] = NULL;

        execve(TERMUX_PY, argv, environ);
        perror("[ANKA] execve python3 (bg) failed");
        _exit(127);
    }

    /* Parent: bekleme, hemen don */
    fprintf(stderr, "[ANKA] Python arka plan baslatildi (PID=%d): %s\n",
            (int)pid, script_path);
    return 0;
}

/*
 * Fallback: system() ile ama dogru env + mutlak yol
 * (execve kullanamiyorsan)
 */
static int anka_run_python_system(const char *cmd) {
    anka_set_termux_env();
    char full_cmd[2048];
    snprintf(full_cmd, sizeof(full_cmd), "%s %s", TERMUX_PY, cmd);
    return system(full_cmd);
}

#endif /* ANKA_ENV_H */

