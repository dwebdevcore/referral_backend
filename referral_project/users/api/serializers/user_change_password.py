from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'new_password_confirm']

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError('Wrong old password.')
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        new_password_confirm = data.pop('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError(
                {'new_password_confirm': 'Those passwords don\'t match.'}
            )
        return super(UserChangePasswordSerializer, self).validate(data)

    def update(self, instance, validated_data):
        user = instance
        user.set_password(validated_data.get('new_password'))
        user.save()
        return user
