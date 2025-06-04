from api.service.auth_service import auth_service

class AuthController:
    def __init__(self):
        self.auth_service = auth_service
    
    def check_health(self):
        return self.auth_service.get_health_status()

auth_controller = AuthController()
