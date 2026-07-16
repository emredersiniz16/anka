#ifndef FLY_ENGINE_H
#define FLY_ENGINE_H

typedef enum {
    FLY_IDLE, FLY_THINK, FLY_WAIT, FLY_GHOST, FLY_MIRROR
} FlyState;

extern FlyState current_state; 

void update_fly_behavior();

#endif
EOF
