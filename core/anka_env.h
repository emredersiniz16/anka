cat <<EOF > anka_env.h
#ifndef ANKA_ENV_H
#define ANKA_ENV_H
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <string.h>
#include <stdio.h>
extern char **environ;
#define TERMUX_PREFIX "/data/data/com.termux/files/usr"
#define TERMUX_HOME   "/data/data/com.termux/files/home"
#define TERMUX_PY     TERMUX_PREFIX "/bin/python3"
static void anka_set_termux_env(void) {
    setenv("PATH", TERMUX_PREFIX "/bin:/system/bin:/system/xbin", 1);
    setenv("LD_LIBRARY_PATH", TERMUX_PREFIX "/lib", 1);
    setenv("PREFIX", TERMUX_PREFIX, 1);
    setenv("HOME", TERMUX_HOME, 1);
    setenv("TMPDIR", TERMUX_PREFIX "/tmp", 1);
    setenv("LANG", "en_US.UTF-8", 1);
}
static int anka_run_python(const char *script_path, char *const args[]) {
    anka_set_termux_env();
    pid_t pid = fork();
    if (pid < 0) { perror("[ANKA] fork failed"); return -1; }
    if (pid == 0) {
        char *argv[64];
        int i = 0;
        argv[i++] = (char *)TERMUX_PY;
        argv[i++] = (char *)script_path;
        if (args) {
            while (args[i - 2] != NULL && i < 62) {
                argv[i] = args[i - 2]; i++;
            }
        }
        argv[i] = NULL;
        execve(TERMUX_PY, argv, environ);
        perror("[ANKA] execve python3 failed");
        _exit(127);
    }
    int status;
    waitpid(pid, &status, 0);
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    return -1;
}
#endif
EOF
