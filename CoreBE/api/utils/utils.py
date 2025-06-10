import uuid

class TokenGenerator:
    @staticmethod
    def generate_cli_token_uuid(acoount_id: int) -> str:
        new_uuid = str(uuid.uuid4())
        return f"{acoount_id}clitoken{new_uuid}"
