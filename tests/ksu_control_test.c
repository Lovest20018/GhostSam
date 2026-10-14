/* This test never invokes reboot/ioctl or loads a kernel module. */
#include <assert.h>
#include "ksu.h"

int main(void) {
  struct ksu_get_info_cmd info = {
      .version = 32601,
      .flags = KSU_FLAG_LKM | KSU_FLAG_LATE_LOAD,
      .uapi_version = KSU_UAPI_EXPECTED,
  };
  assert(ksu_control_info_valid(&info));
  info.version = 33000;
  assert(ksu_control_info_valid(&info));
  info.version = 0;
  assert(!ksu_control_info_valid(&info));
  info.version = 32601;
  info.uapi_version = 2;
  assert(!ksu_control_info_valid(&info));
  info.uapi_version = 6;
  assert(!ksu_control_info_valid(&info));
  info.uapi_version = KSU_UAPI_EXPECTED;
  info.flags = KSU_FLAG_LKM;
  assert(!ksu_control_info_valid(&info));
  info.flags = KSU_FLAG_LATE_LOAD;
  assert(!ksu_control_info_valid(&info));
  info.flags = KSU_FLAG_LKM | KSU_FLAG_LATE_LOAD | (1U << 4);
  assert(ksu_control_info_valid(&info));
  return 0;
}
