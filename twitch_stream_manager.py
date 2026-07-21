# This code:
# 1. Starts and stops our video feed, effectively starting and stopping twitch streams
# 2. Connects to chat to display messages during stream
# 3. Handles turning on/off the ring light and listens for button to start/stop the stream

from twitch_chat_irc import twitch_chat_irc

def update_text_overlay(message):
    # TODO: update our list of on-screen messages
    # Then we call the command to remake our overlay text
    #draw_overlay(message)
    print(message)

#on exit:
def on_exit():
    connection.close()
    pixels.fill((0, 0, 0))

connection = twitch_chat_irc.TwitchChatIRC()
connection.listen(channel_id, on_message=update_text_overlay)