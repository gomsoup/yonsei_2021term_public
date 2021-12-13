from flask import jsonify, current_app

class CustomError(Exception):
    def __init__(self, status, error_msg, dev_error = None):
        self.status_code = status
        self.error_msg = error_msg
        self.dev_error = dev_error
        self.is_dev_mode = current_app.debug
        print(self.is_dev_mode)

    def get_error_response(self):
        if not self.is_dev_mode:
            return jsonify({'ret' : self.error_msg}), self.status_code
        else:
            return jsonify({'ret' : self.error_msg, 'dev_ret' : self.dev_error}), self.status_code
        
class UserInputError(CustomError):
    def __init__(self, error_msg, dev_error = None):
        status_code = 400
        super().__init__(status_code, error_msg, dev_error)

class ServerGeneralError(CustomError):
    def __init__(self, error_msg,  dev_error = None):
        status_code = 500
        super().__init__(status_code, error_msg, dev_error)

class ServerDatabaseError(CustomError):
    def __init__(self, error_msg,  dev_error = None):
        status_code = 500
        super().__init__(status_code, error_msg, dev_error)


def error_handle(app):

    @app.errorhandler(UserInputError)
    def handle_user_input_error(e):
        return e.get_error_response()

    @app.errorhandler(ServerGeneralError)
    def handle_server_general_error(e):
        return e.get_error_response()

    @app.errorhandler(ServerDatabaseError)
    def handle_server_general_error(e):
        return e.get_error_response()