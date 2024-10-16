from django.db import models
from django.contrib.auth import get_user_model

from terminusgps_tracker.wialonapi.items.base import WialonBase
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import (
    WialonUser,
    WialonResource,
    WialonUnitGroup,
)
from terminusgps_tracker.wialonapi.constants import (
    UNIT_FULL_ACCESS_MASK,
    UNIT_BASIC_ACCESS_MASK,
)


class CustomerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    aws_sso_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_profile_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_payment_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_address_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_subscription_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_group_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    def delete(self, using=None, keep_parents=False):
        with WialonSession() as session:
            user = self.get_wialon_user(session)
            group = self.get_wialon_group(session)
            super_user = self.get_wialon_super_user(session)
            resource = self.get_wialon_resource(session)

            if all([super_user, user, group, resource]):
                user.delete()
                group.delete()
                resource.delete()
                super_user.delete()
            else:
                raise ValueError(
                    "Failed to properly retrieve Wialon objects for deletion."
                )
        return super().delete(using=using, keep_parents=keep_parents)

    def get_wialon_user(self, session: WialonSession) -> WialonUser | None:
        if self.wialon_user_id:
            return WialonUser(id=str(self.wialon_user_id), session=session)

    def get_wialon_super_user(self, session: WialonSession) -> WialonUser | None:
        if self.wialon_super_user_id:
            return WialonUser(id=str(self.wialon_super_user_id), session=session)

    def get_wialon_resource(self, session: WialonSession) -> WialonResource | None:
        if self.wialon_resource_id:
            return WialonResource(id=str(self.wialon_resource_id), session=session)

    def get_wialon_group(self, session: WialonSession) -> WialonUnitGroup | None:
        if self.wialon_group_id:
            return WialonUnitGroup(id=str(self.wialon_group_id), session=session)

    def add_item(self, item: WialonBase, session: WialonSession) -> None:
        group = self.get_wialon_group(session)
        if group is not None:
            group.add_item(item)

    def rm_item(self, item: WialonBase, session: WialonSession) -> None:
        group = self.get_wialon_group(session)
        if group is not None and str(item.id) in group.items:
            group.rm_item(item)

    def _grant_access(self, session: WialonSession) -> None:
        group = self.get_wialon_group(session)
        super_user = self.get_wialon_super_user(session)
        user = self.get_wialon_user(session)

        if all([group, super_user, user]):
            group.grant_access(super_user, access_mask=UNIT_FULL_ACCESS_MASK)
            group.grant_access(user, access_mask=UNIT_BASIC_ACCESS_MASK)
