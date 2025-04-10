<template>
  <q-page class="flex flex-center">
    <div class="q-pa-md" style="max-width: 400px">
      <q-card class="my-card">
        <q-card-section>
          <div class="text-h6">{{ $t('index.reset_password') }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="onSubmit" class="q-gutter-md">
            <q-input
              v-model="password"
              :label="$t('index.new_password')"
              type="password"
              :rules="[val => !!val || $t('validation.required')]"
            />

            <q-input
              v-model="confirmPassword"
              :label="$t('index.confirm_password')"
              type="password"
              :rules="[
                val => !!val || $t('validation.required'),
                val => val === password || $t('validation.passwords_must_match')
              ]"
            />

            <div>
              <q-btn :label="$t('index.submit')" type="submit" color="primary" class="full-width"/>
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script>
import { post } from 'boot/axios_request'

export default {
  name: 'ResetPasswordPage',

  data () {
    return {
      token: this.$route.query.token || '',
      password: '',
      confirmPassword: ''
    }
  },

  methods: {
    onSubmit () {
      var _this = this

      if (!_this.token) {
        _this.$q.notify({
          type: 'negative',
          message: _this.$t('index.invalid_token')
        })
        return
      }

      if (_this.password !== _this.confirmPassword) {
        _this.$q.notify({
          type: 'negative',
          message: _this.$t('validation.passwords_must_match')
        })
        return
      }

      _this.$q.loading.show()

      post('userlogin/reset-password-confirm/', {
        token: _this.token,
        new_password: _this.password,
        confirm_password: _this.confirmPassword
      })
        .then(response => {
          _this.$q.loading.hide()

          if (response.code === '200') {
            _this.$q.notify({
              type: 'positive',
              message: _this.$t('index.password_reset_success')
            })

            // Redirect to login page
            _this.$router.push({ name: 'login' })
          } else {
            _this.$q.notify({
              type: 'negative',
              message: response.msg || _this.$t('index.password_reset_failed')
            })
          }
        })
        .catch(error => {
          _this.$q.loading.hide()
          _this.$q.notify({
            type: 'negative',
            message: error.detail || _this.$t('index.password_reset_failed')
          })
        })
    }
  }
}
</script>
