from __future__ import annotations

"""This module contains the types related to Accounts."""

__all__ = [
    "Template",
    "NewTemplate",
    "TemplateResponse",
    "TemplateStatus",
    "AccountUpdate",
]

import dataclasses
import logging
import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    TypedDict,
)


from .. import utils

from .base_update import BaseUpdate  # noqa
from .callback import CallbackDataT, _resolve_callback_data  # noqa

if TYPE_CHECKING:
    from ..client import WhatsApp

_logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True, frozen=True, kw_only=True)
class AccountUpdate(BaseUpdate):
    """
    Represents an Account Update.

    Attributes:
        id: ID of Whatsapp Business Accounts this update belongs to.
        timestamp: Timestamp of the update.
        phone_number: Phone number of the account.
        event: The event that occured.(the account was verified, banned, etc.)
        waba_ban_state: The state of the WABA ban if the account is banned.
        waba_ban_date: The date the WABA was banned if the account is banned.
        violation_type: The type of violation.
        lock_info_expiration: The expiration date of the lock if the account is locked.
        restriction_type: The type of restriction.
        restriction_info_expiration: The expiration date of the restriction.
        business_verification_status: The status of the business verification.
        partner_client_certification_info: Information about the partner client certification.
        waba_info: Information about the Whatsapp Business Account.
        auth_international_rate_eligibility: Information about the international rate eligibility.
    """

    id: str
    timestamp: datetime.datetime
    phone_number: str
    event: str
    waba_ban_state: str | None = None
    waba_ban_date: str | None = None
    violation_type: str | None = None
    lock_info_expiration: datetime.datetime | None = None
    restriction_type: str | None = None
    restriction_info_expiration: datetime.datetime | None = None
    business_verification_status: str | None = None
    partner_client_certification_info: PartnerClientCertificationInfo | None = None
    waba_info: WabaInfo
    auth_international_rate_eligibility: AuthInternationalRateEligibility | None = None

    @classmethod
    def from_update(cls, client: WhatsApp, update: dict) -> AccountUpdate:
        value = (data := update["entry"][0])["changes"][0]["value"]
        return cls(
            _client=client,
            raw=update,
            id=data["id"],
            timestamp=datetime.datetime.fromtimestamp(data["time"]),
            phone_number=value["phone_number"],
            event=value["event"],
            waba_ban_state=value["ban_info"]["waba_ban_state"],
            waba_ban_date=value["ban_info"]["waba_ban_date"],
            violation_type=value["violation_info"]["violation_type"],
            lock_info_expiration=datetime.datetime.fromtimestamp(
                value["lock_info"]["expiration"]
            ),
            restriction_type=value["restriction_info"]["restriction_type"],
            restriction_info_expiration=datetime.datetime.fromtimestamp(
                value["restriction_info"]["expiration"]
            ),
            bussiness_verification_status=value.get("business_verification_status"),
            partner_client_certification_info=cls.PartnerClientCertificationInfo(
                client_business_id=value["partner_client_certification_info"][
                    "client_business_id"
                ],
                status=value["partner_client_certification_info"]["status"],
                rejection_reasons=value["partner_client_certification_info"][
                    "rejection_reasons"
                ],
            ),
            waba_info=cls.WabaInfo(
                waba_id=value["waba_info"]["waba_id"],
                owner_business_id=value["waba_info"]["owner_business_id"],
                solution_id=value["waba_info"]["solution_id"],
                solution_partner_business_ids=value["waba_info"][
                    "solution_partner_business_ids"
                ],
                is_obo_to_shared_migrated=value["waba_info"][
                    "is_obo_to_shared_migrated"
                ],
            ),
            auth_international_rate_eligibility=cls.AuthInternationalRateEligibility(
                start_time=value["auth_international_rate_eligibility"]["start_time"],
                exception_countries=value["auth_international_rate_eligibility"][
                    "exception_countries"
                ],
            ),
        )

    class PartnerClientCertificationInfo(TypedDict):
        """
        Information about the partner client certification.

        Attributes:
            client_business_id: The business ID of the client.
            status: The status of the certification.
            rejection_reasons: The reasons for the rejection.
        """

        client_business_id: str
        status: AccountUpdate.PartnerClientCertificationInfoStatus
        rejection_reasons: AccountUpdate.PartnerClientCertificationInfoRejectionReasons

    class WabaInfo(TypedDict):
        """
        Information about the Whatsapp Business Account.

        Attributes:
            waba_id: The ID of the WABA.
            owner_business_id: The business ID of the owner.
            solution_id: The solution ID.
            solution_partner_business_ids: The business IDs of the solution partners.
            is_obo_to_shared_migrated: Whether the account is migrated.
        """

        waba_id: str
        owner_business_id: str | None
        solution_id: str | None
        solution_partner_business_ids: list[str] | None
        is_obo_to_shared_migrated: bool | None

    class AuthInternationalRateEligibility(TypedDict):
        """
        Information about the international rate eligibility.

        Attributes:
            start_time: The start time of the eligibility.
            exception_countries: The countries that are exceptions.
        """

        start_time: int
        exception_countries: list[AccountUpdate.ExceptionCountry] | None

    class ExceptionCountry(TypedDict):
        """
        Information about the exception country.

        Attributes:
            country_code: The country code.
            start_time: The start time of the exception.
        """

        country_code: str
        start_time: int

    class PartnerClientCertificationInfoStatus(utils.StrEnum):
        """
        The status of the certification.

        Attributes:
            PENDING: The certification is pending.
            APPROVED: The certification was approved.
            FAILED: The certification failed.
            REVOKED: The certification was revoked.
            UNKNOWN: The status is unknown.
        """

        PENDING = "PENDING"
        APPROVED = "APPROVED"
        FAILED = "FAILED"
        REVOKED = "REVOKED"
        UNKNOWN = "UNKNOWN"

        @classmethod
        def _missing_(
            cls, value: str
        ) -> AccountUpdate.PartnerClientCertificationInfoStatus:
            return cls.UNKNOWN

    class PartnerClientCertificationInfoRejectionReasons(utils.StrEnum):
        """
        The reasons for the rejection of the certification.

        Attributes:
            LEGAL_NAME_NOT_MATCHING: The legal name is not matching.
            WEBSITE_NOT_MATCHING: The website is not matching.
            NONE: There are no reasons for the rejection.
            BUSINESS_NOT_ELIGIBLE: The business is not eligible.
            LEGAL_NAME_NOT_FOUND_IN_DOCUMENTS: The legal name was not found in the documents.
            ADDRESS_NOT_MATCHING: The address is not matching.
            UNKNOWN: The reasons are unknown.
        """

        LEGAL_NAME_NOT_MATCHING = "LEGAL NAME NOT MATCHING"
        WEBSITE_NOT_MATCHING = "WEBSITE NOT MATCHING"
        NONE = "NONE"
        BUSINESS_NOT_ELIGIBLE = "BUSINESS NOT ELIGIBLE"
        LEGAL_NAME_NOT_FOUND_IN_DOCUMENTS = "LEGAL NAME NOT FOUND IN DOCUMENTS"
        ADDRESS_NOT_MATCHING = "ADDRESS NOT MATCHING"
        UNKNOWN = "UNKNOWN"

        @classmethod
        def _missing_(
            cls, value: str
        ) -> AccountUpdate.PartnerClientCertificationInfoRejectionReasons:
            return cls.UNKNOWNc
