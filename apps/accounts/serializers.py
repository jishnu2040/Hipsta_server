from rest_framework import serializers
from .models import User


# RegistrationSerializer
class UserRegisterSerializer(serializers.ModelSerializer):
    
    password=serializers.CharField(max_length =68, min_length =6, write_only =True)# write_only= True, because password no need to deserialize
    password2=serializers.CharField(max_length =68, min_length =6, write_only =True)# write_only= True, because password no need to deserialize
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, write_only=True)
    # the above line need to reviewed
    class Meta:
        model=User
        fields= ['email', 'first_name', 'last_name', 'password', 'password2','user_type']


    def validate(self, attrs):
        password = attrs.get('password', '')
        password2= attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")

        common_passwords = ["password", "123456", "12345678", "1234", "qwerty", "123456", "dragon", "pussy", "baseball", "football"]

        if password.lower() in common_passwords:
            raise serializers.ValidationError("Password is too common")
        return attrs


    def create(self, validated_data):
        user_type = validated_data.pop('user_type', 'customer')
        user=User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            user_type=user_type
        )
        
        return user
    
# VerifySerializer
class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField()
    