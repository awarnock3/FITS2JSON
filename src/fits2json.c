#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "fitsio.h"

enum {
    APP_STATUS_USAGE = -1,
    APP_STATUS_MEMORY = -2,
    APP_STATUS_WRITE = -3
};

enum value_kind {
    VALUE_NONE = 0,
    VALUE_BOOL,
    VALUE_STRING
};

struct header_card {
    char *keyword;
    enum value_kind value_kind;
    int bool_value;
    char *string_value;
    int has_comment;
    char *comment;
};

struct hdu_model {
    int index;
    int hdu_type;
    struct header_card *cards;
    size_t count;
    size_t capacity;
};

struct fits_document {
    struct hdu_model *hdus;
    size_t count;
    size_t capacity;
};

static void print_usage(FILE *stream)
{
    fprintf(stream, "Usage: fits2json filename[ext]\n\n");
    fprintf(stream, "Convert FITS header data to JSON on stdout.\n\n");
    fprintf(stream, "Examples:\n");
    fprintf(stream, "  fits2json file.fits      - convert every HDU header as a JSON array\n");
    fprintf(stream, "  fits2json file.fits[0]   - convert the primary array header\n");
    fprintf(stream, "  fits2json file.fits[2]   - convert the 2nd extension header\n");
    fprintf(stream, "  fits2json file.fits+2    - same as above\n");
    fprintf(stream, "  fits2json file.fits[GTI] - convert the GTI extension header\n\n");
    fprintf(stream, "Note that it may be necessary to enclose the input filename in\n");
    fprintf(stream, "single quotes on the Unix command line.\n");
}

static char *xstrdup(const char *value)
{
    size_t length;
    char *copy;

    if (value == NULL) {
        value = "";
    }

    length = strlen(value);
    copy = malloc(length + 1);
    if (copy == NULL) {
        return NULL;
    }

    memcpy(copy, value, length + 1);
    return copy;
}

static void free_header_card(struct header_card *card)
{
    if (card == NULL) {
        return;
    }

    free(card->keyword);
    free(card->string_value);
    free(card->comment);
    memset(card, 0, sizeof(*card));
}

static void free_hdu_model(struct hdu_model *model)
{
    size_t index;

    if (model == NULL) {
        return;
    }

    for (index = 0; index < model->count; index++) {
        free_header_card(&model->cards[index]);
    }

    free(model->cards);
    memset(model, 0, sizeof(*model));
}

static void free_fits_document(struct fits_document *document)
{
    size_t index;

    if (document == NULL) {
        return;
    }

    for (index = 0; index < document->count; index++) {
        free_hdu_model(&document->hdus[index]);
    }

    free(document->hdus);
    memset(document, 0, sizeof(*document));
}

static int append_card(struct hdu_model *model, struct header_card *card)
{
    struct header_card *new_cards;
    size_t new_capacity;

    if (model->count == model->capacity) {
        new_capacity = model->capacity == 0 ? 32 : model->capacity * 2;
        new_cards = realloc(model->cards, new_capacity * sizeof(*new_cards));
        if (new_cards == NULL) {
            return APP_STATUS_MEMORY;
        }

        model->cards = new_cards;
        model->capacity = new_capacity;
    }

    model->cards[model->count++] = *card;
    memset(card, 0, sizeof(*card));
    return 0;
}

static int append_hdu_model(struct fits_document *document, struct hdu_model *model)
{
    struct hdu_model *new_hdus;
    size_t new_capacity;

    if (document->count == document->capacity) {
        new_capacity = document->capacity == 0 ? 8 : document->capacity * 2;
        new_hdus = realloc(document->hdus, new_capacity * sizeof(*new_hdus));
        if (new_hdus == NULL) {
            return APP_STATUS_MEMORY;
        }

        document->hdus = new_hdus;
        document->capacity = new_capacity;
    }

    document->hdus[document->count++] = *model;
    memset(model, 0, sizeof(*model));
    return 0;
}

static int write_text(FILE *stream, const char *text)
{
    if (fputs(text, stream) == EOF) {
        return APP_STATUS_WRITE;
    }
    return 0;
}

static int write_json_string(FILE *stream, const char *text)
{
    const unsigned char *cursor;

    if (fputc('"', stream) == EOF) {
        return APP_STATUS_WRITE;
    }

    for (cursor = (const unsigned char *)(text == NULL ? "" : text); *cursor != '\0'; cursor++) {
        switch (*cursor) {
        case '"':
            if (fputs("\\\"", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\\':
            if (fputs("\\\\", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\b':
            if (fputs("\\b", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\f':
            if (fputs("\\f", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\n':
            if (fputs("\\n", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\r':
            if (fputs("\\r", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        case '\t':
            if (fputs("\\t", stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        default:
            if (*cursor < 0x20) {
                if (fprintf(stream, "\\u%04x", (unsigned int)*cursor) < 0) {
                    return APP_STATUS_WRITE;
                }
            } else if (fputc(*cursor, stream) == EOF) {
                return APP_STATUS_WRITE;
            }
            break;
        }
    }

    if (fputc('"', stream) == EOF) {
        return APP_STATUS_WRITE;
    }

    return 0;
}

static const char *hdu_type_name(int hdu_type)
{
    switch (hdu_type) {
    case IMAGE_HDU:
        return "IMAGE_HDU";
    case ASCII_TBL:
        return "ASCII_TBL";
    case BINARY_TBL:
        return "BINARY_TBL";
    default:
        return "UNKNOWN_HDU";
    }
}

static int selector_was_provided(const char *argument, int current_hdu)
{
    return current_hdu != 1 || strchr(argument, '[') != NULL;
}

static int fill_comment(struct header_card *card, const char *comment, int always_include)
{
    if (!always_include && (comment == NULL || comment[0] == '\0')) {
        return 0;
    }

    card->comment = xstrdup(comment);
    if (card->comment == NULL) {
        return APP_STATUS_MEMORY;
    }

    card->has_comment = 1;
    return 0;
}

static int normalize_card(fitsfile *fptr, int keynum, struct header_card *card, int *skip_card, int *status)
{
    char raw_card[FLEN_CARD];
    char keyname[FLEN_KEYWORD];
    char raw_value[FLEN_VALUE];
    char raw_comment[FLEN_COMMENT];
    int keyclass;
    char value_type = 0;
    int app_status;

    memset(card, 0, sizeof(*card));
    *skip_card = 0;

    fits_read_record(fptr, keynum, raw_card, status);
    if (*status) {
        return *status;
    }

    keyclass = fits_get_keyclass(raw_card);

    fits_read_keyn(fptr, keynum, keyname, raw_value, raw_comment, status);
    if (*status) {
        return *status;
    }

    if (keyclass == TYP_CONT_KEY) {
        *skip_card = 1;
        return 0;
    }

    card->keyword = xstrdup(keyname);
    if (card->keyword == NULL) {
        return APP_STATUS_MEMORY;
    }

    if (keyclass == TYP_COMM_KEY) {
        return fill_comment(card, raw_comment, 1);
    }

    if (fill_comment(card, raw_comment, 0) != 0) {
        return APP_STATUS_MEMORY;
    }

    fits_get_keytype(raw_value, &value_type, status);
    if (*status == VALUE_UNDEFINED) {
        *status = 0;
        return 0;
    }
    if (*status) {
        return *status;
    }

    if (value_type == 'L') {
        card->value_kind = VALUE_BOOL;
        card->bool_value = (raw_value[0] == 'T');
        return 0;
    }

    if (value_type == 'C') {
        char *long_string = NULL;
        char long_comment[FLEN_COMMENT];
        int free_status = 0;

        memset(long_comment, 0, sizeof(long_comment));
        fits_read_key_longstr(fptr, keyname, &long_string, long_comment, status);
        if (*status) {
            return *status;
        }

        card->string_value = xstrdup(long_string == NULL ? "" : long_string);
        fits_free_memory(long_string, &free_status);
        if (card->string_value == NULL) {
            return APP_STATUS_MEMORY;
        }

        if (long_comment[0] != '\0') {
            free(card->comment);
            card->comment = NULL;
            card->has_comment = 0;
            app_status = fill_comment(card, long_comment, 1);
            if (app_status != 0) {
                return app_status;
            }
        }

        card->value_kind = VALUE_STRING;
        return 0;
    }

    card->string_value = xstrdup(raw_value);
    if (card->string_value == NULL) {
        return APP_STATUS_MEMORY;
    }

    card->value_kind = VALUE_STRING;
    return 0;
}

static int read_selected_hdu_model(fitsfile *fptr, struct hdu_model *model, int *status)
{
    int nkeys = 0;
    int keynum;

    fits_get_hdu_num(fptr, &model->index);
    if (*status) {
        return *status;
    }

    fits_get_hdu_type(fptr, &model->hdu_type, status);
    if (*status) {
        return *status;
    }

    fits_get_hdrspace(fptr, &nkeys, NULL, status);
    if (*status) {
        return *status;
    }

    for (keynum = 1; keynum <= nkeys; keynum++) {
        struct header_card card;
        int skip_card = 0;
        int app_status;

        app_status = normalize_card(fptr, keynum, &card, &skip_card, status);
        if (app_status != 0) {
            free_header_card(&card);
            return app_status;
        }

        if (skip_card) {
            continue;
        }

        app_status = append_card(model, &card);
        if (app_status != 0) {
            free_header_card(&card);
            return app_status;
        }
    }

    return 0;
}

static int read_whole_file_document(fitsfile *fptr, struct fits_document *document, int *status)
{
    int hdu_count = 0;
    int hdu_index;

    fits_get_num_hdus(fptr, &hdu_count, status);
    if (*status) {
        return *status;
    }

    for (hdu_index = 1; hdu_index <= hdu_count; hdu_index++) {
        struct hdu_model model;
        int app_status;

        memset(&model, 0, sizeof(model));

        fits_movabs_hdu(fptr, hdu_index, NULL, status);
        if (*status) {
            return *status;
        }

        app_status = read_selected_hdu_model(fptr, &model, status);
        if (app_status != 0) {
            free_hdu_model(&model);
            return app_status;
        }

        app_status = append_hdu_model(document, &model);
        if (app_status != 0) {
            free_hdu_model(&model);
            return app_status;
        }
    }

    return 0;
}

static int emit_hdu_json_object(FILE *stream, const struct hdu_model *model)
{
    size_t index;
    int status;

    status = write_text(stream, "{\"index\":");
    if (status != 0) {
        return status;
    }
    if (fprintf(stream, "%d", model->index) < 0) {
        return APP_STATUS_WRITE;
    }
    status = write_text(stream, ",\"type\":");
    if (status != 0) {
        return status;
    }
    status = write_json_string(stream, hdu_type_name(model->hdu_type));
    if (status != 0) {
        return status;
    }
    status = write_text(stream, ",\"cards\":[");
    if (status != 0) {
        return status;
    }

    for (index = 0; index < model->count; index++) {
        const struct header_card *card = &model->cards[index];

        if (index > 0) {
            if (fputc(',', stream) == EOF) {
                return APP_STATUS_WRITE;
            }
        }

        status = write_text(stream, "{\"keyword\":");
        if (status != 0) {
            return status;
        }
        status = write_json_string(stream, card->keyword);
        if (status != 0) {
            return status;
        }

        if (card->value_kind != VALUE_NONE) {
            status = write_text(stream, ",\"value\":");
            if (status != 0) {
                return status;
            }

            if (card->value_kind == VALUE_BOOL) {
                status = write_text(stream, card->bool_value ? "true" : "false");
            } else {
                status = write_json_string(stream, card->string_value);
            }
            if (status != 0) {
                return status;
            }
        }

        if (card->has_comment) {
            status = write_text(stream, ",\"comment\":");
            if (status != 0) {
                return status;
            }
            status = write_json_string(stream, card->comment);
            if (status != 0) {
                return status;
            }
        }

        if (fputc('}', stream) == EOF) {
            return APP_STATUS_WRITE;
        }
    }

    return write_text(stream, "]}");
}

static int emit_hdu_json(FILE *stream, const struct hdu_model *model)
{
    int status;

    status = emit_hdu_json_object(stream, model);
    if (status != 0) {
        return status;
    }

    if (fputc('\n', stream) == EOF) {
        return APP_STATUS_WRITE;
    }

    if (fflush(stream) == EOF) {
        return APP_STATUS_WRITE;
    }

    return 0;
}

static int emit_document_json(FILE *stream, const struct fits_document *document)
{
    size_t index;
    int status;

    status = write_text(stream, "[");
    if (status != 0) {
        return status;
    }

    for (index = 0; index < document->count; index++) {
        if (index > 0) {
            if (fputc(',', stream) == EOF) {
                return APP_STATUS_WRITE;
            }
        }

        status = emit_hdu_json_object(stream, &document->hdus[index]);
        if (status != 0) {
            return status;
        }
    }

    status = write_text(stream, "]\n");
    if (status != 0) {
        return status;
    }

    if (fflush(stream) == EOF) {
        return APP_STATUS_WRITE;
    }

    return 0;
}

int main(int argc, char *argv[])
{
    fitsfile *fptr = NULL;
    struct hdu_model model;
    struct fits_document document;
    int status = 0;
    int app_status = 0;
    int current_hdu = 0;
    int close_status = 0;
    int explicit_selector = 0;

    memset(&model, 0, sizeof(model));
    memset(&document, 0, sizeof(document));

    if (argc != 2) {
        print_usage(stderr);
        return 2;
    }

    if (fits_open_file(&fptr, argv[1], READONLY, &status)) {
        fits_report_error(stderr, status);
        return status;
    }

    fits_get_hdu_num(fptr, &current_hdu);
    if (status == 0) {
        explicit_selector = selector_was_provided(argv[1], current_hdu);
    }

    if (status == 0 && explicit_selector) {
        app_status = read_selected_hdu_model(fptr, &model, &status);
    } else if (status == 0) {
        app_status = read_whole_file_document(fptr, &document, &status);
    }

    if (fptr != NULL) {
        fits_close_file(fptr, &close_status);
        if (status == 0 && close_status != 0) {
            status = close_status;
        }
    }

    if (status == 0 && app_status == 0) {
        if (explicit_selector) {
            app_status = emit_hdu_json(stdout, &model);
        } else {
            app_status = emit_document_json(stdout, &document);
        }
    }

    free_hdu_model(&model);
    free_fits_document(&document);

    if (status != 0) {
        fits_report_error(stderr, status);
        return status;
    }

    if (app_status == APP_STATUS_MEMORY) {
        fprintf(stderr, "fits2json: out of memory while building JSON output\n");
        return 1;
    }

    if (app_status == APP_STATUS_WRITE) {
        fprintf(stderr, "fits2json: failed while writing JSON output\n");
        return 1;
    }

    if (app_status != 0) {
        fprintf(stderr, "fits2json: unexpected internal error\n");
        return 1;
    }

    return 0;
}
