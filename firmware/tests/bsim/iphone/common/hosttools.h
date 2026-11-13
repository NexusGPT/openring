/*
 * Host calls for the two-device tests. The ring and the stand-in host are two
 * native processes on the same machine: the ring writes the passkey it shows
 * into a file that the host reads (the wearer reads it from the screen and
 * types it on the phone). The functions are the ones the native simulator
 * provides to every bsim application (nsi_host_trampolines.h).
 */
#ifndef BSIM_CONTROL_HOSTTOOLS_H
#define BSIM_CONTROL_HOSTTOOLS_H

char *nsi_host_getenv(const char *name);
int nsi_host_open(const char *pathname, int flags);
long nsi_host_read(int fd, void *buffer, unsigned long size);
long nsi_host_write(int fd, const void *buffer, unsigned long size);
int nsi_host_close(int fd);

#define HT_O_RDONLY 0
#define HT_O_WRONLY 1
#define HT_O_TRUNC  01000   /* Linux value; the file is created by run.sh */

#endif
