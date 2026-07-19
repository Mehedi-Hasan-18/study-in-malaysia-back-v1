from django.urls import path

from .views import DashboardView, ProfileCompletionView, RecentApplicationsView, StatisticsView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/recent-applications/", RecentApplicationsView.as_view(), name="dashboard-recent-applications"),
    path("dashboard/statistics/", StatisticsView.as_view(), name="dashboard-statistics"),
    path("dashboard/profile-completion/", ProfileCompletionView.as_view(), name="dashboard-profile-completion"),
]
