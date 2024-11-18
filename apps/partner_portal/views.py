from rest_framework import generics, status
from .models import  PartnerDetail
from .serializers import PartnerDetailSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib import redirects
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import generate_presigned_url


class GetPresignedURL(APIView):
    def post(self, request):
        # Extract file name and file type from the request data
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type')

        # Check if file name is provided
        if not file_name:
            return Response({'error': 'file name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate pre-signed URL and file key
        presigned_url, file_key = generate_presigned_url(file_name, file_type)

        if presigned_url:
            # Return both the pre-signed URL and file key
            return Response({'url': presigned_url, 'file_key': file_key})
        else:
            return Response({'error': 'could not generate presigned URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# partner create view 
class PartnerCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PartnerDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Return more detailed error messages
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
