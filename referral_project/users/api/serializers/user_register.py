from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    referrer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'referrer','first_name', 'last_name', 'username',
            'email', 'password', 'password_confirm'
        ]

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError(
                {'password_confirm': 'Those passwords don\'t match.'}
            )
        return super(UserRegisterSerializer, self).validate(data)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
