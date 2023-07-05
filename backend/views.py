from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Database, Contact, Company, Project, Property
from .serializers import DatabaseSerializer, ContactSerializer, CompanySerializer,  PropertySerializer, ProjectSerializer, UserSerializer
from datetime import date
from rest_framework.decorators import action

@login_required
def Index(request):
    print(request.user)
    
    print(Database.objects.filter(creator=request.user)[0])

    return render(request, "index.html", {})

@login_required
def contact(request,id):
    
    return render(request, "contact.html", {})
@login_required
def company(request,id):
    
    return render(request, "company.html", {})
@login_required
def property(request,id):
    
    return render(request, "property.html", {})
@login_required
def project(request,id):

    return render(request, "project.html", {})

def signin(request):
    
    if request.user.is_active:
        return redirect("index")
        
    return render(request, "signin.html", {})


class IndexView(APIView):
    def get(self, request):

        print("Index Page", request.user.id)

        if not self.request.user.is_superuser:
            user = self.request.user

            result = {"Creator": [], "Editors": []}

            creator_db = Database.objects.filter(creator=user)
            editors_db = Database.objects.filter(editors=user)

            queryset = creator_db.union(editors_db)

            data_list = [{"username": user.username,},]
            for db in queryset:
                
                title = db.database_title
                db_id = db.id
                role = ""

                if db.creator == user:
                    role = "Creator"
                elif user in db.editors.all():
                    role = "Editor"

                data = {

                    "title": title,
                    "id": db_id,
                    "role": role
                }
                data_list.append(data)

            return Response(data_list)
        else:
            user = self.request.user
            queryset = Database.objects.all()

            
            data_list = [{"username": user.username,},]
            for db in queryset:
            
                
                title = db.database_title
                db_id = db.id
                creator_db = db.creator.username         

                data = {
                    
                    "title": title,
                    "id": db_id,
                    "creator": creator_db
                }

                data_list.append(data)

            return Response(data_list)

class IndexDatabase(viewsets.ModelViewSet):

    serializer_class = DatabaseSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            user = self.request.user

            result = {"Creator": [], "Editors": []}

            creator_db = Database.objects.filter(creator=user)
            editors_db = Database.objects.filter(editors=user)

            queryset = creator_db.union(editors_db)

            # Create a list of dictionaries containing the required data
            data_list = []
            for db in queryset:
                # Retrieve the username, database title, ID, and role
                username = user.username
                title = db.title
                db_id = db.id
                role = ""
                if db.creator == user:
                    role = "Creator"
                elif user in db.editors.all():
                    role = "Editor"

                # Create a dictionary for each database entry
                data = {
                    "username": username,
                    "title": title,
                    "id": db_id,
                    "role": role
                }
                data_list.append(data)

            return data_list
        else:

            user = self.request.user

            queryset = Database.objects.all()

            
            # data_list = []
            # for db in queryset:
            
                
            #     title = db.database_title
            #     db_id = db.id
            #     creator_db = db.creator             

            #     data = {
                    
            #         "title": title,
            #         "id": db_id,
            #         "creator": creator_db
            #     }

            #     data_list.append(data)

            return queryset
        # If the user is a superuser, return an empty queryset
        return Database.objects.none()

# class ContactView(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ContactSerializer

#     def get_queryset(self):
#         queryset = Contact.objects.all()
        
#         if not self.request.user.is_superuser:
#             db_id = self.kwargs.get('id')
#             db = Database.objects.filter(id=db_id, creator=self.request.user)

#             queryset = queryset.filter(database__in=db)
            
#         else:

#             db_id = self.kwargs.get('id')
#             queryset = queryset.filter(database__in=db_id)

#         return queryset

class ContactListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    
    def get(self, request, *args, **kwargs):
        
        if not self.request.user.is_superuser:
            
            db_id = self.kwargs.get("db")
            db = Database.objects.filter(id=db_id, creator = request.user)
            queryset = self.queryset.filter(database__in=[db])
            
        else:
            print("superuserentered")
            db_id = self.kwargs.get("db")
            queryset = self.queryset.filter(database__in=[db_id])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ContactCreateApi(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):

        db_id = self.kwargs.get("db")
        request.data["database"] = db_id

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ContactDeleteApi(generics.DestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if not (instance.database.creator == request.user or instance.database.editor == request.user):
            return Response({'message': 'Permission denied. User role is not permitted to delete the item'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)

        response_data = {
            'message': 'Item deleted successfully',
            'deleted_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class ContactUpdateApi(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def update(self, request, *args, **kwargs):
        print(request.user)

        instance = self.get_object()
        database = instance.database
        print(database)

        if not (database.creator == request.user or database.editor == request.user):
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'message': 'Item updated successfully',
            'updated_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CompanyListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    
    def get(self, request, *args, **kwargs):
        
        if not self.request.user.is_superuser:
            
            db_id = self.kwargs.get("db")
            db = Database.objects.filter(id=db_id, creator = request.user)
            queryset = self.queryset.filter(database__in=[db])
            
        else:
            print("superuserentered")
            db_id = self.kwargs.get("db")
            queryset = self.queryset.filter(database__in=[db_id])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CompanyCreateApi(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer

    def create(self, request, *args, **kwargs):

        db_id = self.kwargs.get("db")
        request.data["database"] = db_id

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CompanyDeleteApi(generics.DestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if not (instance.database.creator == request.user or instance.database.editor == request.user):
            return Response({'message': 'Permission denied. User role is not permitted to delete the item'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)

        response_data = {
            'message': 'Item deleted successfully',
            'deleted_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class CompanyUpdateApi(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def update(self, request, *args, **kwargs):
        print(request.user)

        instance = self.get_object()
        database = instance.database
        print(database)

        if not (database.creator == request.user or database.editor == request.user):
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'message': 'Item updated successfully',
            'updated_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PropertyListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
    
    def get(self, request, *args, **kwargs):
        
        if not self.request.user.is_superuser:
            
            db_id = self.kwargs.get("db")
            db = Database.objects.filter(id=db_id, creator = request.user)
            queryset = self.queryset.filter(database__in=[db])
            
        else:
            print("superuserentered")
            db_id = self.kwargs.get("db")
            queryset = self.queryset.filter(database__in=[db_id])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class PropertyCreateApi(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = PropertySerializer

    def create(self, request, *args, **kwargs):

        db_id = self.kwargs.get("db")
        request.data["database"] = db_id

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PropertyDeleteApi(generics.DestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if not (instance.database.creator == request.user or instance.database.editor == request.user):
            return Response({'message': 'Permission denied. User role is not permitted to delete the item'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)

        response_data = {
            'message': 'Item deleted successfully',
            'deleted_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class PropertyUpdateApi(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

    def update(self, request, *args, **kwargs):
        print(request.user)

        instance = self.get_object()
        database = instance.database
        print(database)

        if not (database.creator == request.user or database.editor == request.user):
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'message': 'Item updated successfully',
            'updated_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProjectListApi(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    
    def get(self, request, *args, **kwargs):
        
        if not self.request.user.is_superuser:
            
            db_id = self.kwargs.get("db")
            db = Database.objects.filter(id=db_id, creator = request.user)
            queryset = self.queryset.filter(database__in=[db])
            
        else:
            print("superuserentered")
            db_id = self.kwargs.get("db")
            queryset = self.queryset.filter(database__in=[db_id])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ProjectCreateApi(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):

        db_id = self.kwargs.get("db")
        request.data["database"] = db_id

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectDeleteApi(generics.DestroyAPIView):
    
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()

        if not (instance.database.creator == request.user or instance.database.editor == request.user):
            return Response({'message': 'Permission denied. User role is not permitted to delete the item'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)

        response_data = {
            'message': 'Item deleted successfully',
            'deleted_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

class ProjectUpdateApi(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def update(self, request, *args, **kwargs):
        print(request.user)

        instance = self.get_object()
        database = instance.database
        print(database)

        if not (database.creator == request.user or database.editor == request.user):
            return Response({'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_data = {
            'message': 'Item updated successfully',
            'updated_item_id': instance.id
        }

        return Response(response_data, status=status.HTTP_200_OK)



class SigninView(APIView):
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        print("Signin Page: ",user)

        if user is not None:

            login(request, user)
            return Response({'message': 'Signed in successfully'},status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)

class SignoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({},status=status.HTTP_200_OK)
    
class CreateUserView(APIView):
    def post(self, request):
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save()

            username = user_serializer.validated_data['username']
            password = user_serializer.validated_data['password']
            user.set_password(password)  # Set the password and hash it
            user.save()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                return redirect(reverse('createdb'))
                # token, _ = Token.objects.get_or_create(user=user)
                # return Response({'token': token.key}, status=status.HTTP_201_CREATED)

            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        else:
            errors = {}
            errors.update(user_serializer.errors)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
class CreateDatabaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['creator'] = request.user.id

        database_serializer = DatabaseSerializer(data=data)

        if database_serializer.is_valid():
            database = database_serializer.save()

            return redirect(reverse('index'))
        else:
            errors = {}
            errors.update(database_serializer.errors)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)