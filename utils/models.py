from django.db import models

class SystemSettings(models.Model):
    """
    存储系统设置的模型
    """
    key = models.CharField(max_length=100, unique=True, verbose_name="设置键名")
    value = models.TextField(verbose_name="设置值")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'system_settings'
        verbose_name = '系统设置'
        verbose_name_plural = "系统设置"
        ordering = ['key']

    def __str__(self):
        return f"{self.key}: {self.value}"
