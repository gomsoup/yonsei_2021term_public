from flask_restx import Namespace, fields
from werkzeug.datastructures import FileStorage

communicator = Namespace(
    name = 'upload',
    description = "Arduino와 APP의 통신을 위해 사용되는 API"
)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

NOTIFY_IDLE=0
APP_SWITCH_ARGENT_MODE = 1
APP_SWITCH_NORMAL_MODE = 2
DEVICE_PACKAGE_RECEIVED = 3
DEVICE_ALERT_ARGENT = 4
DEVICE_SET_ARGENT = 5
DEVICE_SET_NORMAL = 6
NOTIFY_ARGENT =7

parser = communicator.parser()
parser.add_argument('Content-type :', location='headers', required=True, help='Header의 Content type은 반드시 multipart/form-data 로 지정되어야 함')
parser.add_argument('image', type=FileStorage, location='files', required = True, help='Body의 image 필드에 jpg, png, jpeg 확장자의 이미지를 첨부하여 전송해야 함')
parser.add_argument('message', type=int, required=True, 
                                help='이미지의 업로드 상황을 나타내는 메시지. 다음과 같은 정수로 전송이 필요함.\n \
                                0 : DEVICE_PACKAGE_RECIEVED. Package가 도착했을 경우\n \
                                1 : DEVICE_ALERT_ARGENT. 장치가 흔들림 등 긴급상황 감지\n')

arduino_post_parser = communicator.parser()
arduino_post_parser.add_argument('message', type=int, required=True, 
                        help = '디바이스 상태 전환을 나타내는 메시지 코드. 다음과 같은 문자(char)로 전송이 필요함 \n \
                            3 : DEVICE_PACKAGE_RECEIVED. 택배가 도착되었을 경우\n \
                            4 : DEVICE_ALERT_ARGENT. 장치가 긴급 모드로 전환되었을 경우\n \
                            ')

app_post_parser = communicator.parser()
app_post_parser.add_argument('message', type=int, required=True,
                            help='앱에서 디바이스의 상태를 전환하는 메시지코드. 다음과 같은 문자(char)로 전송이 필요함 \n \
                                1 : APP_SWITCH_ARGENT_MODE. 장치를 긴급 모드로 전환할 경우 \n \
                                2 : APP_SWITCH_NORMAL_MODE. 장치를 일반 모드로 전환할 경우 \n \
                                    '
)

upload_res_success_model = communicator.model('res__success_model', {
    'ret' : fields.String(description='성공 메시지', required = True, example="Success")
})

arduino_get_success_model = communicator.model('res_arduino_get_success_model', {
    'currentState' : fields.String(description = '현재 기기 상태 코드', required=True, example='1'),
    'Description' : fields.String(description = '현재 상태 코드 설명', required=True, example='APP_SWITCH_ARGENT_MODE'),
    'ret' : fields.String(description = '성공 메시지', required=True, example="Sucss")
})

upload_res_fail_model = communicator.model('res_fail_model', {
    'ret' : fields.String(description='실패 메시지', required = True, example="error occured while commit log")
})

upload_res_failed_with_dev_model = communicator.inherit('res_failed_with_dev_model', upload_res_fail_model, {
    'dev_ret' : fields.String(description='디버깅 메시지', example='user did\'t post message field')
})

upload_res_server_failed_with_dev_model = communicator.inherit('res_server_failed_with_dev_model', upload_res_fail_model, {
    'dev_ret' : fields.String(description='디버깅 메시지', example='Database Error')
})
