from pyfcm import FCMNotification
from model.fcm import *

push_service = FCMNotification(key)

# FCM에 긴급모드 전환 notify 요청
def sendArgentMessage():
    body = APP_SWITCH_ARGENT_MODE_STRING
    title = "긴급모드 전환"

    res = push_service.notify_multiple_devices(
        registration_ids=tokens,
        message_title = title,
        message_body = body
    )

    print(res)

# FCM에 택배도착 알림 notify 요청
def sendPackageReceivedMessage():
    body = DEVICE_PACKAGE_RECEIVED_STRING
    title = "택배 도착"

    res = push_service.notify_multiple_devices(
        registration_ids=tokens,
        message_title = title,
        message_body = body
    )

    print(res)