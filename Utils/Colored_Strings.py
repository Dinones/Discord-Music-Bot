###########################################################################################################################
#  Who doesn't like colors? Just a script to print with colors in the terminal making it more visual.                     #
###########################################################################################################################

###########################################################################################################################
####################################################     CONSTANTS     ####################################################
###########################################################################################################################

SPECIAL = {
    "Default"       : '0',
    "Bold"          : '1',
    "Italics"       : '3',
    "Underlined"    : '4',
    "Strikethrough" : '9'
}

COLORS = {
    "Black"     : '30',
    "Red"       : '31',
    "Green"     : '32',
    "Yellow"    : '33',
    "Blue"      : '34',
    "Magenta"   : '35',
    "Cyan"      : '36',
    "White"     : '37',

    "DarkGray"      : '90',
    "LightRed"      : '91',
    "LightGreen"    : '92',
    "LightYellow"   : '93',
    "LightBlue"     : '94',
    "LightMagenta"  : '95',
    "LightCyan"     : '96',
}

BACKGROUND = {
    "Black"     : '40',
    "Red"       : '41',
    "Green"     : '42',
    "Yellow"    : '43',
    "Blue"      : '44',
    "Magenta"   : '45',
    "Cyan"      : '46',
    "White"     : '47',
}

RESET_FORMAT = '\033[0;m'

INFO = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[+] {RESET_FORMAT}'
CORRECT = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[>] {RESET_FORMAT}'
WARN = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[!] {RESET_FORMAT}'
ERROR = f'\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m[X] {RESET_FORMAT}'

###########################################################################################################################
#####################################################     GENERAL     #####################################################
###########################################################################################################################

G_COULD_NOT_GET_AWS_SECRETS = \
    f'{ERROR}\033[{SPECIAL["Bold"]};{COLORS["Magenta"]}m{"[{module}] "}{RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mCould not get AWS secrets. Error: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Italics"]}m{"{error}"} {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Bold"]}mA log has been generated: {RESET_FORMAT}'+\
    f'\033[{COLORS["Red"]};{SPECIAL["Italics"]}m{"{log_path}"}{RESET_FORMAT}'