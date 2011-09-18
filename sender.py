import gettext
import os
import settings
import datetime

locale_path = os.path.join(settings.PROG_DIR, 'locale')
gettext.install('messages', locale_path)

lan_ru = gettext.translation('messages', locale_path, languages=['ru'])
lan_ru.install()
_ = lan_ru.gettext

class Sender(object):
    def Send(message, recipient):
        d = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.txt'
        f = open(d, 'w')
        f.write(message)
        f.close()


