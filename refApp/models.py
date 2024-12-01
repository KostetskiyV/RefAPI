from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.db import models
from django.conf import settings

from rest_framework import serializers

class ReferralCode:

    CODE_SYMBS = "qwertyuiopasdfghjklzxcvbnm1234567890"
    SYMBS_COUNT = 36

    def checkRefCode(self, refCode):
        return len(User.objects.filter(refcode=refCode)) == 1

    def createRefCode(self):

        from random import randint

        while True:
            refCode = ""
            for i in range(6):
                refCode += self.CODE_SYMBS[randint(0, self.SYMBS_COUNT-1)]

            if not self.checkRefCode(refCode):
                return refCode

class UserManager(BaseUserManager):

    def create_user(self, phoneNumber, password=None):
        if phoneNumber is None:
            raise serializers.ValidationError('Users must have a phone number.')

        phoneNumber = str(phoneNumber)
        if 11 > len(phoneNumber) or len(phoneNumber) > 13 or not phoneNumber.isdigit():
            raise serializers.ValidationError('Phone number must be 11-13 symbols in len and contain only digits.')

        phoneNumber = int(phoneNumber)
        user = self.model(phoneNumber=phoneNumber, refcode=ReferralCode().createRefCode())
        user.set_unusable_password()
        user.save()

        return user

    def create_superuser(self, phoneNumber, password):

        user = self.create_user(phoneNumber)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

    def auth_user(self, phoneNumber):
        user = User.objects.filter(phoneNumber=phoneNumber)
        if len(user) == 0:
            self.create_user(phoneNumber)
        return {"phone": phoneNumber}

    def is_activated(self, phoneNumber):

        if phoneNumber is None or not(11 <= len(phoneNumber) <= 13):
            raise serializers.ValidationError("Incorrect phone number")

        user = User.objects.filter(phoneNumber=phoneNumber)
        if len(user) == 0:
            raise serializers.ValidationError("Incorrect phone number")

        return {"activated": user[0].activated, "referral_code": user[0].refcode, "referrals": user[0].referrals}

    def activate_referral(self, ref_code, phoneNumber):

        if ref_code is None or len(ref_code) != 6:
            raise serializers.ValidationError("You mast enter a referral code in len of 6 symbols")

        if phoneNumber is None or not(11 <= len(phoneNumber) <= 13):
            raise serializers.ValidationError("Incorrect phone number")

        user = User.objects.filter(phoneNumber=phoneNumber)
        if len(user) == 0:
            raise serializers.ValidationError("Incorrect phone number")
        if user[0].activated != "False":
            raise serializers.ValidationError("Specified user is already activated")
        if user[0].refcode == ref_code:
            raise serializers.ValidationError("You can`t use your referral code on yourself")
        inviter = User.objects.filter(refcode=ref_code)
        if len(inviter) == 0:
            raise serializers.ValidationError("Non-existent referral code")

        if inviter[0].referrals == "":
            inviter[0].referrals = phoneNumber
        else:
            inviter[0].referrals += f", {phoneNumber}"
        inviter[0].save()
        user[0].activated = ref_code
        user[0].save()
        return {"activated": ref_code}

class User(AbstractBaseUser, PermissionsMixin):
    phoneNumber = models.BigIntegerField(db_index=True, validators=[MinValueValidator(10000000000), MaxValueValidator(9999999999999)], unique=True)

    refcode = models.CharField(max_length=6, validators=[MinLengthValidator(4)], unique=True)

    activated = models.CharField(max_length=6, default="False")

    referrals = models.CharField(default="")

    USERNAME_FIELD = 'phoneNumber'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phoneNumber