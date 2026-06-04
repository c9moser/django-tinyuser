from enum import StrEnum
from django.utils.translation import gettext_noop as _, gettext_lazy, gettext


class FriendshipStatus(StrEnum):
    """Enumeration for representing the status of a friendship."""
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    @staticmethod
    def from_string(status_str):
        """Convert a string to a FriendshipStatus enum member.

        :param status_str: The string representation of the friendship status.
        :type status_str: str
        :return: The corresponding FriendshipStatus enum member.
        :rtype: FriendshipStatus
        :raises ValueError: If the input string does not correspond to any valid status.
        """
        mapping = {
            'pending': FriendshipStatus.PENDING,
            'accepted': FriendshipStatus.ACCEPTED,
            'rejected': FriendshipStatus.REJECTED,
        }
        try:
            return mapping[status_str.lower()]
        except KeyError:
            raise ValueError(f"Invalid friendship status: '{status_str}'. Valid options are: {', '.join(mapping.keys())}.")  # noqa: E501

    @property
    def name_raw(self) -> str:
        """
        Return the raw name of the enum member.

        :return: The raw name of the enum member.
        :rtype: str
        """
        mapping = {
            self.PENDING: _('pending'),
            self.ACCEPTED: _('accepted'),
            self.REJECTED: _('rejected'),
        }
        return mapping.get(self.value, self.value)

    @property
    def name_lazy(self) -> str:
        """
        Return the lazy translation of the enum member's name.

        :return: The lazy translation of the enum member's name.
        :rtype: str
        """
        return gettext_lazy(self.name_raw())

    @property
    def name(self) -> str:
        """
        Return the translated name of the enum member.

        :return: The translated name of the enum member.
        :rtype: str
        """
        return gettext(self.name_raw())

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.value.upper()}>"


class FriendshipBlockedStatus(StrEnum):
    """Enumeration for representing the blocked status of a friendship."""
    NOT_BLOCKED = 'not_blocked'
    BLOCKED_BY_USER1 = 'blocked_by_user1'
    BLOCKED_BY_USER2 = 'blocked_by_user2'
    BLOCKED_BY_BOTH = 'blocked_by_both'

    @staticmethod
    def from_string(status_str):
        """Convert a string to a FriendshipBlockedStatus enum member.

        :param status_str: The string representation of the blocked status.
        :type status_str: str
        :return: The corresponding FriendshipBlockedStatus enum member.
        :rtype: FriendshipBlockedStatus
        :raises ValueError: If the input string does not correspond to any valid blocked status.
        """
        mapping = {
            'not_blocked': FriendshipBlockedStatus.NOT_BLOCKED,
            'blocked_by_user1': FriendshipBlockedStatus.BLOCKED_BY_USER1,
            'blocked_by_user2': FriendshipBlockedStatus.BLOCKED_BY_USER2,
            'blocked_by_both': FriendshipBlockedStatus.BLOCKED_BY_BOTH,
        }
        try:
            return mapping[status_str.lower()]
        except KeyError:
            raise ValueError(f"Invalid friendship blocked status: '{status_str}'. Valid options are: {', '.join(mapping.keys())}.")  # noqa: E501

    @property
    def name_raw(self) -> str:
        """
        Return the raw name of the enum member.

        :return: The raw name of the enum member.
        :rtype: str
        """
        mapping = {
            self.NOT_BLOCKED: _('not blocked'),
            self.BLOCKED_BY_USER1: _('blocked by user1'),
            self.BLOCKED_BY_USER2: _('blocked by user2'),
            self.BLOCKED_BY_BOTH: _('blocked by both users'),
        }
        return mapping.get(self.value, self.value)

    @property
    def name_lazy(self) -> str:
        """
        Return the lazy translation of the enum member's name.

        :return: The lazy translation of the enum member's name.
        :rtype: str
        """
        return gettext_lazy(self.name_raw())

    @property
    def name(self) -> str:
        """
        Return the translated name of the enum member.

        :return: The translated name of the enum member.
        :rtype: str
        """
        return gettext(self.name_raw())

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self.value.upper()}>"
