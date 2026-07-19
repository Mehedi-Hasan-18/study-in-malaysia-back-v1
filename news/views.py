from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Blog, FAQ, Inquiry, News
from .serializers import BlogSerializer, FAQSerializer, InquirySerializer, NewsSerializer


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    search_fields = ["title", "body"]
    ordering_fields = ["published_at", "title"]


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    search_fields = ["title", "body", "author", "tags"]
    ordering_fields = ["published_at", "title"]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filterset_fields = ["category"]
    search_fields = ["question", "answer", "category"]
    ordering_fields = ["display_order", "id"]


class InquiryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer


class ContactView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data": serializer.data}, status=201)
