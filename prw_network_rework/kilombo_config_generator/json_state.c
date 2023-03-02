/* Saving bot state as json. Not for use in the real bot, only in the simulator. */
#include <kilombo.h>

#ifdef SIMULATOR

#include <jansson.h>
#include <stdio.h>
#include <string.h>

/*#include "keep_dist.h"*/
#include "PRWDIS.h"

json_t *json_state()
{
  //create the state object we return
  json_t* state = json_object();


  return state;
}

#endif
