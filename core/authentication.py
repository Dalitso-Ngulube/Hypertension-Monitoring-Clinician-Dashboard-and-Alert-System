from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class JWTAuthenticationFromQueryParam(JWTAuthentication):
    """
    Allow the JWT to be supplied as a ?token= query parameter.

    Used by CSV export endpoints so the browser can trigger a download
    via window.open() without setting an Authorization header.
    """

    def authenticate(self, request):
        # Try the standard Authorization header first
        header_result = super().authenticate(request)
        if header_result is not None:
            return header_result

        # Fall back to ?token= query parameter
        raw_token = request.query_params.get('token')
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except InvalidToken as exc:
            raise AuthenticationFailed(str(exc))

        return self.get_user(validated_token), validated_token
