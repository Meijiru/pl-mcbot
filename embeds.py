from discord import Embed
from connect_and_launch import get_server_info, get_title


def server_info_embed():
    """ Generates embed object for server info"""
    ip, status, version = get_server_info()
    if status == None:
        status = "Maintenance"
    
    
    text = f"**IP:** {ip} \n" \
           f"**Status:** {status} \n" \
           f"**Version:** {version}"
    if get_title() == "PloudOS.com - Manage server":
        text = f"**IP:** {ip} \n" \
            f"**Status:** Maintenance \n" \
            f"**Version:** Unknown"
    
    embed = Embed()
    embed.add_field(name="Server Info", value=text, inline=False)
    return embed


def help_embed():
    """ Generates embed object for help command"""
    embed = Embed(title="Help")
    embed.add_field(name="-launch",
                    value="Launches the server",
                    inline=False)
    embed.add_field(name="-status",
                    value="Gets the server status",
                    inline=False)
    embed.add_field(name="-info",
                    value="Gets the server info",
                    inline=False)
    embed.add_field(name="-stop",
                    value="Stops the server",
                    inline=False)
    embed.add_field(name="-help",
                    value="Displays this message",
                    inline=False)
    return embed
