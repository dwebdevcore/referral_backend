from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APIClient


class StrictAPIClient(APIClient):
    def get_ok(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        assert response.status_code == HTTP_200_OK, \
            str(response.json())
        return response

    def post_ok(self, *args, **kwargs):
        if 'format' not in kwargs and len(args) < 3:
            kwargs['format'] = 'json'
        response = super().post(*args, **kwargs)
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}, \
            str(response.json())
        return response

    def put_ok(self, *args, **kwargs):
        if 'format' not in kwargs and len(args) < 3:
            kwargs['format'] = 'json'
        response = super().put(*args, **kwargs)
        assert response.status_code == HTTP_200_OK, \
            str(response.json())
        return response

    def delete_ok(self, *args, **kwargs):
        response = super().delete(*args, **kwargs)
        assert response.status_code == HTTP_204_NO_CONTENT, \
            str(response.json())
        return response
