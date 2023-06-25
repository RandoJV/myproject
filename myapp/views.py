
from datetime import datetime
from django.http import Http404
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from .models import Person
from .serializers import PersonSerializer, TrackSerializer
from .models import Album, Track
from .serializers import AlbumSerializer
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse


def index(request):
    now = datetime.now()
    html = f'''
    <html>
        <body>
            <h1>Hello from Vercel!</h1>
            <p>The current time is { now }.</p>
        </body>
    </html>
    '''
    return HttpResponse(html)

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Album):
            return self.check_album_permission(request, obj)
        elif isinstance(obj, Track):
            return self.check_track_permission(request, obj)

        return False

    def check_album_permission(self, request, album):
        if album.author is None or album.author == request.user:
            return True
        return False

    def check_track_permission(self, request, track):
        if track.album.author is None or track.album.author == request.user:
            return True
        return False

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        elif request.method == 'POST' and request.user.is_authenticated:
            return True
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            if view.kwargs.get('track_pk'):
                # If it's a track, the permission will be checked in has_object_permission
                return True
            else:
                return request.user.is_authenticated
        return False
    


class MyAPIView(APIView):
    permission_classes =(permissions.IsAuthenticated, IsAuthorOrReadOnly)
    def get(self, request, pk=None):
        if pk is not None:
            # Logic to handle GET request with a specific pk
            try:
                person = Person.objects.get(pk=pk)
            except Person.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            serializer = PersonSerializer(person)
            return Response(serializer.data)
        
        else:
            # Logic to handle GET request without a pk
            persons = Person.objects.all()
            serializer = PersonSerializer(persons, many=True)
            return Response(serializer.data)

    
    def post(self, request):
        # Create a new person based on the request data
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def put(self, request, pk):
        # Get the person object to be updated

        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if not IsAuthorOrReadOnly().has_object_permission(request, self, person):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Update the person object with the new data
        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Get the person object to be deleted
        try:
            person = Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        if not IsAuthorOrReadOnly().has_object_permission(request, self, person):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Delete the person object
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlbumView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    def get_object(self, pk):
        try:
            return Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            raise Http404
    def get(self, request, pk=None, format=None):
        if pk is not None:
            # Retrieve a single album
            try:
                album = Album.objects.get(pk=pk)
                serializer = AlbumSerializer(album)
                return Response(serializer.data)
            except Album.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve multiple albums
            albums = Album.objects.all()
            serializer = AlbumSerializer(albums, many=True)
            return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        album = self.get_object(pk)
        if not IsAuthorOrReadOnly().has_object_permission(request, self, album):
            return Response({"message": "Data bukan milik Anda"}, status=status.HTTP_403_FORBIDDEN)
        serializer = AlbumSerializer(album, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, pk, format=None):
        album = self.get_object(pk)
        if not IsAuthorOrReadOnly().has_object_permission(request, self, album):
            return Response({"message": "Data bukan milik Anda"}, status=status.HTTP_403_FORBIDDEN)

        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TrackView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_album(self, album_pk):
        try:
            return Album.objects.get(pk=album_pk)
        except Album.DoesNotExist:
            raise Http404

    def get_track(self, album, track_pk):
        try:
            return album.tracks.get(pk=track_pk)
        except Track.DoesNotExist:
            raise Http404

    def get(self, request, album_pk, track_pk, format=None):
        album = self.get_album(album_pk)
        track = self.get_track(album, track_pk)
        serializer = TrackSerializer(track)
        return Response(serializer.data)

    def post(self, request, album_pk, track_pk, format=None):
        album = self.get_album(album_pk)
        serializer = TrackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(album=album)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, album_pk, track_pk, format=None):
        album = self.get_album(album_pk)
        track = self.get_track(album, track_pk)
        if not IsAuthorOrReadOnly().has_object_permission(request, self, track):
            return Response({"message": "Data bukan milik Anda"}, status=status.HTTP_403_FORBIDDEN)
        serializer = TrackSerializer(track, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    def delete(self, request, album_pk, track_pk, format=None):
        album = self.get_album(album_pk)
        track = self.get_track(album, track_pk)
        if not IsAuthorOrReadOnly().has_object_permission(request, self, track):
            return Response({"message": "Data bukan milik Anda"}, status=status.HTTP_403_FORBIDDEN)
        track.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_track(self, album, track_pk):
        try:
            return album.tracks.get(pk=track_pk)
        except Track.DoesNotExist:
            raise Http404
        
    def check_object_permissions(self, user, obj):
        # Allow if the user is the author of the track or the track has no author assigned
        if obj.author is None or obj.author == user:
            return True
        return False