import json

from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.openapi import Parameter, IN_QUERY

from . import serializers


class AuthenticationAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys):
        return ["Authentication endpoints"]


# login = {
#     "auto_schema": AuthenticationAutoSchema,
#     "operation_summary": "Login",
#     "method": "POST",
#     "request_body": serializers.LoginSerializer,
#     "responses": {
#         200: serializers.UserTokenSerializer,
#         401: json.dumps(messages.WRONG_CREDENTIALS),
#     },
# }
#
#
# register = {
#     "auto_schema": AuthenticationAutoSchema,
#     "operation_summary": "Register",
#     "method": "POST",
#     "request_body": serializers.RegisterSerializer,
#     "responses": {200: serializers.UserTokenSerializer},
# }

user_permission = {
    'method': 'post',
    'request_body': serializers.PermissionAssignSerializer
}
