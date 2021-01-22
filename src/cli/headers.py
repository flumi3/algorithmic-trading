# Contains header that will be displayed in the cli

tab_str = "    "  # 4 blanks

HEADER_WELCOME: str = (
        "##########################\n"
        "#" + tab_str * 2 + "Welcome!" + tab_str * 2 + "#\n"
        "##########################"
)

HEADER_NEW_BACKTEST: str = (
        "#####################################\n"
        "#" + tab_str * 2 + "Create New Backtest" + tab_str * 2 + "#\n"
        "#####################################"
)

HEADER_NEW_BOT: str = (
        "################################\n"
        "#" + tab_str + "Create New Trading Bot" + tab_str + "#\n"
        "################################"
)

HEADER_DISPLAY_BOTS: str = (
        "##############################\n"
        "#" + tab_str + "Trading Bot Overview" + tab_str + "#\n"
        "##############################"
)
