TESTING = False

class ProductionEnv:
    # FILL-IN:
    TOKEN = ''
    COIN_MARKET_CAP_KEY = ''

    PREFIX = '!'
    COLOR = 0x57408b

    # Cool games
    STATUS = [
        'Blood',
        'Call Of Duty: Black Ops',
        'Call Of Duty: Black Ops II',
        'Call Of Duty: Modern Warfare',
        'Call Of Duty: Modern Warfare 2',
        'Call Of Duty: Modern Warfare 3',
        'Cities: Skylines',
        'Cyberpunk 2077',
        'Don\'t Starve Together',
        'DOOM',
        'DOOM 2',
        'DOOM 3',
        'DOOM 2016',
        'Doom Eternal',
        'Duke Nuke Em 3D',
        'Factorio',
        'Fallout: New Vegas',
        'Final Fantasy VII',
        'Fortnite',
        'Grand Theft Auto V',
        'Half Life',
        'Half Life 2',
        'Hotline Miami',
        'Hotline Miami 2'
        'Minecraft',
        'Need For Speed Most Wanted',
        'Portal',
        'Portal 2',
        'Quake',
        'Quake 2',
        'Quake 3 Arena',
        'Return To Castle Wolfenstein',
        'Shadow Warrior',
        'The Elder Scrolls V: Skyrim',
        'Star Craft',
        'Star Craft 2',
        'Stardew Valley',
        'Team Fortress 2',
        'Terraria',
        'Warcraft',
        'Warcraft II',
        'Warcraft III',
        'The Witcher 3: Wild Hunt',
        'Wolfenstein 3D',
        'World Of Warcraft'
    ]

    DB_FILE = 'production.db'

    # FILL-IN: Various discord IDs
    GUILD = 0
    MOD_ROLE = 0
    MUTED_ROLE = 0
    WELCOME_CHANNEL = 0
    BOT_CHANNEL = 0

    WELCOME_MSG = 'Welcome to Midgar! Please read the rules, and most importantly have fun! **Please do not block this bot, as it is used to inform our members of punishments.**'

    MUTE_MSG = 'We\'re sorry, but you have been muted for violating one of our rules.'
    UNMUTE_MSG = 'You have been unmuted.'
    WARN_MSG = description='We\'re sorry, but you have been warned for violating one of our rules.'
    KICK_MSG = description='We\'re sorry, but you have been kicked for violating one of our rules.'
    BAN_MSG = description='We\'re sorry, but you have been banned for violating one of our rules.'
    UNBAN_MSG = description='You have been unbanned.' # TODO

    WARN_IMG = 'images/warning.jpg'

class TestingEnv:
    # FILL-IN:
    TOKEN = ''

    COIN_MARKET_CAP_KEY = ProductionEnv.COIN_MARKET_CAP_KEY
    PREFIX = ProductionEnv.PREFIX
    COLOR = ProductionEnv.COLOR

    STATUS = ProductionEnv.STATUS
    DB_FILE = 'testing.db'

    # FILL IN:
    GUILD = 0
    MOD_ROLE = 0
    MUTED_ROLE = 0
    WELCOME_CHANNEL = 0
    BOT_CHANNEL = 0

    WELCOME_MSG = ProductionEnv.WELCOME_MSG
    MUTE_MSG = ProductionEnv.MUTE_MSG
    UNMUTE_MSG = ProductionEnv.UNMUTE_MSG
    WARN_MSG = ProductionEnv.WARN_MSG
    KICK_MSG = ProductionEnv.KICK_MSG
    BAN_MSG = ProductionEnv.BAN_MSG
    UNBAN_MSG = ProductionEnv.UNBAN_MSG

    WARN_IMG = ProductionEnv.WARN_IMG

if TESTING:
    config = TestingEnv
else:
    config = ProductionEnv
