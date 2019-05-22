from rest_framework.routers import DefaultRouter


class ExtendableDefaultRouter(DefaultRouter):
    def extend(self, router: DefaultRouter) -> 'ExtendableDefaultRouter':
        self.registry.extend(router.registry)
        return self
