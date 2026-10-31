class ApplicationError(Exception):
    status_code = 500
    code = "application_error"


class ExternalServiceError(ApplicationError):
    status_code = 503
    code = "external_service_unavailable"