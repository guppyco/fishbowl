from accounts.models import IpTracker


class IpTrackerMiddleware:
    """
    Calling IpTracker will save all ip addresses of logged in users.
    As a piece of middleware, this is run upon every request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        ip = self.get_client_ip(request)

        if user.is_authenticated:
            IpTracker.objects.get_or_create(
                user_profile=user,
                ip=ip,
            )

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request) -> str:
        """
        Get client ip address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        return ip
