<template>
  <q-page class="flex flex-center">
    <q-card class="q-pa-md" style="width: 400px">
      <q-card-section>
        <div class="text-h6 text-center">{{ $t('index.register') }}</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onSubmit">
          <q-input
            v-model="formData.staff_name"
            :label="$t('index.staff_name')"
            outlined
            dense
            :rules="[val => !!val || $t('validation.required')]"
          />

          <q-input
            v-model="formData.email"
            :label="$t('index.email')"
            outlined
            dense
            type="email"
            :rules="[
              val => !!val || $t('validation.required'),
              val => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) || $t('validation.email')
            ]"
          />

          <q-input
            v-model="formData.password"
            :label="$t('index.password')"
            outlined
            dense
            type="password"
            :rules="[
              val => !!val || $t('validation.required'),
              val => val.length >= 8 || $t('validation.password_length')
            ]"
          />

          <q-input
            v-model="formData.confirmPassword"
            :label="$t('index.confirm_password')"
            outlined
            dense
            type="password"
            :rules="[
              val => !!val || $t('validation.required'),
              val => val === formData.password || $t('validation.password_match')
            ]"
          />

          <q-input
            v-model="formData.phone_number"
            :label="$t('index.phone_number')"
            outlined
            dense
            :rules="[
              val => !!val || $t('validation.required'),
              val => /^[0-9]{10,15}$/.test(val) || $t('validation.phone')
            ]"
          />

          <q-select
            v-model="formData.staff_type"
            :label="$t('index.staff_type')"
            :options="staffTypes"
            outlined
            dense
            :rules="[val => !!val || $t('validation.required')]"
          />

          <q-input
            v-model="formData.real_name"
            :label="$t('index.real_name')"
            outlined
            dense
          />

          <div class="q-mt-md">
            <q-btn
              type="submit"
              color="primary"
              :label="$t('index.register')"
              class="full-width"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useQuasar } from 'quasar'

export default {
  setup() {
    const $store = useStore()
    const $router = useRouter()
    const $q = useQuasar()

    const formData = ref({
      staff_name: '',
      email: '',
      password: '',
      confirmPassword: '',
      phone_number: '',
      staff_type: '',
      real_name: ''
    })

    const staffTypes = [
      { label: 'Admin', value: 'admin' },
      { label: 'Staff', value: 'staff' },
      { label: 'Manager', value: 'manager' }
    ]

    const onSubmit = () => {
      $store.dispatch('registerUser', formData.value)
        .then(() => {
          $q.notify({
            type: 'positive',
            message: $q.lang.t('notice.register_success')
          })
          $router.push({ name: 'login' })
        })
        .catch(error => {
          $q.notify({
            type: 'negative',
            message: error.message || $q.lang.t('notice.register_failed')
          })
        })
    }

    return {
      formData,
      staffTypes,
      onSubmit
    }
  }
}
</script>