# UI和Token处理问题修复

## 问题概述

在系统使用过程中，发现了以下几个影响用户体验的问题：

1. **Token处理问题**：
   - 当token缺失或过期时，系统会频繁显示错误消息并要求用户重新登录
   - 即使用户的会话仍然有效，也会被要求重新登录
   - 首次进入系统时，会显示"Authorization not obtained"错误消息

2. **登录界面UI问题**：
   - 登录窗口顶部的"USER LOGIN"和"ADMIN LOGIN"选项卡没有明显的视觉区分
   - 用户难以识别当前选中的是哪个选项卡
   - 没有默认选中的选项卡

3. **后端错误**：
   - 登录后显示"Server Error"
   - 后端日志显示在`StaffGetSerializer`中有一个问题，它试图排除一个名为'password'的字段，但这个字段在模型中不存在

## 解决方案

### 1. Token处理改进

#### 问题分析
当用户的token缺失或过期时，系统会立即显示错误消息并要求用户重新登录，即使用户的会话仍然有效。这导致了不必要的登录中断和糟糕的用户体验。

#### 实施的改进
1. **添加自动刷新token的功能**：
   - 添加了一个新的API端点`/login/refresh-token/`，用于刷新用户的token
   - 当检测到token缺失但用户已登录（通过其他session信息）时，系统会尝试自动刷新token
   - 如果刷新成功，用户可以无缝地继续使用系统，不需要重新登录

2. **添加token刷新锁定机制**：
   - 添加了`is_refreshing_token`标志，避免循环刷新token
   - 在token刷新开始时设置标志，在刷新结束时清除标志
   - 这样可以避免多个请求同时尝试刷新token，导致循环刷新

3. **改进错误处理**：
   - 完全禁止显示401错误消息，只触发登录窗口
   - 在首次加载时不发送不必要的请求，避免显示错误消息
   - 添加详细的日志输出，便于调试

### 2. 登录界面UI改进

#### 问题分析
登录窗口顶部的"USER LOGIN"和"ADMIN LOGIN"选项卡没有明显的视觉区分，用户难以识别当前选中的是哪个选项卡。

#### 实施的改进
1. **改进了选项卡的视觉效果**：
   - 增加了选项卡的宽度和高度
   - 添加了背景色和圆角，使选中的选项卡更加明显
   - 调整了不同状态下的透明度，使未选中的选项卡颜色变淡

2. **设置了默认选项卡**：
   - 默认选中"USER LOGIN"选项卡
   - 确保在首次加载时显示正确的选项卡

3. **改进了选项卡的交互体验**：
   - 移除了多余的tooltip，简化了界面
   - 增加了选项卡的点击区域，使其更容易点击

### 3. 后端错误修复

#### 问题分析
在`StaffGetSerializer`和`FileRenderSerializer`的Meta类中，我们看到了`exclude = ['openid', 'is_delete', 'password']`，但是`password`字段已经从模型中移除了。这导致了后端错误。

#### 实施的改进
1. **修改序列化器**：
   - 修改了`StaffGetSerializer`和`FileRenderSerializer`的Meta类，移除了不存在的'password'字段
   - 这样，序列化器不再尝试排除一个不存在的字段，避免了错误

2. **代码清理**：
   - 更新了代码注释，反映了密码字段已经从模型中移除的事实
   - 序列化器现在更加清晰，只排除实际存在的字段

## 技术细节

### 修改的文件
1. **templates/src/boot/axios_request.js**：
   - 添加了token刷新逻辑
   - 改进了错误处理
   - 添加了详细的日志输出

2. **templates/src/layouts/MainLayout.vue**：
   - 改进了登录窗口的选项卡样式
   - 添加了默认选项卡设置
   - 添加了token刷新成功后关闭登录窗口的逻辑

3. **staff/serializers.py**：
   - 修复了序列化器中的字段错误
   - 移除了对不存在字段的引用

### 关键代码片段

#### Token刷新逻辑
```javascript
// 检查是否正在刷新token，避免循环刷新
const isRefreshing = SessionStorage.getItem('is_refreshing_token') === 'true'
if (isRefreshing) {
  console.warn('Token refresh already in progress, skipping')
  return Promise.reject(new Error('Token refresh in progress'))
}

// 设置标志，表示正在刷新token
SessionStorage.set('is_refreshing_token', 'true')

// 尝试刷新token
return axiosInstance.post('/login/refresh-token/')
  .then(response => {
    if (response.data && response.data.code === '200' && response.data.data && response.data.data.openid) {
      // 保存新token
      const newToken = response.data.data.openid
      LocalStorage.set('openid', newToken)
      // 设置登录状态
      LocalStorage.set('auth', '1')
      // 更新请求头
      config.headers.token = newToken
      console.log('Token refreshed successfully')
      // 如果正在显示登录窗口，关闭它
      if (SessionStorage.getItem('showing_login') === 'true') {
        Bus.$emit('closeLogin', true)
        SessionStorage.remove('showing_login')
      }
      // 清除正在刷新token的标志
      SessionStorage.remove('is_refreshing_token')
      return config
    } else {
      // 清除正在刷新token的标志
      SessionStorage.remove('is_refreshing_token')
      // 不显示错误消息，直接重定向到登录页面
      Bus.$emit('needLogin', true)
      return Promise.reject(new Error('Failed to refresh token'))
    }
  })
```

#### 登录选项卡样式
```css
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
```

## 结论

通过这些改进，系统的用户体验得到了显著提升：

1. **更流畅的用户体验**：
   - 用户不再因为token问题而频繁中断操作
   - 系统会在后台自动处理token问题，对用户透明
   - 只有在确实无法解决问题时，才会提示用户重新登录

2. **更清晰的界面**：
   - 登录窗口的选项卡更加明显，用户可以更容易地区分当前选中的是哪个选项卡
   - 默认选中"USER LOGIN"选项卡，符合大多数用户的使用习惯

3. **更稳定的系统**：
   - 修复了后端错误，避免了"Server Error"
   - 系统更加健壮，能够更好地处理各种情况

这些改进使系统更加用户友好和健壮，提供了更好的用户体验。
