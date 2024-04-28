from enum import Enum


def add_enum_members_to_docstr(enum_class: type[Enum]):
    """Adds the docstrings of the enum values to the enum class.

    This is useful to have the docstrings of the enum values in the OpenAPI
    documentation.
    """

    indentation = " " * 4

    # the 4 white spaces are needed to have a consistent indentation in the docs
    member_doc_prefix = f"\n{indentation}- "
    enum_class.__doc__ = (
        enum_class.__doc__ or f"Possible values of {enum_class.__name__}"
    ) + "\n"
    enum_class.__doc__ += member_doc_prefix + member_doc_prefix.join(
        f"{u.value} = {u.name}" for u in enum_class
    )
