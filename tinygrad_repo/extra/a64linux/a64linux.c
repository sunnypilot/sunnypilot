#include <Hypervisor/Hypervisor.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/uio.h>
#include <sys/ioctl.h>
#include <dirent.h>
#include <fcntl.h>
#include <poll.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/times.h>

typedef struct { uint8_t e_ident[16]; uint16_t e_type, e_machine; uint32_t e_version; uint64_t e_entry, e_phoff, e_shoff; uint32_t e_flags; uint16_t e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx; } Elf64_Ehdr;
typedef struct { uint32_t p_type, p_flags; uint64_t p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align; } Elf64_Phdr;
enum { PT_LOAD = 1, PT_INTERP = 3, PT_PHDR = 6, ET_DYN = 3, EM_AARCH64 = 183 };
enum { AT_NULL, AT_PHDR = 3, AT_PHENT, AT_PHNUM, AT_PAGESZ, AT_BASE, AT_FLAGS, AT_ENTRY, AT_UID = 11, AT_EUID, AT_GID, AT_EGID, AT_PLATFORM, AT_HWCAP, AT_CLKTCK, AT_SECURE = 23, AT_RANDOM = 25, AT_EXECFN = 31 };

#define GB (1ULL<<30)
#define MEM_SIZE (16*GB)
#define MMAP_LO (1*GB)
#define MMAP_HI (14*GB)
#define STACK_TOP (15*GB)
#define SYS_PAGE (MEM_SIZE - 0x10000)
#define PG 4096ULL
#define UP(x) (((x)+PG-1)&~(PG-1))
#define G(a) ((void*)(mem+(uint64_t)(a)))
#define CK(x) do { hv_return_t r_ = (x); if (r_) { fprintf(stderr, "a64linux: %s failed %x\n", #x, r_); exit(1); } } while (0)

static uint8_t *mem;
static const char *rootfs = "";
static int trace;
static uint64_t brk_lo, brk_cur, hiwater = MMAP_LO;
static hv_vcpu_t vcpu;

static struct { uint64_t s, e; } fr[65536];
static int nfr;
static void fr_del(int i) { memmove(&fr[i], &fr[i+1], (--nfr-i)*sizeof(fr[0])); }
static void fr_ins(int i, uint64_t s, uint64_t e) { memmove(&fr[i+1], &fr[i], (nfr++-i)*sizeof(fr[0])); fr[i].s = s; fr[i].e = e; }
static void fr_take(uint64_t s, uint64_t e) {
  for (int i = 0; i < nfr; i++) {
    if (fr[i].e <= s || fr[i].s >= e) continue;
    uint64_t fs = fr[i].s, fe = fr[i].e;
    fr_del(i--);
    if (fs < s) fr_ins(++i, fs, s);
    if (fe > e) fr_ins(++i, e, fe);
  }
}
static void fr_give(uint64_t s, uint64_t e) {
  if (s < MMAP_LO || e > MMAP_HI || s >= e) return;
  fr_take(s, e);
  int i = 0;
  while (i < nfr && fr[i].s < s) i++;
  fr_ins(i, s, e);
  if (i+1 < nfr && fr[i].e == fr[i+1].s) { fr[i].e = fr[i+1].e; fr_del(i+1); }
  if (i > 0 && fr[i-1].e == fr[i].s) { fr[i-1].e = fr[i].e; fr_del(i); }
}
static uint64_t fr_alloc(uint64_t len) {
  for (int i = 0; i < nfr; i++) if (fr[i].e - fr[i].s >= len) { uint64_t s = fr[i].s; fr_take(s, s+len); return s; }
  return 0;
}

static const char *xp(const char *p) {
  static char buf[4][4096]; static int n;
  struct stat st;
  if (p[0] != '/' || !rootfs[0]) return p;
  char *b = buf[n++ & 3];
  snprintf(b, 4096, "%s%s", rootfs, p);
  return lstat(b, &st) == 0 ? b : p;
}
static int64_t er(int64_t r) {
  static const short map[] = {[EAGAIN]=11, [EDEADLK]=35, [ENOTSUP]=95, [ELOOP]=40, [ENAMETOOLONG]=36, [ENOTEMPTY]=39, [ENOSYS]=38, [EOVERFLOW]=75,
                              [ETIMEDOUT]=110, [EAFNOSUPPORT]=97, [ENOTSOCK]=88, [ENOBUFS]=105, [EINPROGRESS]=115, [ECONNREFUSED]=111};
  if (r != -1) return r;
  int e = errno;
  return -(int64_t)(e < (int)(sizeof(map)/sizeof(map[0])) && map[e] ? map[e] : e <= 34 ? e : 22);
}
static int oflags(int f) {
  int r = f & 3;
  if (f & 0100) r |= O_CREAT; if (f & 0200) r |= O_EXCL; if (f & 01000) r |= O_TRUNC; if (f & 02000) r |= O_APPEND; if (f & 04000) r |= O_NONBLOCK;
  if (f & 040000) r |= O_DIRECTORY; if (f & 0100000) r |= O_NOFOLLOW; if (f & 02000000) r |= O_CLOEXEC;
  return r;
}
static int atflags(int f) { return (f & 0x100 ? AT_SYMLINK_NOFOLLOW : 0) | (f & 0x200 ? AT_REMOVEDIR : 0); }
static int dfd(int64_t d) { return (int)d == -100 ? AT_FDCWD : (int)d; }
struct lstat64 { uint64_t dev, ino; uint32_t mode, nlink, uid, gid; uint64_t rdev, pad1; int64_t size; int32_t blksize, pad2; int64_t blocks, at, atn, mt, mtn, ct, ctn; uint32_t unused[2]; };
static void put_stat(struct lstat64 *o, struct stat *s) {
  *o = (struct lstat64){.dev=s->st_dev, .ino=s->st_ino, .mode=s->st_mode, .nlink=s->st_nlink, .uid=s->st_uid, .gid=s->st_gid, .rdev=s->st_rdev, .size=s->st_size,
    .blksize=4096, .blocks=s->st_blocks, .at=s->st_atimespec.tv_sec, .atn=s->st_atimespec.tv_nsec, .mt=s->st_mtimespec.tv_sec, .mtn=s->st_mtimespec.tv_nsec,
    .ct=s->st_ctimespec.tv_sec, .ctn=s->st_ctimespec.tv_nsec};
}
static DIR *dirs[4096];
static int64_t sys_getdents(int fd, uint8_t *out, uint64_t cap) {
  if (fd < 0 || fd >= 4096) return -9;
  if (!dirs[fd] && !(dirs[fd] = fdopendir(dup(fd)))) return er(-1);
  uint64_t n = 0; struct dirent *d; long pos;
  while (pos = telldir(dirs[fd]), (d = readdir(dirs[fd]))) {
    uint64_t rl = (19 + strlen(d->d_name) + 1 + 7) & ~7ULL;
    if (n + rl > cap) { seekdir(dirs[fd], pos); break; }
    *(uint64_t*)(out+n) = d->d_ino; *(int64_t*)(out+n+8) = n+rl; *(uint16_t*)(out+n+16) = rl; out[n+18] = d->d_type; strcpy((char*)out+n+19, d->d_name);
    n += rl;
  }
  return n;
}
static int64_t sys_mmap(uint64_t addr, uint64_t len, int prot, int flags, int fd, uint64_t off) {
  len = UP(len);
  if (!len) return -22;
  if (flags & 0x10) { if (addr & (PG-1) || addr + len > MMAP_HI) return -22; fr_take(addr, addr+len); }
  else if (!(addr = fr_alloc(len))) return -12;
  if (flags & 0x10 || addr < hiwater) memset(G(addr), 0, len);
  if (addr + len > hiwater) hiwater = addr + len;
  if (!(flags & 0x20)) for (uint64_t got = 0; got < len; ) {
    ssize_t r = pread(fd, G(addr+got), len-got, off+got);
    if (r <= 0) break;
    got += r;
  }
  return addr;
}
static int64_t sys_brk(uint64_t nb) {
  if (nb < brk_lo || nb > MMAP_LO) return brk_cur;
  if (nb < brk_cur) memset(G(nb), 0, brk_cur-nb);
  return brk_cur = nb;
}
static int clk(int c) { return c == 1 || c == 6 || c == 7 ? CLOCK_MONOTONIC : c == 4 ? CLOCK_MONOTONIC_RAW : c == 2 ? CLOCK_PROCESS_CPUTIME_ID : c == 3 ? CLOCK_THREAD_CPUTIME_ID : CLOCK_REALTIME; }

static int64_t do_syscall(uint64_t n, uint64_t *a) {
  struct stat st; int64_t r;
  switch (n) {
  case 17: return getcwd(G(a[0]), a[1]) ? (int64_t)strlen(G(a[0]))+1 : er(-1);
  case 23: return er(dup(a[0]));
  case 24: return a[0] == a[1] ? -22 : er(dup2(a[0], a[1]));
  case 25: switch (a[1]) {
    case 1030: return er(fcntl(a[0], F_DUPFD_CLOEXEC, (int)a[2]));
    case 0: case 1: case 2: return er(fcntl(a[0], a[1], (int)a[2]));
    case 3: return (r = fcntl(a[0], F_GETFL)) < 0 ? er(-1) : (r & 3) | (r & O_APPEND ? 02000 : 0) | (r & O_NONBLOCK ? 04000 : 0);
    case 4: return er(fcntl(a[0], F_SETFL, oflags(a[2]) & (O_APPEND|O_NONBLOCK)));
    default: return -22; }
  case 29: return a[1] == 0x5451 ? er(fcntl(a[0], F_SETFD, FD_CLOEXEC)) : a[1] == 0x5401 && isatty(a[0]) ? 0 : -25;
  case 34: return er(mkdirat(dfd(a[0]), xp(G(a[1])), a[2]));
  case 35: return er(unlinkat(dfd(a[0]), xp(G(a[1])), atflags(a[2])));
  case 38: return er(renameat(dfd(a[0]), xp(G(a[1])), dfd(a[2]), xp(G(a[3]))));
  case 46: return er(ftruncate(a[0], a[1]));
  case 48: case 439: return er(faccessat(dfd(a[0]), xp(G(a[1])), a[2], 0));
  case 49: return er(chdir(xp(G(a[0]))));
  case 52: return er(fchmod(a[0], a[1]));
  case 53: return er(fchmodat(dfd(a[0]), xp(G(a[1])), a[2], 0));
  case 56: return er(openat(dfd(a[0]), xp(G(a[1])), oflags(a[2]), (int)a[3]));
  case 57: if (a[0] < 4096 && dirs[a[0]]) { closedir(dirs[a[0]]); dirs[a[0]] = NULL; } return er(close(a[0]));
  case 59: if ((r = pipe(G(a[0])))) return er(r);
    if (a[1] & 02000000) for (int i = 0; i < 2; i++) fcntl(((int*)G(a[0]))[i], F_SETFD, FD_CLOEXEC);
    return 0;
  case 61: return sys_getdents(a[0], G(a[1]), a[2]);
  case 62: return er(lseek(a[0], a[1], a[2]));
  case 63: return er(read(a[0], G(a[1]), a[2]));
  case 64: return er(write(a[0], G(a[1]), a[2]));
  case 65: case 66: {
    struct iovec iv[64], *g = G(a[1]); int c = a[2] > 64 ? 64 : a[2];
    for (int i = 0; i < c; i++) iv[i] = (struct iovec){G(g[i].iov_base), g[i].iov_len};
    return er(n == 65 ? readv(a[0], iv, c) : writev(a[0], iv, c)); }
  case 67: return er(pread(a[0], G(a[1]), a[2], a[3]));
  case 68: return er(pwrite(a[0], G(a[1]), a[2], a[3]));
  case 73: { struct timespec *ts = a[2] ? G(a[2]) : NULL; return er(poll(G(a[0]), a[1], ts ? ts->tv_sec*1000 + ts->tv_nsec/1000000 : -1)); }
  case 78: return er(readlinkat(dfd(a[0]), xp(G(a[1])), G(a[2]), a[3]));
  case 79: if ((a[3] & 0x1000) && !*(char*)G(a[1])) r = fstat(a[0], &st); else r = fstatat(dfd(a[0]), xp(G(a[1])), &st, atflags(a[3]));
    if (r) return er(r); put_stat(G(a[2]), &st); return 0;
  case 80: if ((r = fstat(a[0], &st))) return er(r); put_stat(G(a[1]), &st); return 0;
  case 82: return er(fsync(a[0]));
  case 93: case 94: exit(a[0]);
  case 96: case 172: case 178: return getpid();
  case 98: switch (a[1] & 0x7f) {
    case 1: case 10: return 0;
    case 0: case 9: if (*(uint32_t*)G(a[0]) != (uint32_t)a[2]) return -11;
      fprintf(stderr, "a64linux: futex wait would block forever (threads are not supported)\n"); exit(1);
    default: return -38; }
  case 99: case 122: case 132: case 134: case 135: case 167: case 226: case 227: case 233: return 0;
  case 101: case 115: { struct timespec *ts = G(n == 101 ? a[0] : a[2]); nanosleep(ts, NULL); return 0; }
  case 113: return er(clock_gettime(clk(a[0]), G(a[1])));
  case 114: return er(clock_getres(clk(a[0]), a[1] ? G(a[1]) : NULL));
  case 123: if (a[1] < 8) return -22; memset(G(a[2]), 0, a[1]); *(uint8_t*)G(a[2]) = 1; return 8;
  case 124: return 0;
  case 129: case 130: case 131: fprintf(stderr, "a64linux: guest raised signal %d\n", (int)a[n == 131 ? 2 : 1]); exit(128 + (int)a[n == 131 ? 2 : 1]);
  case 153: return er(times(G(a[0])));
  case 160: { char *u = G(a[0]); memset(u, 0, 65*6);
    strcpy(u, "Linux"); strcpy(u+65, "a64linux"); strcpy(u+130, "5.15.0"); strcpy(u+195, "#1 SMP"); strcpy(u+260, "aarch64"); return 0; }
  case 163: case 261: { uint64_t *o = G(a[n == 163 ? 1 : 3]); int res = a[n == 163 ? 0 : 1];
    if (n == 261 && !a[3]) return 0;
    o[0] = res == 3 ? 8<<20 : res == 7 ? 4096 : ~0ULL; o[1] = res == 7 ? 4096 : ~0ULL; return 0; }
  case 165: { struct rusage ru; getrusage(RUSAGE_SELF, &ru); memset(G(a[1]), 0, 144); memcpy(G(a[1]), &ru, 32); return 0; }
  case 166: return umask(a[0]);
  case 169: return er(gettimeofday(G(a[0]), NULL));
  case 173: return getppid();
  case 174: case 175: return getuid();
  case 176: case 177: return getgid();
  case 179: { uint64_t *s = G(a[0]); memset(s, 0, 112); s[4] = 16*GB; s[5] = 8*GB; *(uint16_t*)&s[10] = 1; *(uint32_t*)((char*)s+104) = 1; return 0; }
  case 198: return -97;
  case 214: return sys_brk(a[0]);
  case 215: fr_give(a[0], a[0]+UP(a[1])); return 0;
  case 216: { uint64_t ol = UP(a[1]), nl = UP(a[2]);
    if (nl <= ol) { fr_give(a[0]+nl, a[0]+ol); return a[0]; }
    if (!(a[3] & 1)) return -12;
    if ((r = sys_mmap(0, nl, 3, 0x22, -1, 0)) < 0) return r;
    memcpy(G(r), G(a[0]), ol); fr_give(a[0], a[0]+ol); return r; }
  case 222: return sys_mmap(a[0], a[1], a[2], a[3], a[4], a[5]);
  case 278: arc4random_buf(G(a[0]), a[1]); return a[1];
  case 220: case 435: fprintf(stderr, "a64linux: clone is not supported\n"); return -38;
  default: if (trace) fprintf(stderr, "a64linux: unimplemented syscall %llu\n", n); return -38;
  }
}

static uint64_t load_elf(const char *path, uint64_t *entry, uint64_t *phdr, uint64_t *phnum, char *interp) {
  int fd = open(path, O_RDONLY);
  if (fd < 0) { perror(path); exit(127); }
  Elf64_Ehdr eh; Elf64_Phdr ph[32];
  if (pread(fd, &eh, sizeof(eh), 0) != sizeof(eh) || memcmp(eh.e_ident, "\177ELF", 4) || eh.e_machine != EM_AARCH64 || eh.e_phnum > 32) { fprintf(stderr, "a64linux: %s is not an aarch64 ELF\n", path); exit(126); }
  pread(fd, ph, eh.e_phnum*sizeof(ph[0]), eh.e_phoff);
  uint64_t lo = ~0ULL, hi = 0, base = 0;
  for (int i = 0; i < eh.e_phnum; i++) if (ph[i].p_type == PT_LOAD) {
    if (ph[i].p_vaddr < lo) lo = ph[i].p_vaddr & ~(PG-1);
    if (ph[i].p_vaddr + ph[i].p_memsz > hi) hi = UP(ph[i].p_vaddr + ph[i].p_memsz);
  }
  if (eh.e_type == ET_DYN) { base = fr_alloc(UP(hi-lo) + 0x10000); base = ((base + 0xffff) & ~0xffffULL) - lo; if (base + hi > hiwater) hiwater = base + hi; }
  else brk_lo = brk_cur = hi;
  for (int i = 0; i < eh.e_phnum; i++) {
    if (ph[i].p_type == PT_LOAD) pread(fd, G(base + ph[i].p_vaddr), ph[i].p_filesz, ph[i].p_offset);
    if (ph[i].p_type == PT_INTERP && interp) pread(fd, interp, ph[i].p_filesz, ph[i].p_offset);
    if (ph[i].p_type == PT_PHDR && phdr) *phdr = base + ph[i].p_vaddr;
  }
  if (phdr && !*phdr) *phdr = base + lo + eh.e_phoff;
  if (phnum) *phnum = eh.e_phnum;
  *entry = base + eh.e_entry;
  close(fd);
  return base;
}

extern char **environ;
int main(int argc, char **argv) {
  char *extra[64]; int nextra = 0, ai = 1;
  for (; ai < argc && argv[ai][0] == '-'; ai += 2) {
    if (!strcmp(argv[ai], "-L")) rootfs = argv[ai+1];
    else if (!strcmp(argv[ai], "-E")) extra[nextra++] = argv[ai+1];
  }
  if (ai >= argc) { fprintf(stderr, "usage: a64linux [-L rootfs] [-E VAR=VAL] prog args...\n"); return 2; }
  trace = getenv("A64LINUX_TRACE") != NULL;

  mem = mmap(NULL, MEM_SIZE, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANON, -1, 0);
  if (mem == MAP_FAILED) { perror("mmap"); return 1; }
  CK(hv_vm_create(NULL));
  CK(hv_vm_map(mem+0x10000, 0x10000, MEM_SIZE-0x10000, HV_MEMORY_READ|HV_MEMORY_WRITE|HV_MEMORY_EXEC));
  hv_vcpu_exit_t *ex;
  CK(hv_vcpu_create(&vcpu, &ex, NULL));

  uint64_t *l1 = G(SYS_PAGE);
  for (uint64_t i = 0; i < MEM_SIZE/GB; i++) l1[i] = (i*GB) | (1<<10) | (3<<8) | 1;
  for (int i = 0; i < 1024; i++) ((uint32_t*)G(SYS_PAGE+0x1000))[i] = 0xd4000002;
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_MAIR_EL1, 0xff));
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_TCR_EL1, 25 | (1<<8) | (1<<10) | (3<<12) | (1<<23) | (1ULL<<32)));
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_TTBR0_EL1, SYS_PAGE));
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_VBAR_EL1, SYS_PAGE+0x1000));
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_CPACR_EL1, 3<<20));
  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_SCTLR_EL1, (1<<0) | (1<<2) | (1<<12) | (1<<11) | (1<<20) | (1<<22) | (1<<23) | (1<<28) | (1<<29)));

  fr[0].s = MMAP_LO; fr[0].e = MMAP_HI; nfr = 1;
  char interp[256] = {0};
  uint64_t entry, phdr = 0, phnum, ientry, ibase = 0;
  load_elf(xp(argv[ai]), &entry, &phdr, &phnum, interp);
  if (interp[0]) ibase = load_elf(xp(interp), &ientry, NULL, NULL, NULL);

  uint64_t sp = STACK_TOP, strs[512]; int ns = 0, gargc = argc - ai, nenv = 0;
  #define PUSHS(s) (sp -= strlen(s)+1, strcpy(G(sp), s), strs[ns++] = sp)
  for (int i = ai; i < argc; i++) PUSHS(argv[i]);
  for (char **e = environ; *e && ns < 440; e++) if (strncmp(*e, "PYTHONHOME=", 11) && strncmp(*e, "DYLD_", 5)) { PUSHS(*e); nenv++; }
  for (int i = 0; i < nextra; i++) { PUSHS(extra[i]); nenv++; }
  uint64_t plat = PUSHS("aarch64"), rnd = (sp -= 16);
  memcpy(G(rnd), "a64linux-random!", 16);
  uint64_t aux[] = {AT_PHDR, phdr, AT_PHENT, sizeof(Elf64_Phdr), AT_PHNUM, phnum, AT_PAGESZ, PG, AT_BASE, ibase, AT_FLAGS, 0, AT_ENTRY, entry, AT_UID, getuid(), AT_EUID, getuid(),
                    AT_GID, getgid(), AT_EGID, getgid(), AT_HWCAP, 3, AT_CLKTCK, 100, AT_RANDOM, rnd, AT_SECURE, 0, AT_PLATFORM, plat, AT_EXECFN, strs[0], AT_NULL, 0};
  sp = (sp - (1 + gargc + 1 + nenv + 1)*8 - sizeof(aux)) & ~15ULL;
  uint64_t *w = G(sp);
  *w++ = gargc;
  for (int i = 0; i < gargc; i++) *w++ = strs[i];
  *w++ = 0;
  for (int i = 0; i < nenv; i++) *w++ = strs[gargc+i];
  *w++ = 0;
  memcpy(w, aux, sizeof(aux));

  CK(hv_vcpu_set_sys_reg(vcpu, HV_SYS_REG_SP_EL1, sp));
  CK(hv_vcpu_set_reg(vcpu, HV_REG_PC, interp[0] ? ientry : entry));
  CK(hv_vcpu_set_reg(vcpu, HV_REG_CPSR, 0x3c5));

  for (;;) {
    CK(hv_vcpu_run(vcpu));
    if (ex->reason == HV_EXIT_REASON_VTIMER_ACTIVATED) { hv_vcpu_set_vtimer_mask(vcpu, true); continue; }
    uint64_t esr = 0, elr = 0, far = 0, spsr = 0, pc = 0;
    hv_vcpu_get_reg(vcpu, HV_REG_PC, &pc);
    if (ex->reason == HV_EXIT_REASON_EXCEPTION && (ex->exception.syndrome >> 26) == 0x16) {
      hv_vcpu_get_sys_reg(vcpu, HV_SYS_REG_ESR_EL1, &esr); hv_vcpu_get_sys_reg(vcpu, HV_SYS_REG_ELR_EL1, &elr);
      hv_vcpu_get_sys_reg(vcpu, HV_SYS_REG_FAR_EL1, &far); hv_vcpu_get_sys_reg(vcpu, HV_SYS_REG_SPSR_EL1, &spsr);
      if ((esr >> 26) == 0x15) {
        uint64_t a[6], n;
        for (int i = 0; i < 6; i++) hv_vcpu_get_reg(vcpu, HV_REG_X0+i, &a[i]);
        hv_vcpu_get_reg(vcpu, HV_REG_X8, &n);
        int64_t r = do_syscall(n, a);
        if (trace) fprintf(stderr, "sys %llu(%llx, %llx, %llx, %llx) = %lld\n", n, a[0], a[1], a[2], a[3], r);
        hv_vcpu_set_reg(vcpu, HV_REG_X0, r); hv_vcpu_set_reg(vcpu, HV_REG_PC, elr); hv_vcpu_set_reg(vcpu, HV_REG_CPSR, spsr);
        continue;
      }
      fprintf(stderr, "a64linux: guest fault esr=%llx pc=%llx addr=%llx\n", esr, elr, far);
    } else fprintf(stderr, "a64linux: exit reason=%x syndrome=%llx pc=%llx addr=%llx\n", ex->reason, ex->exception.syndrome, pc, ex->exception.virtual_address);
    return 139;
  }
}
