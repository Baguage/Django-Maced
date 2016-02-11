import collections
import random
import string
import json

from django.http import HttpResponse

BAD_ITEM_NAME_CHARACTERS = (
    "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", ".", "/", ":", ";", "<", "=", ">", "?", "@", "[", "\\",
    "]", "^", "`", "{", "|", "}", "~"
)

class MissingFromPost:
    pass


# if not isinstance(field, models.fields.AutoField):  # We don't set auto fields
#     if isinstance(field, models.fields.DateTimeField):  # Not supported yet
#         continue
#     elif isinstance(field, (models.fields.TextField, models.fields.CharField)):
#         pass
#     elif isinstance(field, models.fields.related.ForeignKey):  # Ignore warning. It is valid.
#         pass


# Something I found here: http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def update_dictionary(dictionary_to_update, dictionary_to_update_with):
    for key, value in dictionary_to_update_with.iteritems():
        if isinstance(value, collections.Mapping):
            recursion = update_dictionary(dictionary_to_update.get(key, {}), value)
            dictionary_to_update[key] = recursion
        else:
            dictionary_to_update[key] = dictionary_to_update_with[key]

    return dictionary_to_update


def is_item_name_valid(item_name):
    if any((character in BAD_ITEM_NAME_CHARACTERS) for character in item_name):
        return False

    return True


def get_bad_item_name_characters_in_string(add_quotes=False):
    string = ""

    for character in BAD_ITEM_NAME_CHARACTERS:
        if add_quotes:
            string += '"'

        string += character

        if add_quotes:
            string += '"'

        string += " "

    string.rstrip()

    return string


def validate_select_options(extra_info, field, item_name, select_type):
    if isinstance(extra_info, list):
        option_count = 0

        for option in extra_info:
            if isinstance(option, tuple):
                if len(option) == 2:
                    if isinstance(option[0], (int, str, unicode)):
                        if select_type == "object":
                            try:
                                int(option[0])
                            except ValueError:
                                raise TypeError(
                                    "Value in option number " + str(option_count) + " in field " +
                                    str(field["name"]) + " in field_list for " + str(item_name) +
                                    " is using select_type \"object\" and must be an integer or a string version of "
                                    "an integer"
                                )
                        elif select_type == "string":
                            pass  # Currently no validation

                        if not isinstance(option[1], (str, unicode)):
                            raise TypeError(
                                "Name in option number " + str(option_count) + " in field " +
                                str(field["name"]) + " in field_list for " + str(item_name) +
                                " must be a string"
                            )
                    else:
                        raise TypeError(
                            "Value in option number " + str(option_count) + " in field " +
                            str(field["name"]) + " in field_list for " + str(item_name) +
                            " must be an integer or a string"
                        )
                else:
                    raise TypeError(
                        "Option number " + str(option_count) + " in field " + str(field["name"]) +
                        " in field_list for " + str(item_name) + " is a tuple of size " + str(len(option)) +
                        " but must be a tuple where the tuple is (value, name)"
                    )
            else:
                raise TypeError(
                    "Option number " + str(option_count) + " in field " + str(field["name"]) +
                    " in field_list for " + str(item_name) +
                    " must be a tuple where the tuple is (value, name)"
                )

            option_count += 1
    else:
        raise TypeError("Options must be a list of tuples where the tuples are (value, name)")


def make_random_id(size):
    return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def serialize_item_action_data(data):
    try:
        return json.dumps(data)
    except TypeError as error:
        return HttpResponse(
            content="There was a problem serializing the item action data. This likely caused by something missing " +
                    "in select_object_models_info. If this maced item is a child of another model, be sure to " +
                    "include the _ptr for the parent class. Raised error: " + str(error),
            status=500
        )
    except Exception as error:
        return HttpResponse(
            content="There was a problem serializing the item action data. Raised error: " + str(error),
            status=500
        )


def prettify_string(ugly_string):
    pretty_string = ugly_string.title().replace("_", " ")

    return pretty_string


def is_authenticated(request, need_authentication):
    if request.user.is_authenticated() or not need_authentication:
        return True
    else:
        return False