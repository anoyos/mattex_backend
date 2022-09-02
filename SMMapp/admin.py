from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields=('system_id','document_date','status')

admin.site.register(CustomUser)

#@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    readonly_fields=('creator',)
admin.site.register(Template,TemplateAdmin)
admin.site.register(NameValuePair)
admin.site.register(Header)
admin.site.register(SignOff)
admin.site.register(Project)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    readonly_fields=('template',)


@admin.register(AttachmentFile)
class AttachmentFileAdmin(admin.ModelAdmin):
    readonly_fields=('submission',)


