<template>
  <q-layout
    view="hHh LpR fFf"
    :style="{ height: $q.screen.height, width: $q.screen.width }"
  >
    <q-header reveal elevated class="bg-primary text-white">
      <q-toolbar class="main-headers text-white shadow-18 rounded-borders">
        <transition appear enter-active-class="animated zoomIn">
          <q-btn flat @click="drawerleft = !drawerleft" round dense icon="menu">
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[15, 15]"
              content-style="font-size: 12px"
              >{{ $t("index.hide_menu") }}</q-tooltip
            >
          </q-btn>
        </transition>
        <transition appear enter-active-class="animated zoomIn">
          <q-toolbar-title shrink class="text-weight-bold" @click="$router.push({ name: 'web_index' })">{{
            $t("index.title")
          }}</q-toolbar-title>
        </transition>
        <q-space />

        <transition appear enter-active-class="animated zoomIn">
          <q-btn
            icon="api"
            round
            dense
            flat
            @click="apiLink()"
            style="margin: 0 10px 0 10px"
          >
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[15, 15]"
              content-style="font-size: 12px"
              >{{ $t('index.api') }}</q-tooltip
            >
          </q-btn>
        </transition>
        <transition appear enter-active-class="animated zoomIn">
          <q-btn
            square
            dense
            flat
            color="white"
            :label="warehouse_name"
            icon="maps_home_work"
            style="margin: 0 10px 0 10px"
          >
            <q-menu>
              <q-list style="min-width: 100px">
                <q-item
                  clickable
                  v-close-popup
                  v-for="(warehouse, index) in warehouseOptions"
                  :key="index"
                  @click="warehouseChange(index)"
                >
                  <q-item-section>{{ warehouse.warehouse_name }}</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </transition>
        <transition appear enter-active-class="animated zoomIn">
          <q-btn
            round
            dense
            flat
            color="white"
            icon="translate"
            style="margin: 0 10px 0 10px"
          >
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[15, 15]"
              content-style="font-size: 12px"
              >{{ $t("index.translate") }}</q-tooltip
            >
            <q-menu>
              <q-list style="min-width: 100px">
                <q-item
                  clickable
                  v-close-popup
                  v-for="(language, index) in langOptions"
                  :key="index"
                  @click="langChange(language.value)"
                >
                  <q-item-section>{{ language.label }}</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </transition>
        <q-separator vertical />
        <template v-if="authin === '1'">
          <transition appear enter-active-class="animated zoomIn">
            <q-btn-dropdown
              stretch
              flat
              color="white-8"
              icon="account_circle"
            >
              <div class="row no-wrap q-pa-md">
                <div class="column" style="width: 150px">
                  <div class="text-h6 q-mb-md">
                    {{ $t("index.user_center") }}
                  </div>
                  <q-btn
                    flat
                    rounded
                    class="full-width"
                    align="left"
                    :label="$t('index.change_user')"
                    @click="login = true"
                  >
                    <q-tooltip
                      content-class="bg-amber text-black shadow-4"
                      :offset="[10, 10]"
                      content-style="font-size: 12px"
                      >{{ $t("index.change_user") }}</q-tooltip
                    >
                  </q-btn>
                  <q-btn
                    flat
                    rounded
                    class="full-width"
                    align="left"
                    :label="$t('index.view_my_openid')"
                    @click="authid = true"
                  >
                    <q-tooltip
                      content-class="bg-amber text-black shadow-4"
                      :offset="[10, 10]"
                      content-style="font-size: 12px"
                      >{{ $t("index.view_my_openid") }}</q-tooltip
                    >
                  </q-btn>
                </div>
                <q-separator vertical inset class="q-mx-lg" />
                <div class="column items-center">
                  <q-avatar size="72px"
                    ><q-img src="statics/staff/stafftype.png"></q-img
                  ></q-avatar>
                  <div class="text-subtitle1 q-mt-md q-mb-xs">
                    {{ login_name }}
                  </div>
                  <q-btn
                    color="primary"
                    :label="$t('index.logout')"
                    push
                    size="sm"
                    v-close-popup
                    icon="img:statics/icons/logout.png"
                    @click="Logout()"
                  >
                    <q-tooltip
                      content-class="bg-amber text-black shadow-4"
                      :offset="[10, 10]"
                      content-style="font-size: 12px"
                      >{{ $t("index.logout") }}</q-tooltip
                    >
                  </q-btn>
                </div>
              </div>
            </q-btn-dropdown>
          </transition>
        </template>
        <template v-if="authin === '0'">
          <transition appear enter-active-class="animated zoomIn">
            <q-btn
              :label="$t('index.login')"
              color="primary"
              @click="login = true"
              style="margin-left: 10px"
            >
              <q-tooltip
                content-class="bg-amber text-black shadow-4"
                :offset="[15, 15]"
                content-style="font-size: 12px"
                >{{ $t("index.login_tip") }}</q-tooltip
              >
            </q-btn>
          </transition>
          <transition appear enter-active-class="animated zoomIn">
            <q-btn
              :label="$t('index.register')"
              color="primary"
              @click="register = true"
              style="margin-left: 10px"
            >
              <q-tooltip
                content-class="bg-amber text-black shadow-4"
                :offset="[15, 15]"
                content-style="font-size: 12px"
                >{{ $t("index.register_tip") }}</q-tooltip
              >
            </q-btn>
          </transition>
        </template>
      </q-toolbar>
    </q-header>
    <q-drawer
      v-model="drawerleft"
      show-if-above
      :width="200"
      :breakpoint="500"
      bordered
      content-class="bg-grey-3 shadow-24"
    >
      <q-scroll-area class="fit" style="overflow-y: auto">
        <q-list>
          <q-item
            clickable
            :to="{ name: 'outbounddashboard' }"
            @click="linkChange('outbounddashboard')"
            v-ripple
            exact
            :active="link === 'outbounddashboard' && link !== ''"
            :class="{
              'my-menu-link': link === 'outbounddashboard' && link !== '',
            }"
          >
            <q-item-section avatar><q-icon name="auto_graph" /></q-item-section>
            <q-item-section>{{ $t("menuItem.dashboard") }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item
            clickable
            :to="{ name: 'asn' }"
            @click="linkChange('inbound')"
            v-ripple
            exact
            :active="link === 'inbound' && link !== ''"
            :class="{ 'my-menu-link': link === 'inbound' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="speaker_notes"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.inbound") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'dn' }"
            @click="linkChange('outbound')"
            v-ripple
            exact
            :active="link === 'outbound' && link !== ''"
            :class="{ 'my-menu-link': link === 'outbound' && link !== '' }"
          >
            <q-item-section avatar><q-icon name="rv_hookup" /></q-item-section>
            <q-item-section>{{ $t("menuItem.outbound") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'stocklist' }"
            @click="linkChange('stock')"
            v-ripple
            exact
            :active="link === 'stock' && link !== ''"
            :class="{ 'my-menu-link': link === 'stock' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="multiline_chart"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.stock") }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item
            clickable
            :to="{ name: 'capitallist' }"
            @click="linkChange('finance')"
            v-ripple
            exact
            :active="link === 'finance' && link !== ''"
            :class="{ 'my-menu-link': link === 'finance' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="devices_other"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.finance") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'goodslist' }"
            @click="linkChange('goods')"
            v-ripple
            exact
            :active="link === 'goods' && link !== ''"
            :class="{ 'my-menu-link': link === 'goods' && link !== '' }"
          >
            <q-item-section avatar><q-icon name="shop_two" /></q-item-section>
            <q-item-section>{{ $t("menuItem.goods") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'company' }"
            @click="linkChange('baseinfo')"
            v-ripple
            exact
            :active="link === 'baseinfo' && link !== ''"
            :class="{ 'my-menu-link': link === 'baseinfo' && link !== '' }"
          >
            <q-item-section avatar><q-icon name="info" /></q-item-section>
            <q-item-section>{{ $t("menuItem.baseinfo") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'warehouseset' }"
            @click="linkChange('warehouse')"
            v-ripple
            exact
            :active="link === 'warehouse' && link !== ''"
            :class="{ 'my-menu-link': link === 'warehouse' && link !== '' }"
          >
            <q-item-section avatar><q-icon name="settings" /></q-item-section>
            <q-item-section>{{ $t("menuItem.warehouse") }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item
            clickable
            :to="{ name: 'stafflist' }"
            @click="linkChange('staff')"
            v-ripple
            exact
            :active="link === 'staff' && link !== ''"
            :class="{ 'my-menu-link': link === 'staff' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="assignment_ind"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.staff") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'driverlist' }"
            @click="linkChange('driver')"
            v-ripple
            exact
            :active="link === 'driver' && link !== ''"
            :class="{ 'my-menu-link': link === 'driver' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="transfer_within_a_station"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.driver") }}</q-item-section>
          </q-item>
          <q-separator />
          <q-item
            clickable
            :to="{ name: 'initializeupload' }"
            @click="linkChange('uploadcenter')"
            v-ripple
            exact
            :active="link === 'uploadcenter' && link !== ''"
            :class="{ 'my-menu-link': link === 'uploadcenter' && link !== '' }"
          >
            <q-item-section avatar
              ><q-icon name="file_upload"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.uploadcenter") }}</q-item-section>
          </q-item>
          <q-item
            clickable
            :to="{ name: 'downloadinbound' }"
            @click="linkChange('downloadcenter')"
            v-ripple
            exact
            :active="link === 'downloadcenter' && link !== ''"
            :class="{
              'my-menu-link': link === 'downloadcenter' && link !== '',
            }"
          >
            <q-item-section avatar
              ><q-icon name="file_download"
            /></q-item-section>
            <q-item-section>{{ $t("menuItem.downloadcenter") }}</q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>
    <q-page-container
      class="main-page"
      :style="{
        height: container_height,
        width: $q.screen.width,
      }"
    >
      <router-view />
    </q-page-container>
    <q-dialog
      v-model="authid"
      transition-show="jump-down"
      transition-hide="jump-up"
    >
      <q-card style="min-width: 350px">
        <q-bar
          class="bg-light-blue-10 text-white rounded-borders"
          style="height: 50px"
        >
          <div>{{ $t("index.your_openid") }}</div>
          <q-space></q-space>
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[20, 20]"
              content-style="font-size: 12px"
              >{{ $t("index.close") }}</q-tooltip
            >
          </q-btn>
        </q-bar>
        <q-card-section class="q-pt-md"
          ><q-input
            dense
            outlined
            square
            label="Openid"
            v-model="openid"
            readonly
            disable
        /></q-card-section>
      </q-card>
    </q-dialog>
    <q-dialog
      v-model="login"
      transition-show="jump-down"
      transition-hide="jump-up"
    >
      <q-card style="min-width: 350px">
        <q-bar
          class="bg-light-blue-10 text-white rounded-borders"
          style="height: 50px"
        >
          <q-tabs
            v-model="activeTab"
            class="tabs"
            active-color="white"
            indicator-color="white"
            :breakpoint="0"
          >
            <q-tab
              name="user"
              @click="admin = false"
              :class="{'active-tab': !admin, 'inactive-tab': admin}"
            >
              {{ $t("index.user_login") }}
            </q-tab>
            <q-tab
              name="admin"
              @click="admin = true"
              :class="{'active-tab': admin, 'inactive-tab': !admin}"
            >
              {{ $t("index.admin_login") }}
            </q-tab>
          </q-tabs>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[20, 20]"
              content-style="font-size: 12px"
              >{{ $t("index.close") }}</q-tooltip
            >
          </q-btn>
        </q-bar>
        <q-card-section class="q-pt-md">
          <template v-if="admin">
            <q-input
              dense
              outlined
              square
              :label="$t('index.admin_name')"
              v-model="adminlogin.name"
              autofocus
              @keyup.enter="adminLogin()"
              :rules="[val => !!val || $t('validation.required')]"
            />
            <q-input
              dense
              outlined
              square
              :label="$t('index.password')"
              :type="isPwd ? 'password' : 'text'"
              v-model="adminlogin.password"
              @keyup.enter="adminLogin()"
              style="margin-top: 5px"
              :rules="[val => !!val || $t('validation.required')]"
            >
              <template v-slot:append>
                <q-icon
                  :name="isPwd ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd = !isPwd"
                />
              </template>
            </q-input>
          </template>
          <template v-if="!admin">
            <q-input
              dense
              outlined
              square
              :label="$t('index.staff_name')"
              v-model="loginform.name"
              autofocus
              @keyup.enter="Login()"
              bottom-slots
            />
            <q-input
            dense
            outlined
            square
            :label="$t('index.password')"
            :type="isPwd ? 'password' : 'text'"
            v-model="loginform.password"
            @keyup.enter="Login()"
            style="margin-top: 5px"
            bottom-slots
          >
              <template v-slot:append>
                <q-icon
                  :name="isPwd ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd = !isPwd"
                />
              </template>
            </q-input>
          </template>
        </q-card-section>
        <q-card-actions align="left" class="text-primary">
          <q-space />
          <template>
            <q-btn
              color="primary"
              :label="$t('index.login')"
              style="font-size: 16px; margin: 0 8px; width: 100%"
              @click="admin ? adminLogin() : Login()"
            />
          </template>
          <div class="q-mx-auto">
            <q-btn
              flat
              class="text-teal-4 q-mt-sm"
              @click="
                login = false;
                register = true;
              "
            >
              {{ $t("index.register_tip") }}
            </q-btn>
            <!-- Explanation: Add the "Forgot Password" link -->
            <q-btn
              flat
              class="text-teal-4 q-mt-sm"
              @click="forgotPassword = true; login = false"
            >
              {{ $t("index.forgot_password") }}
            </q-btn>
          </div>
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="forgotPassword">
      <q-card style="min-width: 350px">
        <q-bar
          class="bg-light-blue-10 text-white rounded-borders"
          style="height: 50px"
        >
          <div>{{ $t("index.forgot_password") }}</div>
          <q-space></q-space>
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[20, 20]"
              content-style="font-size: 12px"
              >{{ $t("index.close") }}</q-tooltip
            >
          </q-btn>
        </q-bar>
        <q-card-section class="q-pt-md">
          <!-- 错误消息区域 -->
          <div v-if="forgotPasswordError" class="text-negative q-mb-md">
            <q-icon name="error" />
            {{ forgotPasswordError }}
          </div>

          <q-input
            dense
            outlined
            square
            :label="$t('index.staff_name')"
            v-model="forgotPasswordForm.name"
            autofocus
            bottom-slots
          />
          <q-input
            dense
            outlined
            square
            :label="$t('index.email')"
            v-model="forgotPasswordForm.email"
            style="margin-top: 5px"
            bottom-slots
          />
        </q-card-section>
        <q-card-actions align="right" class="text-primary q-mx-sm">
          <q-btn
            class="full-width"
            color="primary"
            :label="$t('index.reset_password')"
            @click="ResetPassword()"
            :loading="isLoading"
          />
        </q-card-actions>
        <q-card-actions align="center" style="margin-top: -8px">
          <q-btn
            class="text-teal-4"
            flat
            :label="$t('index.return_to_login')"
            @click="login = true; forgotPassword = false"
            :disable="isLoading"
          ></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog
      v-model="register"
      transition-show="jump-down"
      transition-hide="jump-up"
    >
      <q-card style="min-width: 350px">
        <q-bar
          class="bg-light-blue-10 text-white rounded-borders"
          style="height: 50px"
        >
          <div>{{ $t("index.register_tip") }}</div>
          <q-space></q-space>
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip
              content-class="bg-amber text-black shadow-4"
              :offset="[20, 20]"
              content-style="font-size: 12px"
              >{{ $t("index.close") }}</q-tooltip
            >
          </q-btn>
        </q-bar>
        <q-card-section class="q-pt-md">
          <q-input
            dense
            outlined
            square
            :label="$t('index.staff_name')"
            v-model="registerform.name"
            autofocus
            @keyup.enter="Register()"
          />
          <q-input
            dense
            outlined
            square
            :label="$t('index.email')"
            v-model="registerform.email"
            type="email"
            @keyup.enter="Register()"
            style="margin-top: 5px"
          />
          <q-input
            dense
            outlined
            square
            :label="$t('index.password')"
            v-model="registerform.password1"
            :type="isPwd ? 'password' : 'text'"
            @keyup.enter="Register()"
            style="margin-top: 5px"
          >
            <template v-slot:append>
              <q-icon
                :name="isPwd ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd = !isPwd"
              />
            </template>
          </q-input>
          <q-input
            dense
            outlined
            square
            :label="$t('index.confirm_password')"
            v-model="registerform.password2"
            :type="isPwd2 ? 'password' : 'text'"
            @keyup.enter="Register()"
            style="margin-top: 5px"
          >
            <template v-slot:append>
              <q-icon
                :name="isPwd2 ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="isPwd2 = !isPwd2"
              />
            </template>
          </q-input>
        </q-card-section>
        <q-card-actions align="right" class="text-primary q-mx-sm"
          ><q-btn
            class="full-width"
            color="primary"
            :label="$t('index.register')"
            @click="Register()"
        /></q-card-actions>
        <q-card-actions align="center" style="margin-top: -8px">
          <q-btn
            class="text-teal-4"
            flat
            :label="$t('index.return_to_login')"
            @click="
              login = true;
              register = false;
            "
          ></q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>
<script>
import { get, getauth, post, postauth, baseurl } from 'boot/axios_request'
import { LocalStorage, SessionStorage, openURL } from 'quasar'
import Bus from 'boot/bus.js'

export default {
  data () {
    return {
      device: LocalStorage.getItem('device'),
      device_name: LocalStorage.getItem('device_name'),
      lang: this.$i18n.locale,
      container_height: this.$q.screen.height + '' + 'px',
      warehouse_name: '',
      warehouseOptions: [],
      langOptions: [
        { value: 'en-US', label: 'English' },
        { value: 'zh-hans', label: '中文简体' },
        { value: 'zh-hant', label: '中文繁體' },
        { value: 'fr', label: 'Français' },
        { value: 'pt', label: 'Português' },
        { value: 'sp', label: 'Español' },
        { value: 'de', label: 'Deutsch' },
        { value: 'ru', label: 'русский язык' },
        { value: 'ar', label: 'Arabic' },
        { value: 'it', label: 'Italiano' },
        { value: 'ja', label: '日本語' }
      ],
      title: this.$t('index.webtitle'),
      admin: false,
      adminlogin: {
        name: '',
        password: ''
      },
      openid: '',
      isPwd: true,
      isPwd2: true,
      authin: '0',
      authid: false,
      left: false,
      drawerleft: false,
      tab: '',
      login: false,
      link: '',
      login_name: '',
      login_id: 0,
      check_code: '',
      register: false,
      registerform: {
        name: '',
        email: '',
        password1: '',
        password2: ''
      },
      loginform: {
        name: '',
        password: ''
      },
      // Explanation: Add the forgotPassword data property.
      forgotPassword: false,
      forgotPasswordForm: {
        name: '',
        email: ''
      },
      forgotPasswordError: '',
      isLoading: false,
      needLogin: '',
      activeTab: ''
    }
  },
  methods: {
    linkChange (e) {
      var _this = this
      localStorage.removeItem('menulink')
      localStorage.setItem('menulink', e)
      _this.link = e
    },
    drawerClick (e) {
      var _this = this
      if (_this.miniState) {
        _this.miniState = false
        e.stopPropagation()
      }
    },
    brownlink (e) {
      openURL(e)
    },
    apiLink () {
      openURL(baseurl + '/api/docs/')
    },


Login () {
  var _this = this
  console.log('[DEBUG] Login method called')
  if (!_this.loginform.name || _this.loginform.name.trim() === '') {
    _this.$q.notify({
      message: _this.$t('validation.required'),
      color: 'negative',
      icon: 'close',
      timeout: 2000
    })
    return
  }
  if (!_this.loginform.password || _this.loginform.password.trim() === '') {
    _this.$q.notify({
      message: _this.$t('validation.required'),
      icon: 'close',
      color: 'negative',
      timeout: 2000
    })
    return
  }
  // 清除所有标志，确保登录过程不受影响
  SessionStorage.remove('is_refreshing_token')
  SessionStorage.remove('showing_login')

  SessionStorage.set('axios_check', 'false')
  post('/login/', {name: _this.loginform.name, password: _this.loginform.password}) //  Changed URL to /login/
    .then((res) => {
      // Explanation: Check the response code.
      if (res.code === '200') {
        console.log('[DEBUG] Login successful, setting auth status')
        _this.authin = '1'
        _this.login = false
        _this.login_id = res.data.user_id
        LocalStorage.set('auth', '1')
        LocalStorage.set('login_name', res.data.name) // CHANGE: Changed to res.data.name
        LocalStorage.set('login_id', res.data.user_id)
        LocalStorage.set('login_mode', 'user')
        // 设置 token
        if (res.data.openid) {
          console.log('[DEBUG] Setting openid from login response')
          LocalStorage.set('openid', res.data.openid)
        }
        // 清除所有标志
        SessionStorage.remove('is_refreshing_token')
        SessionStorage.remove('showing_login')
        _this.$q.notify({
          message: _this.$t('index.login_success'),
          icon: 'check',
          color: 'green',
          timeout: 5000  // 增加通知显示时间到5秒
        })
        // Explanation: Call the staffType() method.
        _this.staffType()
        localStorage.removeItem('menulink')
        _this.link = ''
        _this.$router.push({ name: 'web_index' })
        window.setTimeout(() => {
          location.reload()
        }, 1)
      } else {
        _this.$q.notify({
          message: res.msg || _this.$t('index.login_failed'),
          icon: 'close',
          color: 'negative',
          timeout: 5000  // 增加通知显示时间到5秒
        })
      }
    })
    .catch((err) => {
      _this.$q.notify({
        message: err.detail || _this.$t('index.login_error'),
        icon: 'close',
        color: 'negative',
        timeout: 5000  // 增加通知显示时间到5秒
      })
    })
    },

    // MainLayout.vue
    adminLogin () {
      var _this = this
      if (!_this.adminlogin.name) {
        _this.$q.notify({
          message: _this.$t('validation.required', { field: _this.$t('index.admin_name') }),
          color: 'negative',
          icon: 'close'
        })
        return
      }
      if (!_this.adminlogin.password) {
        _this.$q.notify({
          message: _this.$t('validation.required', { field: _this.$t('index.password') }),
          icon: 'close',
          color: 'negative'
        })
        return
      }
      SessionStorage.set('axios_check', 'false')
      post('login/', _this.adminlogin)
        .then((res) => {
          // Explanation: Check the response code.
          if (res.code === '200') {
            _this.authin = '1'
            _this.login = false
            _this.admin = false
            _this.openid = res.data.openid
            _this.login_name = res.data.name
            _this.login_id = res.data.user_id
            LocalStorage.set('auth', '1')
            LocalStorage.set('openid', res.data.openid)
            LocalStorage.set('login_name', _this.login_name)
            LocalStorage.set('login_id', _this.login_id)
            LocalStorage.set('login_mode', 'admin')
            _this.$q.notify({
              message: _this.$t('index.login_success'),
              icon: 'check',
              color: 'green',
              timeout: 5000  // 增加通知显示时间到5秒
            })
            // Explanation: Call the staffType() method.
            _this.staffType()
            localStorage.removeItem('menulink')
            _this.link = ''
            _this.$router.push({ name: 'web_index' })
            window.setTimeout(() => {
              location.reload()
            }, 1)
          } else {
            _this.$q.notify({
              message: res.msg || _this.$t('index.login_failed'),
              icon: 'close',
              color: 'negative'
            })
          }
        })
        .catch((err) => {
          _this.$q.notify({
            message: err.detail || _this.$t('index.login_error'),
            icon: 'close',
            color: 'negative'
          })
        })
    },

    staffType () {
      var _this = this
      // Explanation: Check if the login_mode is admin.
      if(LocalStorage.getItem('login_mode') === 'admin'){
        LocalStorage.set('staff_type', 'Admin')
        return
      }
      getauth('staff/?staff_name=' + _this.login_name).then((res) => {

        // Explanation: Check if the staff data is found.
        if(res.count > 0){
          LocalStorage.set('staff_type', res.results[0].staff_type)
        } else {
          LocalStorage.set('staff_type', 'Admin')
        }
      })
    },
    // Explanation: Add the ResetPassword() method.
    ResetPassword () {
      console.log('ResetPassword function called')
      var _this = this
      console.log('forgotPasswordForm:', _this.forgotPasswordForm)

      // 清除之前的错误消息
      _this.forgotPasswordError = ''

      if (!_this.forgotPasswordForm.name || _this.forgotPasswordForm.name.trim() === '') {
        console.log('Name is empty')
        _this.forgotPasswordError = _this.$t('validation.required', { field: _this.$t('index.staff_name') })
        _this.$q.notify({
          message: _this.forgotPasswordError,
          color: 'negative',
          icon: 'close',
          timeout: 5000 // 显示5秒
        })
        return
      }
      if (!_this.forgotPasswordForm.email || _this.forgotPasswordForm.email.trim() === '') {
        console.log('Email is empty')
        _this.forgotPasswordError = _this.$t('validation.required', { field: _this.$t('index.email') })
        _this.$q.notify({
          message: _this.forgotPasswordError,
          icon: 'close',
          color: 'negative',
          timeout: 5000 // 显示5秒
        })
        return
      }

      // Send forgot password request to the backend
      const data = {
        username: _this.forgotPasswordForm.name,
        email: _this.forgotPasswordForm.email
      }

      console.log('Sending data:', data)

      // 设置加载状态
      _this.isLoading = true

      // 清除之前的错误消息
      _this.forgotPasswordError = ''

      // 使用XMLHttpRequest发送请求
      try {
        console.log('Using XMLHttpRequest to send request')

        // 使用确定的URL
        const apiUrl = 'http://127.0.0.1:8009/login/forgot-password/'

        console.log('API URL:', apiUrl)
        console.log('Sending data:', data)

        // 显示一个加载指示器在按钮上
        // 不需要额外的通知

        // 使用XMLHttpRequest而不是fetch
        var xhr = new XMLHttpRequest()
        xhr.open('POST', apiUrl, true)
        xhr.setRequestHeader('Content-Type', 'application/json')

        xhr.onload = function() {
          console.log('XHR response received:', xhr.status, xhr.responseText)
          _this.isLoading = false

          try {
            var responseData = JSON.parse(xhr.responseText)
            console.log('Response data:', responseData)

            if (responseData.code === '200') {
              _this.$q.notify({
                message: _this.$t('index.reset_email_sent'),
                icon: 'check',
                color: 'green',
                timeout: 10000 // 显示10秒
              })
              _this.forgotPasswordError = ''
              _this.forgotPassword = false
              _this.login = true
            } else {
              // 在表单上显示错误消息
              _this.forgotPasswordError = responseData.msg || _this.$t('index.reset_email_failed')
              _this.$q.notify({
                message: _this.forgotPasswordError,
                icon: 'close',
                color: 'negative',
                timeout: 10000 // 显示10秒
              })
            }
          } catch (e) {
            console.error('Error parsing response:', e)
            _this.forgotPasswordError = 'Error parsing response: ' + e.message
            _this.$q.notify({
              message: _this.forgotPasswordError,
              icon: 'close',
              color: 'negative',
              timeout: 10000 // 显示10秒
            })
          }
        }

        xhr.onerror = function() {
          console.error('XHR error')
          _this.isLoading = false
          _this.forgotPasswordError = 'Network error'
          _this.$q.notify({
            message: _this.forgotPasswordError,
            icon: 'close',
            color: 'negative',
            timeout: 10000 // 显示10秒
          })
        }

        console.log('Sending data:', JSON.stringify(data))
        xhr.send(JSON.stringify(data))
      } catch (e) {
        console.error('Exception in fetch:', e)
        _this.isLoading = false

        // 在表单上显示错误消息
        _this.forgotPasswordError = 'Error: ' + e.message
        _this.$q.notify({
          message: _this.forgotPasswordError,
          icon: 'close',
          color: 'negative',
          timeout: 10000 // 显示10秒
        })
      }
    },





    Logout () {
      var _this = this
      _this.authin = '0'
      _this.login_name = ''
      LocalStorage.remove('auth')
      SessionStorage.remove('axios_check')
      LocalStorage.set('login_name', '')
      LocalStorage.set('login_id', '')
      _this.$q.notify({
        message: 'Success Logout',
        icon: 'check',
        color: 'negative'
      })
      // _this.staffType();
      localStorage.removeItem('menulink')
      _this.link = ''
      _this.$router.push({ name: 'web_index' })
      window.setTimeout(() => {
        location.reload()
      }, 1)
    },
    Register () {
      var _this = this
      SessionStorage.set('axios_check', 'false')
      post('register/', _this.registerform)
        .then((res) => {
          if (res.code === '200') {
            _this.register = false
            _this.openid = res.data.openid
            _this.login_name = _this.registerform.name
            _this.login_id = res.data.user_id
            _this.authin = '1'
            LocalStorage.set('openid', res.data.openid)
            LocalStorage.set('login_name', _this.registerform.name)
            LocalStorage.set('login_id', _this.login_id)
            LocalStorage.set('auth', '1')
            _this.registerform = {
              name: '',
              email: '',
              password1: '',
              password2: ''
            }
            _this.$q.notify({
              message: res.msg,
              icon: 'check',
              color: 'green',
              timeout: 5000  // 增加通知显示时间到5秒
            })
            _this.staffType()
            localStorage.removeItem('menulink')
            _this.link = ''
            _this.$router.push({ name: 'web_index' })
            window.setTimeout(() => {
              location.reload()
            }, 1)
          } else {
            _this.$q.notify({
              message: res.msg,
              icon: 'close',
              color: 'negative'
            })
          }
        })
        .catch((err) => {
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
    },


    // MainLayout.vue
    staffType () {
      var _this = this
      // Explanation: Check if the login_mode is admin.
      if(LocalStorage.getItem('login_mode') === 'admin'){
        LocalStorage.set('staff_type', 'Admin')
        return
      }
      getauth('staff/?staff_name=' + _this.login_name).then((res) => {
        // Explanation: Check if the staff data is found.
        if(res.count > 0){
          LocalStorage.set('staff_type', res.results[0].staff_type)
        } else {
          LocalStorage.set('staff_type', 'Admin')
        }
      })
    },

    warehouseOptionsGet () {
      var _this = this
      // 使用axios直接发送请求，以便于调试
      const axios = require('axios')
      axios.get('http://127.0.0.1:8009/warehouse/multiple/?max_page=30')
        .then((response) => {
          const res = response.data
          if (res.count === 1) {
            _this.openid = res.results[0].openid
            _this.warehouse_name = res.results[0].warehouse_name
            LocalStorage.set('openid', _this.openid)
          } else {
            _this.warehouseOptions = res.results
            if (LocalStorage.has('openid')) {
              _this.warehouseOptions.forEach((item, index) => {
                if (item.openid === LocalStorage.getItem('openid')) {
                  _this.warehouse_name = item.warehouse_name
                }
              })
            }
          }
        })
        .catch(error => {
          console.error('Error fetching warehouse options:', error)
        })
        .catch((err) => {
          console.log(err)
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
    },
    warehouseChange (e) {
      var _this = this
      _this.warehouse_name = _this.warehouseOptions[e].warehouse_name
      _this.openid = _this.warehouseOptions[e].openid
      LocalStorage.set('openid', _this.openid)
      LocalStorage.set('staff_type', 'Admin')
      _this.login_name = ''
      LocalStorage.set('login_name', '')
      _this.authin = '0'
      _this.isLoggedIn()
      LocalStorage.remove('auth')
      SessionStorage.remove('axios_check')
    },
    langChange (e) {
      var _this = this
      _this.lang = e
      window.setTimeout(() => {
        location.reload()
      }, 1)
    },
    isLoggedIn () {
      // 始终显示登录对话框，而不是注册对话框
      console.log('[DEBUG] isLoggedIn called, setting login=true')
      console.log('[DEBUG] Current auth status:', LocalStorage.getItem('auth'))
      console.log('[DEBUG] Current showing_login status:', SessionStorage.getItem('showing_login'))
      this.login = true
      this.register = false
      // 设置标志，表示正在显示登录窗口
      SessionStorage.set('showing_login', 'true')
      console.log('[DEBUG] After setting showing_login:', SessionStorage.getItem('showing_login'))
    }
  },
  created () {
    var _this = this
    console.log('[DEBUG] MainLayout created hook called')
    // 设置标志，表示这是首次加载
    SessionStorage.set('not_first_load', 'true')
    console.log('[DEBUG] Set not_first_load to true')
    if (LocalStorage.has('openid')) {
      _this.openid = LocalStorage.getItem('openid')
      _this.activeTab = LocalStorage.getItem('login_mode') || 'user' // 默认为user
    } else {
      _this.openid = ''
      LocalStorage.set('openid', '')
      // 设置默认选项卡为user
      _this.activeTab = 'user'
      _this.admin = false
    }
    if (LocalStorage.has('login_name')) {
      _this.login_name = LocalStorage.getItem('login_name')
    } else {
      _this.login_name = ''
      LocalStorage.set('login_name', '')
    }
    if (LocalStorage.has('auth')) {
      _this.authin = '1'
      _this.staffType()
    } else {
      LocalStorage.set('staff_type', 'Admin')
      _this.authin = '0'
      _this.isLoggedIn()
    }
  },
  mounted () {
    var _this = this
    console.log('[DEBUG] MainLayout mounted hook called')
    console.log('[DEBUG] Current auth status:', LocalStorage.getItem('auth'))
    console.log('[DEBUG] Current showing_login status:', SessionStorage.getItem('showing_login'))
    // 如果用户已登录，才获取仓库选项
    if (LocalStorage.getItem('auth') === '1') {
      console.log('[DEBUG] User is logged in, getting warehouse options')
      _this.warehouseOptionsGet()
    } else {
      console.log('[DEBUG] User is not logged in, skipping warehouse options')
    }
    _this.link = localStorage.getItem('menulink')
    Bus.$on('needLogin', (val) => {
      console.log('[DEBUG] needLogin event received, val:', val)
      _this.isLoggedIn()
    })
    // 监听关闭登录窗口的事件
    Bus.$on('closeLogin', (val) => {
      console.log('[DEBUG] closeLogin event received, val:', val)
      if (val) {
        console.log('[DEBUG] Closing login window and setting auth status')
        _this.login = false
        _this.authin = '1'
        _this.staffType()
        // 登录成功后获取仓库选项
        _this.warehouseOptionsGet()
        // 清除showing_login标志
        SessionStorage.remove('showing_login')
        console.log('[DEBUG] Removed showing_login flag')
      }
    })
  },
  updated () {
  },
  beforeDestroy () {
    Bus.$off('needLogin')
    Bus.$off('closeLogin')
  },
  destroyed () {
  },
  watch: {
    lang (lang) {
      var _this = this
      LocalStorage.set('lang', lang)
      _this.$i18n.locale = lang
    },
    login (val) {
      if (val) {
        if (this.activeTab === 'admin') {
          this.admin = true
        } else {
          this.admin = false
        }
      }
    }
  }
}
</script>
<style>
.tabs .q-tab__indicator {
  width: 80%;
  height: 2px;
  margin: auto;
  color: white;
}
.tabs .absolute-bottom {
  bottom: 4px;
}

/* 新增样式 */
.active-tab {
  font-weight: bold;
  opacity: 1 !important;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.inactive-tab {
  opacity: 0.7 !important;
}

.tabs .q-tab {
  padding: 0 16px;
  min-height: 36px;
  margin: 4px;
}
</style>
