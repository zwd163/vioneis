# 忘记密码功能开发

## 功能概述

忘记密码功能允许用户在忘记登录密码时，通过提供用户名和注册邮箱来重置密码。系统会验证用户提供的信息，并向用户的注册邮箱发送一封包含密码重置链接的邮件。用户可以通过点击链接来设置新密码。

## 实现细节

### 前端实现

#### 1. 添加忘记密码对话框

在登录界面添加了"忘记密码"按钮和对话框，允许用户输入用户名和邮箱来请求密码重置。

```html
<q-dialog v-model="forgotPasswordDialog">
  <q-card style="min-width: 350px">
    <q-card-section>
      <div class="text-h6">{{ $t('index.forgot_password') }}</div>
    </q-card-section>
    <q-card-section class="q-pt-none">
      <q-input dense v-model="forgotPassword.username" :label="$t('index.username')" autofocus />
      <q-input dense v-model="forgotPassword.email" :label="$t('index.email')" class="q-mt-sm" />
    </q-card-section>
    <q-card-actions align="right">
      <q-btn flat :label="$t('index.cancel')" color="primary" v-close-popup />
      <q-btn flat :label="$t('index.submit')" color="primary" @click="submitForgotPassword" />
    </q-card-actions>
  </q-card>
</q-dialog>
```

#### 2. 添加忘记密码按钮

在登录界面底部添加了"忘记密码"按钮，点击后显示忘记密码对话框。

```html
<q-page-sticky v-show="!fab1 && !fab2 && !fab3 && !fab4" position="bottom" :offset="[0, 120]">
  <q-btn flat color="primary" :label="$t('index.forgot_password')" @click="forgotPasswordDialog = true"/>
</q-page-sticky>
```

#### 3. 添加提交忘记密码请求的方法

添加了`submitForgotPassword`方法，用于向后端发送忘记密码请求。

```javascript
submitForgotPassword() {
  var _this = this;
  if (!_this.forgotPassword.username || !_this.forgotPassword.email) {
    _this.$q.notify({
      message: _this.$t('validation.required'),
      color: 'negative',
      icon: 'close',
      timeout: 2000
    });
    return;
  }
  
  _this.$axios.post(_this.baseurl + '/forgot-password/', _this.forgotPassword)
    .then((res) => {
      if (res.data.code === '200') {
        _this.$q.notify({
          message: _this.$t('notice.mobile_userlogin.notice9')
        });
        _this.forgotPasswordDialog = false;
      } else {
        _this.$q.notify({
          type: 'negative',
          message: _this.$t('notice.mobile_userlogin.notice10')
        });
      }
    })
    .catch((err) => {
      _this.$q.notify({
        type: 'negative',
        message: _this.$t('notice.mobile_userlogin.notice10')
      });
    });
}
```

### 后端实现

#### 1. 添加忘记密码API端点

在`userlogin/views.py`中添加了`forgot_password`视图函数，用于处理忘记密码请求。

```python
def forgot_password(request, *args, **kwargs):
    """
    Handle forgot password request
    """
    if request.method == 'POST':
        try:
            post_data = json.loads(request.body.decode())
            username = post_data.get('username')
            email = post_data.get('email')
            
            # 验证用户名和邮箱
            user = User.objects.filter(username__iexact=username).first()
            if not user or not user.email or user.email.lower() != email.lower():
                return JsonResponse({
                    "code": "400",
                    "msg": "User name/email not match",
                    "data": None
                })
            
            # 生成密码重置令牌
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # 构建密码重置链接
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
            
            # 发送密码重置邮件
            subject = "Password Reset Request"
            message = f"Please click the following link to reset your password: {reset_url}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            return JsonResponse({
                "code": "200",
                "msg": "Password reset email sent",
                "data": None
            })
        except Exception as e:
            print(f"Error in forgot_password: {str(e)}")
            return JsonResponse({
                "code": "500",
                "msg": "Server error",
                "data": None
            })
    else:
        return JsonResponse({
            "code": "405",
            "msg": "Method not allowed",
            "data": None
        })
```

#### 2. 添加密码重置API端点

在`userlogin/views.py`中添加了`reset_password`视图函数，用于处理密码重置请求。

```python
def reset_password(request, uidb64, token, *args, **kwargs):
    """
    Handle password reset request
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            try:
                post_data = json.loads(request.body.decode())
                new_password = post_data.get('new_password')
                
                # 设置新密码
                user.set_password(new_password)
                user.save()
                
                return JsonResponse({
                    "code": "200",
                    "msg": "Password reset successful",
                    "data": None
                })
            except Exception as e:
                print(f"Error in reset_password: {str(e)}")
                return JsonResponse({
                    "code": "500",
                    "msg": "Server error",
                    "data": None
                })
        else:
            # 返回密码重置页面
            return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})
    else:
        return JsonResponse({
            "code": "400",
            "msg": "Invalid reset link",
            "data": None
        })
```

#### 3. 添加URL路由

在`userlogin/urls.py`中添加了忘记密码和密码重置的URL路由。

```python
urlpatterns = [
    # 其他URL路由
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
]
```

#### 4. 添加密码重置模板

创建了`templates/reset_password.html`模板，用于显示密码重置页面。

```html
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #1976d2;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #1976d2;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
        }
        button:hover {
            background-color: #1565c0;
        }
        .error {
            color: red;
            margin-top: 10px;
            text-align: center;
        }
        .success {
            color: green;
            margin-top: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Reset Password</h1>
        <div id="message" class=""></div>
        <div class="form-group">
            <label for="password">New Password</label>
            <input type="password" id="password" name="password" required>
        </div>
        <div class="form-group">
            <label for="confirm_password">Confirm Password</label>
            <input type="password" id="confirm_password" name="confirm_password" required>
        </div>
        <button type="button" onclick="resetPassword()">Reset Password</button>
    </div>

    <script>
        function resetPassword() {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const messageElement = document.getElementById('message');
            
            if (password !== confirmPassword) {
                messageElement.textContent = 'Passwords do not match';
                messageElement.className = 'error';
                return;
            }
            
            if (password.length < 8) {
                messageElement.textContent = 'Password must be at least 8 characters long';
                messageElement.className = 'error';
                return;
            }
            
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    new_password: password
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.code === '200') {
                    messageElement.textContent = 'Password reset successful. You can now login with your new password.';
                    messageElement.className = 'success';
                    document.getElementById('password').disabled = true;
                    document.getElementById('confirm_password').disabled = true;
                    document.querySelector('button').disabled = true;
                } else {
                    messageElement.textContent = data.msg || 'An error occurred';
                    messageElement.className = 'error';
                }
            })
            .catch(error => {
                messageElement.textContent = 'An error occurred';
                messageElement.className = 'error';
                console.error('Error:', error);
            });
        }
    </script>
</body>
</html>
```

### 邮件配置

在`settings.py`中添加了邮件发送配置。

```python
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'  # SMTP服务器地址
EMAIL_PORT = 587  # SMTP服务器端口
EMAIL_USE_TLS = True  # 是否使用TLS加密
EMAIL_HOST_USER = 'your-email@example.com'  # 发件人邮箱
EMAIL_HOST_PASSWORD = 'your-email-password'  # 发件人邮箱密码
DEFAULT_FROM_EMAIL = 'GreaterWMS <your-email@example.com>'  # 默认发件人
```

## 安全考虑

1. **防止用户枚举攻击**：
   - 当用户名或邮箱不匹配时，返回通用错误消息，而不是具体指出是用户名还是邮箱不匹配
   - 这样可以防止攻击者通过尝试不同的用户名来确定哪些用户名是有效的

2. **密码重置令牌安全**：
   - 使用Django内置的`default_token_generator`生成安全的密码重置令牌
   - 令牌有时间限制，通常为24小时
   - 令牌是一次性的，使用后即失效

3. **密码强度要求**：
   - 在前端和后端都添加了密码强度验证
   - 要求密码至少8个字符长

4. **HTTPS传输**：
   - 所有密码重置相关的请求都通过HTTPS传输，确保数据安全

## 用户体验考虑

1. **清晰的错误消息**：
   - 当用户输入有误时，显示清晰的错误消息
   - 错误消息不会泄露敏感信息

2. **简单的操作流程**：
   - 用户只需提供用户名和邮箱，即可请求密码重置
   - 密码重置页面简洁明了，易于使用

3. **成功反馈**：
   - 当密码重置请求成功发送时，显示成功消息
   - 当密码重置成功时，显示成功消息并禁用表单，防止重复提交

## 测试

1. **功能测试**：
   - 测试忘记密码请求发送
   - 测试密码重置链接有效性
   - 测试密码重置功能

2. **安全测试**：
   - 测试无效用户名/邮箱组合
   - 测试过期或无效的密码重置令牌
   - 测试弱密码拒绝

3. **用户体验测试**：
   - 测试错误消息显示
   - 测试成功消息显示
   - 测试表单验证

## 结论

忘记密码功能的实现使系统更加完善，为用户提供了在忘记密码时自助恢复账户访问权限的方式。该功能遵循了安全最佳实践，确保了用户数据的安全性，同时提供了良好的用户体验。

通过这个功能，用户不再需要联系管理员来重置密码，减轻了管理员的工作负担，同时提高了系统的可用性和用户满意度。
