/* Host runner of the ztest shim: runs every registered test, prints one line per test and the result. */
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "zephyr/ztest.h"

#define MAX_TESTS 512
#define MAX_SUITES 16

struct t { const char *suite; const char *name; ztest_shim_fn fn; };
struct s { const char *suite; ztest_shim_before before; };

static struct t tests[MAX_TESTS];
static int ntests;
static struct s suites[MAX_SUITES];
static int nsuites;
static jmp_buf jb;
static int overflow;

void ztest_shim_register(const char *suite, const char *name, ztest_shim_fn fn)
{
	if (ntests < MAX_TESTS) {
		tests[ntests].suite = suite;
		tests[ntests].name = name;
		tests[ntests].fn = fn;
		ntests++;
	} else {
		overflow = 1;
	}
}

void ztest_shim_suite(const char *suite, ztest_shim_before before)
{
	if (nsuites < MAX_SUITES) {
		suites[nsuites].suite = suite;
		suites[nsuites].before = before;
		nsuites++;
	} else {
		overflow = 1;
	}
}

void ztest_shim_fail(const char *file, int line, const char *expr, long long a, long long b)
{
	printf("    assert failed %s:%d: %s (left %lld, right %lld)\n", file, line, expr, a, b);
	longjmp(jb, 1);
}

static int cmp(const void *x, const void *y)
{
	const struct t *a = x, *b = y;
	int c = strcmp(a->suite, b->suite);

	return c ? c : strcmp(a->name, b->name);
}

int main(void)
{
	int pass = 0, fail = 0;

	qsort(tests, (size_t)ntests, sizeof(tests[0]), cmp);
	for (int i = 0; i < ntests; i++) {
		ztest_shim_before before = NULL;
		int found = 0;

		for (int k = 0; k < nsuites; k++) {
			if (strcmp(suites[k].suite, tests[i].suite) == 0) {
				before = suites[k].before;
				found = 1;
			}
		}
		if (!found) {
			printf("FAIL %s.%s (suite not declared with ZTEST_SUITE)\n", tests[i].suite, tests[i].name);
			fail++;
			continue;
		}
		if (setjmp(jb) == 0) {
			if (before) {
				before(NULL);
			}
			tests[i].fn();
			printf("PASS %s.%s\n", tests[i].suite, tests[i].name);
			pass++;
		} else {
			printf("FAIL %s.%s\n", tests[i].suite, tests[i].name);
			fail++;
		}
	}
	printf("suites=%d tests=%d pass=%d fail=%d\n", nsuites, ntests, pass, fail);
	if (fail == 0 && ntests > 0 && !overflow) {
		printf("RESULT PASS tests=%d\n", ntests);
		return 0;
	}
	printf("RESULT FAIL\n");
	return 1;
}
