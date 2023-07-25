extern "C" {
#include "app.h"
#include "debug.h"
#include "FreeRTOS.h"
#include "task.h"
}

#include "inrol_crazyflie/messages/proto_io.hpp"
#include "proto/message.pb.h"

#define DEBUG_MODULE "APP_NANOPB_TEST"

void appMain() {
  DEBUG_PRINT("Waiting for activation ...\n");

  Message m;
  m.value = 1.0;

  while (true) {
    io::report(m);
    vTaskDelay(M2T(1000));
  }
}
