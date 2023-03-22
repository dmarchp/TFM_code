#define STRAIGHT 90
#define TURN 60

// declare motion variable type
typedef enum {
    STOP,
    FORWARD,
    LEFT,
    RIGHT
} motion_t;


typedef struct {
  message_t transmit_msg;
  uint8_t new_message;
  distance_measurement_t dist;

  // uint8_t current_motion_type;
  uint32_t current_dist;
  uint8_t rand_turn;
  uint8_t rand_straight;
  uint32_t time_update;
  uint32_t time_update2;
  
  uint32_t last_motion_ticks;
  uint8_t turning_ticks;
  uint8_t max_turning_ticks;
  uint32_t max_straight_ticks;
  motion_t current_motion_type;
} USERDATA;

extern USERDATA *mydata;
