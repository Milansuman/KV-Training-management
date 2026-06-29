class AppException(Exception):
    status_code = 500
    default_detail = "Internal server error"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        self.status_code = status_code or self.status_code
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class BadRequestException(AppException):
    status_code = 400
    default_detail = "Bad request"


class UnauthorizedException(AppException):
    status_code = 401
    default_detail = "Unauthorized"


class ForbiddenException(AppException):
    status_code = 403
    default_detail = "Forbidden"


class NotFoundException(AppException):
    status_code = 404
    default_detail = "Not found"


class ConflictException(AppException):
    status_code = 409
    default_detail = "Conflict"


class UnprocessableEntityException(AppException):
    status_code = 422
    default_detail = "Unprocessable entity"