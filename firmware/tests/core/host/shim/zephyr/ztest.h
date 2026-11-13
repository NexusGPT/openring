/*
 * Host shim of the small part of Zephyr ztest the core tests use, so the same
 * test bodies compile with the Mac's cc. Not Zephyr: the Zephyr run is the real proof.
 * Supported: ZTEST_SUITE (before hook only), ZTEST, zassert_true, zassert_false,
 * zassert_equal, zassert_not_equal, zassert_is_null, zassert_not_null, zassert_unreachable.
 */
#ifndef ZTEST_HOST_SHIM_H
#define ZTEST_HOST_SHIM_H

#include <stddef.h>
#include <stdbool.h>

typedef void (*ztest_shim_fn)(void);
typedef void (*ztest_shim_before)(void *fixture);

void ztest_shim_register(const char *suite, const char *name, ztest_shim_fn fn);
void ztest_shim_suite(const char *suite, ztest_shim_before before);
void ztest_shim_fail(const char *file, int line, const char *expr, long long a, long long b);

#define ZTEST_SUITE(suite, pred, setup, before, after, teardown) \
	__attribute__((constructor)) static void ztest_shim_suite_##suite(void) \
	{ ztest_shim_suite(#suite, (before)); }

#define ZTEST(suite, fn) \
	static void suite##_##fn(void); \
	__attribute__((constructor)) static void ztest_shim_reg_##suite##_##fn(void) \
	{ ztest_shim_register(#suite, #fn, suite##_##fn); } \
	static void suite##_##fn(void)

#define zassert_true(c, ...) \
	do { if (!(c)) { ztest_shim_fail(__FILE__, __LINE__, #c, 0, 0); } } while (0)
#define zassert_false(c, ...) \
	do { if (c) { ztest_shim_fail(__FILE__, __LINE__, "!(" #c ")", 0, 0); } } while (0)
#define zassert_equal(a, b, ...) \
	do { long long za_ = (long long)(a), zb_ = (long long)(b); \
	     if (za_ != zb_) { ztest_shim_fail(__FILE__, __LINE__, #a " == " #b, za_, zb_); } } while (0)
#define zassert_not_equal(a, b, ...) \
	do { long long za_ = (long long)(a), zb_ = (long long)(b); \
	     if (za_ == zb_) { ztest_shim_fail(__FILE__, __LINE__, #a " != " #b, za_, zb_); } } while (0)
#define zassert_is_null(p, ...) zassert_true((p) == NULL)
#define zassert_not_null(p, ...) zassert_true((p) != NULL)
#define zassert_unreachable(...) ztest_shim_fail(__FILE__, __LINE__, "unreachable", 0, 0)

#endif
