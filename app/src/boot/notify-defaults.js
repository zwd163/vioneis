import { Notify } from 'quasar'

Notify.setDefaults({
  position: 'top',
  type: 'positive',
  progress: true,
  timeout: 5000,  // 增加通知显示时间到5秒
  textColor: 'white',
  classes: 'push'
})
