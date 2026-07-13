import sys
import irc.bot
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QTextBrowser, QVBoxLayout, pyqtSignal

class TwitchBot(irc.bot.SingleServerIRCBot):
    self.newMsg = pyqtSignal(str)

    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print 'Connecting to ' + server + ' on port ' + str(port) + '...'
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        

    def on_welcome(self, c, e):
        print 'Joining ' + self.channel

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        self.newMsg.emit(e.arguments[0])
        # If a chat message starts with an exclamation point, try to run it as a command
        # if e.arguments[0][:1] == '!':
        #     cmd = e.arguments[0].split(' ')[0][1:]
        #     print 'Received command: ' + cmd
        #     self.do_command(e, cmd)
        return

class App(QMainWindow):
    self.current_text = ""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTextBrowser")
        # Set window size
        self.setGeometry(100, 100, 400, 300)

        # Create a vertical layout
        layout = QVBoxLayout(self)

        # Create a QTextBrowser
        self.text_browser = QTextBrowser(self)
        # Enable opening external links
        self.text_browser.setOpenExternalLinks(True)  

        # Set some sample text (you can replace this with your own content)
        self.text_browser.setPlainText("Welcome to the QTextBrowser demo!\n\n"
                "This widget allows you to display rich text, "
                "including hyperlinks and formatting.")

        # Add the QTextBrowser to the layout
        layout.addWidget(self.text_browser)
        twitch_bot.newMsg.connect(self.on_new_text)

    def on_new_text(self, new_text):
        self.current_text = self.current_text +"\n" + new_text
        self.text_browser.setPlainText(self.current_text)

if __name__ == '__main__':
    twitch_bot = TwitchBot(username, client_id, token, channel)
    twitch_bot.start()
    app = QApplication(sys.argv)
    ex = App()
    twitch_bot.newMsg.disconnect()
    sys.exit(app.exec_())