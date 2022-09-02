"""SMM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from SMMapp.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", views.user_login, name="login"),
    path("logout/", views.logout, name="logout"),
    
    path("get-project-list/", views.get_project_list, name="get-project-list"),
    path("get-and-fetch-project-list/", views.get_and_fetch_project_list, name="get-and-fetch-project-list"),
    path("project-list/", views.ProjectListView.as_view(), name="project-list"),
    path('get-and-fetch-project-details/<str:project_id>/', views.get_and_fetch_project_details, name='get-and-fetch-project-details'),
    path('project-details/<int:pk>/', ProjectDetailView.as_view(), name='project-details'),

    path("get-user-list/<str:project_id>/", views.get_user_list, name="user-list"),
    path("get-and-fetch-user-list/<str:project_id>/", views.get_and_fetch_user_list, name="fetch-user-list"),
    path("get-user-details/<str:user_id>/", views.get_user_details, name="user-details"),

    path("change-submission-ref-no-structure/<int:pk>/", views.change_submission_ref_no_structure, name="change-submission-ref-no-structure"),
    path("change-title-structure/<int:pk>/", views.change_title_structure, name="change-title-structure"),

    path("get-submission-type-list/", views.get_submission_type_list, name="get-submission-types"),
    path("submission-type-list/", views.SubmissionTypeListView.as_view(), name="submission-type-list"),
    path('submission-type/<int:pk>/', SubmissionTypeDetailView.as_view(), name='submission-type-detail'),

    #path("get-approval-flow/<str:submission_type_str>", views.get_approval_flow, name="approval-flow"),
    path("approval-flow-list/", views.ApprovalFlowListView.as_view(), name="approval-flow-list"),
    path('approval-flow/<int:pk>/', ApprovalFlowDetailView.as_view(), name='approval-flow-detail'),

    path("get-trade-list/", views.get_trade_list, name="get-trade-list"),
    path("trade-list/", views.TradeListView.as_view(), name="trade-list"),
    path("trade-detail/<int:pk>/", views.TradeDetailView.as_view(), name="trade-detail"),

    path("get-reviewer-list/<int:project_id>", views.get_reviewer_list, name="get-reviewer-list"),
    path("reviewer-list/", views.ReviewerListView.as_view(), name="reviewer-list"),
    path("reviewer-detail/<int:pk>/", views.ReviewerDetailView.as_view(), name="reviewer-detail"),

    path('template/', views.TemplateView.as_view(), name='template'), 
    path('template-list/', views.TemplateListView.as_view(), name='template-list'), 
    path('template-detail/<int:pk>/', TemplateDetailView.as_view(), name='template-detail'),
    path('template-update/<int:pk>/', TemplateUpdateView.as_view(), name='template-update'),

    path("change-template-status/<int:pk>/", views.change_template_status, name="change-template-status"),

    path('submission/', views.SubmissionView.as_view(), name='submission'), 
    path('submission-list/', views.SubmissionListView.as_view(), name='submission-list'), 
    path('submission-detail/<str:system_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('submission-update/<str:system_id>/', SubmissionUpdateView.as_view(), name='submission-update'),

    path('submission-rev/<str:system_id>/', SubmissionRevView.as_view(), name='submission-rev'),
    path('submission-rev-list/<str:system_id>/', SubmissionRevListView.as_view(), name='submission-rev-list'),

    path("submit-for-approval/", views.submit_for_approval, name="submit-for-approval"),
    path("approve-submission/", views.approve_submission, name="approve-submission"),
    path("reject-submission/", views.reject_submission, name="reject-submission"),
    path("get-pending-approval-submission/", views.get_pending_approval_submission, name="get-pending-approval-submission"),

    path('library/', views.LibraryView.as_view(), name='library'), 
    path('library-list/', views.LibraryListView.as_view(), name='library-list'), 

    path('attachment/', views.AttachmentFileView.as_view(), name='attachment'), 
    path('attachment-list/', views.AttachmentFileListView.as_view(), name='attachment-list'), 
    path('attachment-delete/<int:pk>', views.AttachmentDeleteView.as_view(), name='attachment-delete'), 

    path('reply/<str:system_id>', views.ReplyUpdateView.as_view(), name='reply'), 

    path('pdf/<str:system_id>', render_pdf_view, name='pdf'),
    #path("history/<str:system_id>", views.SubmissionHistoryView.as_view(), name="history"),
    #path("history/<str:system_id>", views.get_history, name="history"),
    #path('comment/', views.CommentView.as_view(), name='comment'), 

    #path('signoff/', views.SignOffView.as_view(), name='signoff'), 
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


'''
    path('header/<str:template_id>/', views.HeaderTemplateView.as_view(), name='header'), 
    path('salutation/<str:template_id>/', views.SalutationTemplateView.as_view(), name='salutation'), 
    path('title/<str:template_id>/', views.TitleTemplateView.as_view(), name='title'), 
    path('reference/<str:template_id>/', views.ReferenceTemplateView.as_view(), name='reference'), 
    path('attachment/<str:template_id>/', views.AttachmentTemplateView.as_view(), name='attachment'), 
    path('descriptionofcontent/<str:template_id>/', views.DescriptionOfContentTemplateView.as_view(), name='descriptionofcontent'), 
    path('aboutthissubmission/<str:template_id>/', views.AboutThisSubmissionTemplateView.as_view(), name='aboutthissubmission'), 
'''
