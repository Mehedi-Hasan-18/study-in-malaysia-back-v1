from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    base = request.build_absolute_uri("/api/v1/")
    endpoints = {
        "auth": {
            "firebase_login": f"{base}auth/firebase-login/",
            "logout": f"{base}auth/logout/",
            "me": f"{base}auth/me/",
        },
        "profile": {
            "detail": f"{base}profile/",
            "photo": f"{base}profile/photo/",
        },
        "locations": {
            "countries": f"{base}countries/",
            "states": f"{base}states/",
            "cities": f"{base}cities/",
        },
        "catalog": {
            "universities": f"{base}universities/",
            "faculties": f"{base}faculties/",
            "programs": f"{base}programs/",
            "intakes": f"{base}intakes/",
            "fees": f"{base}fees/",
            "scholarships": f"{base}scholarships/",
        },
        "student": {
            "applications": f"{base}applications/",
            "documents": f"{base}documents/",
            "my_scholarships": f"{base}my-scholarships/",
            "wishlist_universities": f"{base}wishlist/universities/",
            "wishlist_scholarships": f"{base}wishlist/scholarships/",
            "dashboard": f"{base}dashboard/",
            "notifications": f"{base}notifications/",
        },
        "content": {
            "news": f"{base}news/",
            "blogs": f"{base}blogs/",
            "faq": f"{base}faq/",
            "contact": f"{base}contact/",
            "inquiry": f"{base}inquiry/",
        },
    }
    return Response({"data": endpoints})
