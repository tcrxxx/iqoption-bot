from pushbullet import Pushbullet
import config

DEFAULT_TITLE="[Summary IQOption]"

pb = Pushbullet(config.PUSHBULLET_API_TOKEN)

devices = pb.devices
phone = devices[0] #change number to change device

#print devices
print("--------------------------------------------------------------------------------------------------------------")
print("PushBullet Device Logged:",phone)
print("--------------------------------------------------------------------------------------------------------------")

def push_note_phone(title,message):
    print("push note to phone:",title)
    pb.push_note(DEFAULT_TITLE + title, message, device=phone)