#include <kilombo.h>
#include <time.h>
#include <stdio.h>
#include <math.h>
#include "PRWDIS.h"



#ifdef SIMULATOR
#include <stdio.h> // for printf
#else
#include <avr/io.h>  // for microcontroller register defs
//  #define DEBUG     // for printf to serial port
//  #include "debug.h"
#endif

REGISTER_USERDATA(USERDATA);

/* Function to tell bot to move */
void smooth_set_motors(uint8_t ccw, uint8_t cw)
{
  // OCR2A = ccw;  OCR2B = cw;
  #ifdef KILOBOT
  uint8_t l = 0, r = 0;
  if (ccw && !OCR2A) // we want left motor on, and it's off
  l = 0xff;
  if (cw && !OCR2B)  // we want right motor on, and it's off
  r = 0xff;
  if (l || r)        // at least one motor needs spin-up
  {
    set_motors(l, r);
    delay(15);
  }
  #endif
  // spin-up is done, now we set the real value
  set_motors(ccw, cw);
}

void set_motion(motion_t new_motion)
{
  if(mydata->current_motion_type != new_motion) {
    switch(new_motion) {
      case STOP:
      default:
      smooth_set_motors(0,0);
      break;
      case FORWARD:
      smooth_set_motors(kilo_straight_left, kilo_straight_right);
      break;
      case LEFT:
      smooth_set_motors(kilo_turn_left, 0);
      break;
      case RIGHT:
      smooth_set_motors(0, kilo_turn_right);
      break;
    }
    mydata->current_motion_type = new_motion;
  }
}

void random_walk(){
  uint8_t rand;
  switch(mydata->current_motion_type) {
    case LEFT:
    case RIGHT:
    if(kilo_ticks > mydata->last_motion_ticks + mydata->turning_ticks) {
      /* start moving forward */
      mydata->last_motion_ticks = kilo_ticks;
      set_motion(FORWARD);
    }
    break;
    case FORWARD:
    if( kilo_ticks > mydata->last_motion_ticks + mydata->max_straight_ticks) {
      /* perform a radnom turn */
      mydata->last_motion_ticks = kilo_ticks;
      if( rand_soft()%2) {
        set_motion(LEFT);
      }
      else {
        set_motion(RIGHT);
      }

      rand = rand_soft() % 2;
      if(rand == 0){
        mydata->turning_ticks = 90;
      }
      if(rand == 1){
        mydata->turning_ticks = 180;
      }

    }
    break;
    case STOP:
    default:
    set_motion(FORWARD);
  }
}

void left_walk() {
    // uint8_t rand
    switch(mydata->current_motion_type){
       case LEFT:
          set_motion(LEFT);
    
    }
}



void setup(){

  rand_seed(kilo_uid + 10); //Random seed so each bot has a initial state.
  mydata->time_update = kilo_ticks;
  mydata->time_update2 = kilo_ticks;
  mydata->rand_turn=rand_soft();
  mydata->time_update=kilo_ticks;
  
  // Random motion variables
  mydata->last_motion_ticks = 0;
  mydata->turning_ticks = 180;
  mydata->max_turning_ticks = 180;
  mydata->max_straight_ticks = 120;
  mydata->last_motion_ticks = rand_soft() % mydata->max_straight_ticks + 1;
  //mydata->current_motion_type = LEFT;
}


void loop()
{
    random_walk();
    //left_walk();
}



/* Create circle barrier */
int16_t circle_barrier(double x, double y, double * dx, double * dy)
{
  double d = sqrt(x*x + y*y);

  if (d < 750.0)
  return 0;

  *dx = -x/d;
  *dy = -y/d;

  return 1;
}


#ifdef SIMULATOR
static char botinfo_buffer[10000];
char *cb_botinfo(void)
{
  char *p = botinfo_buffer;
  p += sprintf (p, "randt: %d", mydata->rand_turn);

  return botinfo_buffer;
    
}
#include <jansson.h>
json_t *json_state();
#endif
/*******************************************************************/

int main() {

  SET_CALLBACK(obstacles, circle_barrier);
  // initialize hardware
  kilo_init();
  // register your program
  kilo_start(setup, loop);

  SET_CALLBACK(botinfo, cb_botinfo); 
  SET_CALLBACK(reset, setup);
  SET_CALLBACK(json_state, json_state);
  return(0);
}
