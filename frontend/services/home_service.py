from datetime import date

from frontend.api.home_api import HomeApi
from frontend.models.home import (
    HomeAdminResponse,
    HomeAdminKpis,
    HomeAdminModuleCount,
    HomeAdminTrendPoint,
    HomeAdminTopUser,
    HomeAdminModuleCompliance,
    HomeAdminAlert,
    HomeAdminInsight,
    HomeUserResponse,
    HomeUserKpis,
    HomeUserModuleCount,
    HomeUserTrendPoint,
    HomeUserPendiente,
    HomeUserAlert,
    HomeUserInsight,
)


class HomeFrontendService:

    def __init__(self, token: str | None = None):
        self.api = HomeApi(token=token)

    def get_admin_summary(
        self,
        start_date: date,
        end_date: date,
        filter_user: str | None = None,
    ) -> HomeAdminResponse:
        response = self.api.get_admin_summary(start_date, end_date, filter_user)
        return HomeAdminResponse(
            kpis=HomeAdminKpis(**response.get("kpis", {})),
            modules=HomeAdminModuleCount(**response.get("modules", {})),
            trend=[HomeAdminTrendPoint(**t) for t in response.get("trend", [])],
            top_users=[HomeAdminTopUser(**u) for u in response.get("top_users", [])],
            module_compliance=[
                HomeAdminModuleCompliance(**m) for m in response.get("module_compliance", [])
            ],
            alerts=[HomeAdminAlert(**a) for a in response.get("alerts", [])],
            insights=[HomeAdminInsight(**i) for i in response.get("insights", [])],
        )

    def get_user_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> HomeUserResponse:
        response = self.api.get_user_summary(start_date, end_date)
        return HomeUserResponse(
            kpis=HomeUserKpis(**response.get("kpis", {})),
            modules=HomeUserModuleCount(**response.get("modules", {})),
            trend=[HomeUserTrendPoint(**t) for t in response.get("trend", [])],
            pendientes=[HomeUserPendiente(**p) for p in response.get("pendientes", [])],
            alerts=[HomeUserAlert(**a) for a in response.get("alerts", [])],
            insights=[HomeUserInsight(**i) for i in response.get("insights", [])],
        )
