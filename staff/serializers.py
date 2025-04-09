from rest_framework import serializers
from .models import ListModel, TypeListModel
from utils import datasolve
# make_password import removed as password field is no longer used

class StaffGetSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=True, required=False)
    real_name = serializers.CharField(read_only=True, required=False) # Added
    staff_type = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False) # Added
    phone_number = serializers.CharField(read_only=True, required=False) # Added
    # Removed check_code and openid from default view if not needed
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ListModel
        # Keep openid/check_code excluded for now
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', ]

class StaffPostSerializer(serializers.ModelSerializer):
    # openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate]) # No longer required for creation
    staff_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added, optional
    staff_type = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=True) # Added, required
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added, optional
    # password field removed as it's not used for authentication
    # check_code = serializers.IntegerField(read_only=False, required=True, validators=[datasolve.data_validate]) # No longer required for creation

    class Meta:
        model = ListModel
        # Keep check_code and openid excluded if they are not set during creation
        exclude = ['is_delete',  'openid']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    # create method simplified as password field is removed
    def create(self, validated_data):
        return super().create(validated_data)

class StaffUpdateSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    staff_type = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=True) # Changed to required
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    # password field removed as it's not used for authentication

    class Meta:
        model = ListModel
        # Exclude fields not typically updated this way
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    # update method with custom error handling
    def update(self, instance, validated_data):
        try:
            # Check if email already exists for another user
            email = validated_data.get('email')
            if email and ListModel.objects.filter(email=email).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"email": ["This email address is already in use by another user."]})

            return super().update(instance, validated_data)
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception:
            # Generic database error, likely a unique constraint violation
            raise serializers.ValidationError({"email": ["This email address is already in use by another user."]})


class StaffPartialUpdateSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    staff_type = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=False) # Added
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    # password field removed as it's not used for authentication

    class Meta:
        model = ListModel
        # Exclude fields not typically updated this way
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    # update method with custom error handling
    def update(self, instance, validated_data):
        try:
            # Check if email already exists for another user
            email = validated_data.get('email')
            if email and ListModel.objects.filter(email=email).exclude(id=instance.id).exists():
                raise serializers.ValidationError({"email": ["This email address is already in use by another user."]})

            return super().update(instance, validated_data)
        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception:
            # Generic database error, likely a unique constraint violation
            raise serializers.ValidationError({"email": ["This email address is already in use by another user."]})

class FileRenderSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=False)
    real_name = serializers.CharField(read_only=False, required=False) # Added
    staff_type = serializers.CharField(read_only=False, required=False)
    email = serializers.EmailField(read_only=False, required=False) # Added
    phone_number = serializers.CharField(read_only=False, required=False) # Added
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ListModel
        ref_name = 'StaffFileRenderSerializer'
        # Exclude sensitive/internal fields
        exclude = ['openid', 'is_delete']

class StaffTypeGetSerializer(serializers.ModelSerializer):
    staff_type = serializers.CharField(read_only=True, required=False)
    creater = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)
    class Meta:
        model = TypeListModel
        exclude = ['openid']
        read_only_fields = ['id', ]
