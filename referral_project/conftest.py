import io
from contextlib import contextmanager

import pytest
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from faker import Faker

from referral_project.users.tests.factories import UserFactory
from referral_project.utils.django import create_jpeg_image, create_png_image, create_simple_uploaded_jpeg_image
from referral_project.utils.pytest.comparators import Comparator
from referral_project.utils.rest_framework.test import StrictAPIClient


@pytest.fixture(scope='session')
def faker() -> Faker:
    return Faker()


@pytest.fixture
def authenticated_user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def unauthenticated_user() -> settings.AUTH_USER_MODEL:
    # Not relying on `authenticated_user` fixture so as to prevent
    # unwanted user caching over multiple fixtures.
    user = UserFactory()
    user.api_client = StrictAPIClient()
    return user


@pytest.fixture
def jpeg_image() -> ContentFile:
    return create_jpeg_image()


@pytest.fixture
def png_image() -> ContentFile:
    return create_png_image()


@pytest.fixture
def simple_uploaded_jpeg_image() -> SimpleUploadedFile:
    return create_simple_uploaded_jpeg_image()


@pytest.fixture
def avatar(
    faker: Faker,
    jpeg_image: ContentFile,
):
    """
    JPEG file appropriate for API Client POST method with 'multipart'
    format.
    """

    avatar = io.BytesIO()
    avatar.write(jpeg_image.read())
    avatar.name = faker.file_name(extension='jpeg')
    avatar.seek(0)
    return avatar


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


ORIGINAL_MEDIA_ROOT = settings.MEDIA_ROOT


# TODO: copy-pasted from pytest-django master -- remove after another major package release
@pytest.fixture(scope='function')
def django_assert_num_queries(pytestconfig):
    import sqlparse
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    @contextmanager
    def _assert_num_queries(num):
        with CaptureQueriesContext(connection) as context:
            yield
            if num != len(context):
                msg = "Expected to perform %s queries but %s were done" % (
                    num, len(context))
                if pytestconfig.getoption('verbose') > 0:
                    sqls = (sqlparse.format(
                        q['sql'],
                        reindent=True,
                        keyword_case='upper',
                    ) for q in context.captured_queries)
                    msg += '\n\nQueries:\n========\n\n%s' % '\n\n'.join(sqls)
                else:
                    msg += " (add -v option to show queries)"
                pytest.fail(msg)

    return _assert_num_queries


def pytest_assertrepr_compare(op, left, right):
    if op != "==":
        return
    if isinstance(left, Comparator) and isinstance(right, Comparator):
        raise Exception('Can not compare two comparators')
    elif isinstance(left, Comparator):
        comparator = left
        other = right
    elif isinstance(right, Comparator):
        comparator = right
        other = left
    else:
        return
    try:
        return comparator.pytest_diff(other)
    except NotImplementedError:
        pass


def pytest_collection_modifyitems(items):
    transactional_fixtures = {
        'pusher_mock',
        'firebase_mock',
        'django_assert_num_queries',
    }
    for item in items:
        if transactional_fixtures & set(item._fixtureinfo.argnames):
            item.add_marker(pytest.mark.django_db(transaction=True))
        else:
            item.add_marker(pytest.mark.django_db)
