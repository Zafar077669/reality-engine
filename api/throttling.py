# api/throttling.py

from rest_framework.throttling import (
    AnonRateThrottle,
    ScopedRateThrottle,
    UserRateThrottle,
)


class BurstAnonThrottle(AnonRateThrottle):
    scope = "burst_anon"


class SustainedAnonThrottle(AnonRateThrottle):
    scope = "sustained_anon"



class BurstUserThrottle(UserRateThrottle):
    scope = "burst_user"

class SustainedUserThrottle(ScopedRateThrottle):
    scope = "sustained_user"


class AuthRateThrottle(ScopedRateThrottle):
    scope = "auth"