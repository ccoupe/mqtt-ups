# from https://github.com/K-MTG/ups_shutdown/blob/master/ups_monitor.py


import smtplib
import requests
import time
from nut2 import PyNUTClient
from subprocess import call

CHECK_INTERVAL = 60  # Seconds - how often to check UPS status
UPS_SHUTDOWN_PER_THRES = 8  # percentage on when to shutdown hub
UPS_SHUTDOWN_MIN_THRES = 8 # minutes remaining on when to shutdown hub

def shutdown_hubitat():
    ip = '10.0.1.20'  # Hubitat IP Address
    login_data = {  # Hubitat Login Credentials
        'username': 'admin',
        'password': 'mypassword'
    }

    with requests.Session() as s:
        try:
            s.get('http://%s/login' % (ip), timeout=5)
            s.post('http://%s/login' % (ip), data=login_data, timeout=5)
            s.post('http://%s/hub/shutdown' % (ip), timeout=5)
            print("Shutdown Command Sent")
        except:
            print("Shutdown Failed")


def send_email(subject):
    # GMAIL Login
    user = 'myemail@gmail.com'
    pwd = 'mypassword'
    recipient = 'myrecepient@icloud.com'

    body = subject
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
    except Exception as e:
        print ("failed to send mail")
        print(e)


opt_track = {
    'on_battery_email_sent': False,
    'shutdown_email_sent': False,
    'script_error': False
}

print("Running Script")

while True:
    status = {}
    try:
        with PyNUTClient() as s:
            status = s.list_vars("ups")
    except:
        pass

    if 'ups.status' not in status or 'battery.charge' not in status or 'battery.runtime' not in status:
        print("Can't Reach UPS")
        print(time.ctime())
        print()
        if opt_track['script_error'] is False:
            opt_track['script_error'] = True
            send_email('UPS script error')

        time.sleep(60)
        continue


    if opt_track['on_battery_email_sent'] is False and "OL" not in status['ups.status']:
        print("Power Outage")
        opt_track['on_battery_email_sent'] = True
        send_email('Home on UPS Power')

    elif opt_track['on_battery_email_sent'] is True and "OL" in status['ups.status']:
        print("Power Restored")
        opt_track['on_battery_email_sent'] = False
        opt_track['shutdown_email_sent'] = False
        send_email('Home Power Restored')

    if opt_track['shutdown_email_sent'] is False and (int(status['battery.charge']) <= UPS_SHUTDOWN_PER_THRES or int(status['battery.runtime']) <= UPS_SHUTDOWN_MIN_THRES*60) and "OL" not in status[
        'ups.status']:
        print("Shutting Down")
        opt_track['on_battery_email_sent'] = True
        opt_track['shutdown_email_sent'] = True
        send_email('Home - Shutting Down Pi & Hubitat')
        shutdown_hubitat()
        time.sleep(3)
        call("sudo shutdown -h now", shell=True) # Shutdown Raspberry Pi

    time.sleep(CHECK_INTERVAL)
