from typing import Any
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

from authorizenet.apicontractsv1 import (
    customerProfileType,
    createCustomerProfileRequest,
    getCustomerProfileRequest,
    deleteCustomerProfileRequest,
    updateCustomerProfileRequest,
)
from authorizenet.apicontrollers import (
    createCustomerProfileController,
    deleteCustomerProfileController,
    getCustomerProfileController,
    updateCustomerProfileController,
)

from terminusgps_tracker.integrations.authorizenet import (
    get_merchant_auth,
    get_environment,
)
from terminusgps_tracker.integrations.wialon.items import (
    WialonUnitGroup,
    WialonUser,
    WialonResource,
)
from terminusgps_tracker.integrations.wialon.session import WialonSession


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_group_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_end_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"
        permissions = [
            ("update_profile_user", "Can change the user associated with the profile.")
        ]

    def __str__(self) -> str:
        return f"{self.user}'s Profile"

    def save(self, **kwargs) -> None:
        if self.authorizenet_id is None:
            self.authorizenet_id = self.authorizenet_create_customer_profile()
        if self.wialon_super_user_id is None:
            with WialonSession() as session:
                admin_id: int = settings.WIALON_ADMIN_ID
                self.wialon_create_profile_objects(admin_id, session)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        if self.authorizenet_id is not None:
            self.authorizenet_delete_customer_profile(profile_id=self.authorizenet_id)
        return super().delete(*args, **kwargs)

    def wialon_create_profile_objects(
        self, admin_id: int, session: WialonSession
    ) -> None:
        admin_user = WialonUser(id=str(admin_id), session=session)
        super_user = WialonUser(
            owner=admin_user,
            name=f"super_{self.user.email}",
            password=self.user.password,
            session=session,
        )
        end_user = WialonUser(
            owner=super_user,
            name=self.user.email,
            password=self.user.password,
            session=session,
        )
        group = WialonUnitGroup(
            owner=super_user, name=f"group_{self.user.email}", session=session
        )
        resource = WialonResource(
            owner=super_user, name=f"resource_{self.user.email}", session=session
        )

        self.wialon_super_user_id = super_user.id
        self.wialon_end_user_id = end_user.id
        self.wialon_group_id = group.id
        self.wialon_resource_id = resource.id

    def authorizenet_create_customer_profile(self) -> int:
        merchantAuthentication = get_merchant_auth()
        request = createCustomerProfileRequest(
            merchantAuthentication=merchantAuthentication,
            profile=customerProfileType(
                merchantCustomerId=str(self.user.pk), email=str(self.user.email)
            ),
        )

        controller = createCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return int(response.customerProfileId)

    @classmethod
    def authorizenet_get_customer_profile(
        cls, profile_id: int | None = None, merchant_id: int | None = None
    ) -> dict[str, Any] | None:
        if not profile_id or not merchant_id:
            raise ValueError("No 'profile_id' or 'merchant_id' provided.")

        request = getCustomerProfileRequest(merchantAuthentication=get_merchant_auth())
        if profile_id:
            request.customerProfileId = str(profile_id)
        if merchant_id:
            request.merchantCustomerId = str(merchant_id)

        controller = getCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return response

    @classmethod
    def authorizenet_update_customer_profile(cls, merchant_id: int) -> None:
        request = updateCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            merchantCustomerId=str(merchant_id),
        )

        controller = updateCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @classmethod
    def authorizenet_delete_customer_profile(cls, profile_id: int) -> None:
        request = deleteCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
        )

        controller = deleteCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
