#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fitsio.h"

static int create_fixture(const char *path)
{
    fitsfile *fptr = NULL;
    int status = 0;
    int logical_true = 1;
    long naxes[1] = {0};
    char *create_path;
    const char *long_value =
        "This synthetic long string exists to verify CONTINUE folding, JSON escaping, "
        "and that Phase 2 emits one logical card instead of duplicated physical helpers.";

    create_path = malloc(strlen(path) + 2);
    if (create_path == NULL) {
        fprintf(stderr, "out of memory\n");
        return 1;
    }

    create_path[0] = '!';
    strcpy(create_path + 1, path);

    fits_create_file(&fptr, create_path, &status);
    fits_create_img(fptr, BYTE_IMG, 0, naxes, &status);
    fits_write_key(fptr, TLOGICAL, "BOOLKEY", &logical_true, "phase 2 boolean", &status);
    fits_write_key(fptr, TSTRING, "SHORTSTR", "phase-2-short", "short string", &status);
    fits_write_key_longstr(fptr, "LONGSTR", long_value, "phase 2 long string", &status);
    fits_write_key(fptr, TSTRING, "HIERARCH LONG.KEY", "VALUE", "hierarch value", &status);
    fits_write_comment(fptr, "phase 2 synthetic comment", &status);
    fits_write_history(fptr, "phase 2 synthetic history", &status);
    fits_close_file(fptr, &status);

    free(create_path);

    if (status) {
        fits_report_error(stderr, status);
        return status;
    }

    return 0;
}

int main(int argc, char *argv[])
{
    if (argc != 2) {
        fprintf(stderr, "Usage: %s output.fits\n", argv[0]);
        return 2;
    }

    return create_fixture(argv[1]);
}
