from rest_framework import serializers

from .models import User

class AuthSerializer(serializers.Serializer):

    code = serializers.IntegerField(min_value=1000, max_value=9999, write_only=True)
    phone = serializers.CharField(min_length=11, max_length=13)

    def create(self, validated_data):
        return User.objects.auth_user(validated_data["phone"])

class ProfileSerializer(serializers.Serializer):

    activated = serializers.CharField(read_only=True)
    referral_code = serializers.CharField(min_length=6, max_length=6, read_only=True)
    referrals = serializers.ListSerializer(child=serializers.CharField(min_length=11, max_length=13), read_only=True)

    def create(self, validated_data):
        phoneNumber = self.context.get("phoneNumber")

        if self.context.get("method") == "GET":
            data = User.objects.is_activated(phoneNumber)
            data["referrals"] = data["referrals"].split(", ")
            return data
        else:
            ref_code = self.context.get("ref_code")
            return User.objects.activate_referral(ref_code, phoneNumber)