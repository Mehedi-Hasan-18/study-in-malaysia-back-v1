from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.cloudinary_utils import delete_file, upload_file

from .authentication import FirebaseAuthentication, get_or_create_user_from_firebase, initialize_firebase
from firebase_admin import auth
from .permissions import IsFirebaseAuthenticated
from .serializers import MeSerializer, StudentProfileSerializer


class FirebaseLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return Response({"error": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST)

        initialize_firebase()
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            return Response({"error": "Invalid Firebase token."}, status=status.HTTP_401_UNAUTHORIZED)

        user = get_or_create_user_from_firebase(decoded_token)
        data = MeSerializer({"user": user, "profile": user.profile}).data
        return Response({"data": data})


class LogoutView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def post(self, request):
        return Response({"data": {"message": "Logged out. Drop Firebase token client-side."}})


class MeView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        data = MeSerializer({"user": request.user, "profile": request.user.profile}).data
        return Response({"data": data})


class ProfileView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFirebaseAuthenticated]

    def get(self, request):
        return Response({"data": StudentProfileSerializer(request.user.profile).data})

    def put(self, request):
        serializer = StudentProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data})


class ProfilePhotoView(APIView):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsFirebaseAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        photo = request.FILES.get("photo")
        if not photo:
            return Response({"error": "photo is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile = request.user.profile
        old_public_id = profile.photo_public_id
        result = upload_file(photo, f"profiles/{request.user.id}/photo/", resource_type="image")

        profile.photo_public_id = result["public_id"]
        profile.photo_url = result["secure_url"]
        profile.save(update_fields=["photo_public_id", "photo_url"])

        if old_public_id:
            delete_file(old_public_id, resource_type="image")

        return Response({"data": StudentProfileSerializer(profile).data})
