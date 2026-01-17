from confluent_kafka import Consumer,KafkaError,KafkaException
import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import random
from myapp.utility.JWT_for_users import UserTokenGeneration
from  django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken

class Command(BaseCommand):
    help = "Kafka Consumer for authentication messages"

    def handle(self, *args, **options):
        config = {
            "bootstrap.servers": "kafka:9092",
            "group.id": "auth_group",
            "auto.offset.reset": "earliest"
        }

        consumer = Consumer(config)
        consumer.subscribe(['auth_topic'])
        self.stdout.write(self.style.SUCCESS("Kafka Consumer started and listening to 'auth_topic'"))

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Kafka error: {msg.error()}")
                        continue
                try:
                    payload = json.loads(msg.value().decode('utf-8'))
                except:
                    self.stdout.write(self.style.ERROR("Failed to decode Kafka message"))


                event_type = payload.get('event_type')
                data = payload.get('data', {})
                fullName = data.get('fullName')
                email = data.get('email')
                phone = data.get('phone')
                password = data.get('password')

                if msg.topic() == 'auth_topic':
                    if event_type == 'email_verification':
                        self.create_user_model(fullName,email,phone,password)
                        self.stdout.write(self.style.SUCCESS(f"Processed email verification for {email}"))



        except KafkaException as e:
            self.stdout.write(self.style.ERROR(f"Kafka Exception: {str(e)}"))

        except KeyboardInterrupt as e:
            self.stdout.write(self.style.WARNING("Kafka Consumer stopped"))
            consumer.close()
            pass


    

    def create_user_model(self, fullName, email, phone, password):
         User = get_user_model()

         if User.objects.filter(email=email).exists():
             self.stdout.write(
                 self.style.WARNING(f"User with email {email} already exists")
             )
             return
     
         user = User.objects.create_user(
             email=email,
             fullName=fullName,
             phone=phone,
             password=password,
         )
     
         username = email.split('@')[0]
         user.username = f"{username}{random.randint(1000,9999)}"
         user.is_active = True
         user.save()  
     
         
         refresh_token = RefreshToken.for_user(user)
         access_token = refresh_token.access_token
     
         
         cache.set(f'access_token_{user.email}', str(access_token), 300)
         cache.set(f'refresh_token_{user.email}', str(refresh_token), 300)
     
         self.stdout.write(
             self.style.SUCCESS(f"User {user.email} created successfully token {str(access_token)} and the refresh token {str(refresh_token)}")

         )





