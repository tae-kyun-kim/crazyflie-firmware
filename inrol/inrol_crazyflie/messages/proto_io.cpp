#include "inrol_crazyflie/messages/proto_io.hpp"
#include <pb_encode.h>

extern "C" {
#include "debug.h"
#include "app_channel.h"
}

namespace io {
  void _write(uint8_t data) {
    uint8_t* data_ptr = &data;
    appchannelSendDataPacket((void*)data_ptr, sizeof(data));
  }

  inline static bool nanopb_write(
    __attribute__((unused)) pb_ostream_t* stream, pb_byte_t const* buf,
    size_t size) {
    appchannelSendDataPacketBlock((void*)buf, size);
    return true;
  }

  static pb_ostream_t nanopb_stream = {
    .callback = nanopb_write,
    .state = nullptr,
    .max_size = SIZE_MAX,
    .bytes_written = 0,
  };

  bool report(Message message) {
    size_t message_len;
    pb_get_encoded_size(&message_len, Message_fields, &message);

    if (message_len > 0xFF) {
      DEBUG_PRINT("message length exceeds 1 byte");
      return false;
    }

    ::io::_write(0xFF);
    ::io::_write(static_cast<uint8_t>(message_len));
    return pb_encode(&nanopb_stream, Message_fields, &message);
  }
}  // namespace io
