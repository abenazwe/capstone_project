from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Meter,  CustomUser, SensorData
from .serializers import *
from django.utils import timezone
from .permissions import  IsAdministrator, IsCustomer
from django.contrib.auth.tokens import default_token_generator
from .verificationemail_helpers import send_verification_email
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import identify_hasher, make_password
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import logging
import pickle
import joblib
import json
from django.views.decorators.csrf import csrf_exempt


# load the machine learning model 
model_f = "D:\Downloads\svm_model.pkl"
# Load the model from the file
with open(model_f, 'rb') as file:
    model_from_pickle = pickle.load(file)


#user views 
@api_view(['GET'])
def verify_email(request):
    """
    Verify users email address 
    """
    try:
        user_idb64 = request.query_params.get('uid')
        uid = force_str(urlsafe_base64_decode(user_idb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None:
        user.email_verified = True
        user.save()
        return render(request, 'verified.html')
       
    else:
        
        return render(request, 'failed_verfication.html') 
    
@api_view(['POST'])
def user_signup(request):
    """
    Register a new user
    """
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(email_verified=False)  # Set email_verified to False initially

            
         # Assign a meter only if the user is a Customer
            if user.role == 'Customer':
                available_meters = Meter.objects.filter(user__isnull=True).first()
                if available_meters:
                    available_meters.user = user
                    available_meters.save()
            # Generate a verification token for the user
            verification_token = default_token_generator.make_token(user)

            # Send the verification email
            send_verification_email(user, verification_token)

            return Response({'message': 'Sign up successful. Verification email sent.', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def signup_page (request):
    return render(request, "signup.html")

@csrf_exempt
@api_view(['POST'])
def user_login(request):
    """
    Login a user
    """
    if request.method == 'POST':
        email = request.data.get('email')
        password = request.data.get('password')

        # Debugging: Print email and password
        print(f"Login attempt - Email: {email}")

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            print("User does not exist")
            return Response({'error': 'User does not exist!!'}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure that the user has verified their email address
        if not user.email_verified:
            print("Email not verified")
            return Response({'error': 'Please verify your email address to login'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the password is already hashed
        if identify_hasher(user.password) is None:
            # Password is not hashed, hash it
            hashed_password = make_password('new_password')
            user.password = hashed_password
            user.save()

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            print(f"User role: {user.role}")  # Debugging line
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {
                'message': 'Login successful',
                'token': token.key, 
                'email': user.email, 
                'role': user.role,
                'name': user.name,
                'user_id': user.user_id 
            }

            if user.role == 'Administrator':
                response_data['redirect_url'] = 'admin_dashboard'
            else:
                response_data['redirect_url'] = 'user_page'

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print("Invalid credentials")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

def login_page(request):
    return render(request, "page.html")


@csrf_exempt
def user_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.meters.exists():
                meter = user.meters.first()
                print(f"Meter Location: {meter.location}")
                context = {"product_id": meter.product_id}
            else:
                context = {"error": "Meter not found"}
                print("Meter not found for user")
        except CustomUser.DoesNotExist:
            context = {"error": "User not found"}
            print("User not found")

        return render(request, "userpage.html", context)
    else:
        return render(request, "userpage.html")


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdministrator])
def view_users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdministrator |IsCustomer])
def edit_user(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'Customer':
        if user_id != request.user.user_id:
            return Response({"message": "You are not authorized to edit this user"}, status=status.HTTP_401_UNAUTHORIZED)
        #Customer cannot edit their role
        serializer = UpdateCustomerUserSerializer(user, data=request.data, partial=True)
    if request.user.role == 'Administrator':
        serializer = UpdateAdminUserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdministrator])
def delete_user(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"message": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


    
# meter views 
@api_view(['POST'])
#@permission_classes([IsAuthenticated,IsAdministrator])
def create_product(request):
    serializer = MeterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def add_meter(request):
    return render(request, 'add_meter.html')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdministrator])
def delete_product(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"message": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Meter.objects.get(pk=product_id)
    except Meter.DoesNotExist:
        return Response({"message": "ID not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
@api_view(['GET'])
#@permission_classes([IsAuthenticated,IsAdministrator])
def get_product(request):
    products = Meter.objects.all()
    serializer = MeterSerializer(products, many=True)
    return Response(serializer.data)

def dashboard (request):
    return render(request, "admin_dashboard.html")

#anyone can post to sensor data
@api_view(['POST'])
def sensor_data(request):
    serializer = SensorDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  #this is for the view details page. after you press the view details it sends you to the specific product id by url
def sensor_data_(request,product_id):
    print("product id", product_id)
    return render(request, 'viewdetails.html', {'product_id': product_id})
  
#this gets specific details on the view details page
@api_view(['GET'])
def sensor_data_details(request, product_id):
    try:
        latest_sensor_data = SensorData.objects.filter(product_id=product_id).order_by('-timestamp').first()
        if latest_sensor_data:
            # Retrieve the user_id from the related Meter model
            user_id = latest_sensor_data.product_id.user.user_id  # Assuming Meter has a foreign key to CustomUser

            # Serialize the sensor data and include the user_id
            serializer = SensorDataSerializer(latest_sensor_data)
            data = serializer.data
            data['user_id'] = user_id

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No data found for this product ID"}, status=status.HTTP_404_NOT_FOUND)
    except SensorData.DoesNotExist:
        return Response({"error": "No data found for this product ID"}, status=status.HTTP_404_NOT_FOUND)

def sensor_data_detail_page(request, product_id):
    return render(request, 'viewdetails.html', {'product_id':product_id})

@api_view(['GET'])
def most_recent_sensor_data(request, user_id):
    try:
        user = CustomUser.objects.get(pk=user_id)
        meter = user.meters.first()
        if meter:
            recent_sensor_data = SensorData.objects.filter(product_id=meter.product_id).order_by('-timestamp').first()
            if recent_sensor_data:
                serializer = SensorDataSerializer(recent_sensor_data)
                return Response(serializer.data)
            else:
                return Response({'error': 'No sensor data found for the assigned meter'}, status=404)
        else:
            return Response({'error': 'No meter assigned to the user'}, status=404)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

#to add a meter 
@csrf_exempt
@api_view(['POST'])
def add_meter(request): 
    name = request.data.get('name')
    location = request.data.get('location')
    if not name or not location:
        return Response({'error': 'Name and location are required'}, status=status.HTTP_400_BAD_REQUEST)
    meter = Meter.objects.create(name=name, location=location)
    serializer = MeterSerializer(meter)
    return Response({'message': 'Meter added successfully'}, status=status.HTTP_201_CREATED)

def add_meter_p(request):
    return render(request, "add_meter.html")

@api_view(['POST'])
def data_post(request):
    """
    Handle data posted from the ESP32
    """
    try:
        product_id = request.data.get('product_id')
        voltage = request.data.get('voltage')
        current = request.data.get('current')
        power = request.data.get('power')
        energy = request.data.get('energy')
        kVA = request.data.get('kVA')
        power_factor = request.data.get('power_factor')
        billing = request.data.get('billing')

        # Check for missing fields
        if not all([product_id, voltage, current, power, energy, kVA, power_factor, billing]):
            return Response({'success': False, 'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        meter = Meter.objects.get(pk=product_id)
      
        sensor_data= SensorData.objects.create(
            product_id=meter,
            voltage=voltage,
            current=current,
            power=power,
            energy=energy,
            kVA=kVA,
            power_factor=power_factor,
            billing=billing,
        )
       
         # Check for anomalies in the new data
        features = [[voltage, current, power, energy, kVA, power_factor, billing]]
        prediction = model_from_pickle.predict(features)[0]
        anomaly_detected = prediction == 1
     
        if anomaly_detected and not sensor_data.alert_sent:
            send_anomaly_email(meter.user, product_id)
            sensor_data.alert_sent = True
            sensor_data.save()
            
            
        return Response({'success': True, 'message': 'Data saved successfully'}, status=status.HTTP_201_CREATED)

    except Meter.DoesNotExist:
        return Response({'success': False, 'message': 'Meter not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_anomalies(request, user_id):
    """
    Endpoint to check if there are any anomalies in the meter assigned to a particular user
    """
    try:
        user = CustomUser.objects.get(user_id=user_id)
        meters = Meter.objects.filter(user=user)
        
        if not meters.exists():
            return Response({'message': 'No meters found for this user'}, status=status.HTTP_404_NOT_FOUND)
        
        latest_readings = []
        for meter in meters:
            try:
                latest_reading = SensorData.objects.filter(product_id=meter).latest('timestamp')
                latest_readings.append(latest_reading)
            except SensorData.DoesNotExist:
                continue

        if not latest_readings:
            return Response({'message': 'No sensor readings found for the user\'s meters'}, status=status.HTTP_404_NOT_FOUND)
        
        anomaly_detected = True
        for latest_reading in latest_readings:
            if not latest_reading.alert_sent:
                features = [[
                    latest_reading.voltage, 
                    latest_reading.current, 
                    latest_reading.power, 
                    latest_reading.energy, 
                    latest_reading.kVA, 
                    latest_reading.power_factor, 
                    latest_reading.billing
                ]]
                prediction = model_from_pickle.predict(features)[0]
                anomaly_detected = prediction == 1
                

                if anomaly_detected:
                    send_anomaly_email(user, latest_reading.product_id.pk)
                    latest_reading.alert_sent = True
                    latest_reading.save()
                    break  

        data = {
            'anomaly_detected': anomaly_detected,
            'timestamp': latest_reading.timestamp if latest_reading else None
        }

        return Response(data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_anomaly_email(user, product_id):
    
    # Email to the customer
    customer_subject = 'Alert: False Data Injection Detected'
    customer_message = (
        'A Potential False Data Injection Attack Has Been Detected On Your Smart Meter. '
        'Please visit the application to check the details and contact the admin if needed.'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    customer_recipient = [user.email]

    send_mail(
        customer_subject,
        customer_message,
        from_email,
        customer_recipient,
        fail_silently=False
    )
    logging.debug("Customer email sent successfully")
    # Email to the admin
    admin_subject = 'Admin Alert: False Data Injection Detected'
    admin_message = (
        f'A False Data Injection Attack Has Been Detected On a Smart Meter with Product ID: {product_id}. '
        'Please check the database and take necessary actions.'
    )
    admin_recipient = ['ezwennes1@gmail.com']

    send_mail(
        admin_subject,
        admin_message,
        from_email,
        admin_recipient,
        fail_silently=False
    )
    logging.debug("Admin email sent successfully")
