def format_terminal_text(text, color="default", bold=False):
    """
    Returns a string formatted with ANSI escape codes for color and/or bold text.

    Args:
        text (str): The text to format.
        color (str, optional): The desired text color.
                                Valid options are: "default", "black", "red", "green",
                                "yellow", "blue", "magenta", "cyan", "white",
                                "bright_black", "bright_red", "bright_green",
                                "bright_yellow", "bright_blue", "bright_magenta",
                                "bright_cyan", "bright_white". Defaults to "default".
        bold (bool, optional): Whether to make the text bold. Defaults to False.

    Returns:
        str: The formatted string with ANSI escape codes.
    """
    color_codes = {
        "default": "0",
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "bright_black": "90",
        "bright_red": "91",
        "bright_green": "92",
        "bright_yellow": "93",
        "bright_blue": "94",
        "bright_magenta": "95",
        "bright_cyan": "96",
        "bright_white": "97",
    }

    ansi_code = "\033["

    attributes = []
    if bold:
        attributes.append("1")
    if color.lower() in color_codes:
        attributes.append(color_codes[color.lower()])
    else:
        attributes.append("0")  # Default color if invalid

    if attributes:
        ansi_code += ";".join(attributes) + "m"
    else:
        ansi_code = ""  # No formatting needed

    return f"{ansi_code}{text}\033[0m"