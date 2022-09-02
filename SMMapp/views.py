from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import loader
from django.template import Context
from django.urls import reverse, reverse_lazy

from django.http import FileResponse, Http404
from django.shortcuts import render,get_object_or_404
from django.views import generic

from django.core.files.base import ContentFile
from django.views.generic.edit import FormView,CreateView,DeleteView,UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.widgets import SelectDateWidget

from django.forms.models import model_to_dict
#from jsignature.widgets import JSignatureWidget
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings

from SMMapp.process import html_to_pdf 
from SMM.common import * 

import json
import io
import re
from datetime import datetime
from collections import OrderedDict
from weasyprint import HTML
from codecs import encode

from SMMapp import views

from SMMapp.models import *
from SMMapp.serializers import *
from SMM.settings import CLIENT_ID
#from SMMapp.forms import *

import uuid
import base64
import requests
import time
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser

from django.views.decorators.cache import never_cache

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
# Create your views here.

#class SubmissionView(LoginRequiredMixin, CreateView):
from rest_framework import permissions

#for pdf generation
#from easy_pdf.views import PDFTemplateView,PDFTemplateResponseMixin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import StringIO, BytesIO
from pdfrw import PdfReader, PdfWriter


class TemplateCreatorPermission(permissions.BasePermission):
    """object lvl permissions for owner """
    def has_object_permission(self, request, view, obj):
        print(obj.creator == request.user)
        return obj.creator == request.user


# allow view ot template only if it's community=true, otherwise it must be the creator
class TemplateCommunityPermission(permissions.BasePermission):
    """object lvl permissions for owner """
    def has_object_permission(self, request, view, obj):
        if not obj.community:
            return (obj.creator == request.user)
        else:
            return True


class SubmissionCreatorPermission(permissions.BasePermission):
    """object lvl permissions for owner """
    def has_object_permission(self, request, view, obj):
        return obj.submitter == request.user


class AttachmentCreationPermission(permissions.BasePermission):
    message = 'You do not have permissions for this action'

    def has_permission(self, request, view):
        submission_id = request.POST.get('submission')
        submission = Submission.objects.filter(id=submission_id).first()
        return submission.submitter == request.user


def check_is_submission_owner(obj,user):
    return obj.submitter == user


def check_is_template_creator(obj,user):
    return obj.creator == user


@api_view(['POST'])
@never_cache
def user_login(request):
    ''' User login '''
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('template'))

    if request.method == 'POST':
            url = "https://api.sandbox-chunwo.mattex.com.hk/login"
            payload = {
                    'email':request.data['email'],#request.POST.get("email"),
                    'password':request.data['password']#request.POST.get("password")
                    }
            headers = {
                  'Origin': 'https://sandbox-chunwo.mattex.com.hk',
                  'Content-Type': 'text/plain'
                }
            email = request.data['email']
            username = email
            password = request.data['password']
            payload = "{\n    \"email\":\"email@mail.com\",\n    \"password\":\"mypassword123\"\n}\n"             
            payload = payload.replace("email@mail.com",email).replace("mypassword123",password)
            r = requests.post(url, data = payload, headers=headers)
            if r.status_code == 200:
                data = r.json()

                # Get user // create one if it doesn't exist yet
                emat_user_id = data['data']['uid']
                user, created = CustomUser.objects.update_or_create(
                    emat_user_id = emat_user_id,
                    defaults = {
                        'username': username,
                        'initials': data['data']['initials'],
                        'email': data['data']['email'],
                        'name': data['data']['name'],
                        'emat_admin': data['data']['admin'],
                        'avatar': data['data']['avatar'],
                    })

                # Login user - @login_required decorator can be used after user has been logged in
                auth_login(request, user)

                request.session['access_token'] = data['data']['access_token']
                request.session['refresh_token'] = data['data']['refresh_token']
                #request.session['token_type'] = data['data']['token_type']
                #request.session['expires_in'] = data['data']['expires_in']

                url2 = f"https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/users/user/smm/{emat_user_id}"
                payload={}
                headers = {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + request.session['access_token']
                }
                r2 = requests.request("GET", url2, headers=headers, data=payload)
                if r2.status_code == 200:
                    data2 = r2.json()
                    user.title = data2['data']['title']
                    user.job_title = data2['data']['job_title']
                    user.status = data2['data']['status']
                    user.emat_status = data2['data']['emat_status']
                    user.signature = data2['data']['signature']
                    user.signature_short = data2['data']['signature_short']
                    user.save()

                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Request failed"}, status=r.status_code)

    else:
        return render(request, 'main/login.html', {})


#@api_view(['GET'])
@login_required
def logout(request):
    #request.session.flush()
    auth_logout(request)
    return HttpResponse("You're logged out.")


@api_view(['GET'])
@login_required
def get_project_list(request):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/projects/smm/project/list/"+str(request.user.emat_user_id)+"/user"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_and_fetch_project_list(request):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/projects/smm/project/list/"+str(request.user.emat_user_id)+"/user"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            for item in data['data']:
                project, created = Project.objects.update_or_create(
                    project_id = item['project_id'],
                    defaults = {
                            'project_code': item['project_code'],
                            'project_name': item['project_name'],
                            'project_display_name': item['project_display_name'],
                            'client': item['client'],
                            'division': item['division'],
                            'status': item['status'],
                            'project_in_charge': item['project_in_charge']
                    })

                #for gettimg extra data about project
                url2 = f"https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/subsidiaries/{item['project_id']}/project"
                payload={}
                headers = {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + request.session['access_token']
                }
                r2 = requests.request("GET", url2, headers=headers, data=payload)
                if r2.status_code == 200:
                    data2 = r2.json()
                    project.primary_name = data2['data']['primary_name']
                    try:
                        project.transaction_type_name = data2['data']['transaction_type_name']
                    except:
                        pass
                    project.chop = data2['data']['chop']
                    project.logo = data2['data']['logo']
                    project.address = data2['data']['address']
                    project.tel = data2['data']['tel']
                    project.status = data2['data']['status']
                    project.save()

                #for getting purpose of submission of this project
                url3 = f"https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/project-settings/submission/purpose/{item['project_id']}"
                r3 = requests.request("GET", url3, headers=headers, data=payload)
                if r3.status_code == 200:
                    data3 = r3.json()
                    for item in data3['purpose']:
                        purpose, created = Purpose.objects.update_or_create(
                            purpose_id = item['id'],
                            defaults = {
                                'name': item['name'],
                                'short_name': item['short_name'],
                                #'project': project
                            })
                        project.purposes.add(purpose)
                    #old method
                    #data3 = r3.json()
                    #project.purpose = data3['purpose']
                
                project.save()

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_and_fetch_project_details(request,project_id):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/projects/smm/project/list/"+str(request.user.emat_user_id)+"/user"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data_to_return = {}
            data = r.json()
            for item in data['data']:
                if str(item['project_id'])==str(project_id): #only save data for this project
                    project, created = Project.objects.update_or_create(
                        project_id = item['project_id'],
                        defaults = {
                                'project_code': item['project_code'],
                                'project_name': item['project_name'],
                                'project_display_name': item['project_display_name'],
                                'client': item['client'],
                                'division': item['division'],
                                'status': item['status'],
                                'project_in_charge': item['project_in_charge']
                        })

                    #for gettimg extra data about project
                    url2 = f"https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/subsidiaries/{item['project_id']}/project"
                    payload={}
                    headers = {
                      'Content-Type': 'application/json',
                      'Authorization': 'Bearer ' + request.session['access_token']
                    }
                    r2 = requests.request("GET", url2, headers=headers, data=payload)
                    if r2.status_code == 200:
                        data2 = r2.json()
                        project.primary_name = data2['data']['primary_name']
                        try:
                            project.transaction_type_name = data2['data']['transaction_type_name']
                        except:
                            pass
                        project.chop = data2['data']['chop']
                        project.logo = data2['data']['logo']
                        project.address = data2['data']['address']
                        project.tel = data2['data']['tel']
                        project.status = data2['data']['status']

                    #for getting purpose of submission of this project
                    url3 = f"https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/project-settings/submission/purpose/{item['project_id']}"
                    r3 = requests.request("GET", url3, headers=headers, data=payload)
                    if r3.status_code == 200:
                        data3 = r3.json()
                        project.purpose = data3['purpose']
                    
                    project.save()
                    return Response(item, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_user_list(request,project_id):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/projects/smm/user/list/"+str(project_id)+"/project"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_and_fetch_user_list(request,project_id):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/projects/smm/user/list/"+str(project_id)+"/project"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            for item in data['data']:
                username = item['email']
                user, created = CustomUser.objects.update_or_create(
                    emat_user_id = item['id'],
                    defaults = {
                        'username': username,
                        'initials': item['initial'],
                        'email': item['email'],
                        'name': item['name'],
                        'title': item['title'],
                        'emat_status': item['status']
                    })
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_user_details(request,user_id):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/setting/api/v1/users/user/smm/"+str(user_id)
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()

            email = data['data']['email']
            username = email
            emat_user_id = data['data']['emat_user_id']
            user, created = CustomUser.objects.update_or_create(
                emat_user_id = emat_user_id,
                defaults = {
                        'username': username,
                        'initials': data['data']['initial'],
                        'email': data['data']['email'],
                        'name': data['data']['name'],
                        #'avatar': data['data']['avatar'],
                        'title': data['data']['title'],
                        'job_title': data['data']['job_title'],
                        'status': data['data']['status'],
                        'emat_status': data['data']['emat_status'],
                        'signature': data['data']['signature'],
                        'signature_short': data['data']['signature_short'],
                })

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_submission_type_list(request):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/document-types/all"
        payload={}
        headers = {
            'Origin': '{{origin}}',
            'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            for item in data['data']:
                sub_type, created = SubmissionType.objects.update_or_create(
                    submission_type_id = item['id'],
                    defaults = {
                        'model_type': item['model_type'],
                        'display_name': item['display_name'],
                        'status': item['status']
                    })

                #now save all approval flows into the db
                url2 = f"https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/flow/{item['id']}/1" 
                payload={}
                headers = {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer ' + request.session['access_token']
                }
                r2 = requests.request("GET", url2, headers=headers, data=payload)
                if r2.status_code == 200:
                    data2 = r2.json()
                    for item in data2['data']:
                        flow, created = ApprovalFlow.objects.update_or_create(
                            approval_flow_id = item['id'],
                            defaults = {
                                'name': item['name'],
                                'step_flow': item['step_flow'],
                                'status': item['status'],
                                'remark': item['remark'],
                                'submission_type': sub_type
                            })

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_trade_list(request):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/trades/for/option"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            for item in data['data']:
                trade, created = Trade.objects.update_or_create(
                    trade_id = item['id'],
                    defaults = {
                        'name': item['name'],
                        'short_form': item['short_form'],
                        'status': item['status']
                    })
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_reviewer_list(request,project_id):
    if request.method == "GET":
        project = Project.objects.filter(project_id=project_id).first()
        if project:
            url = "https://api.sandbox-chunwo.mattex.com.hk/reviewer/api/v1/projects/reviewers"

            dataList = []
            boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
            dataList.append(encode('--' + boundary))
            dataList.append(encode('Content-Disposition: form-data; name=client_id;'))

            dataList.append(encode('Content-Type: {}'.format('text/plain')))
            dataList.append(encode(''))

            dataList.append(encode(str(CLIENT_ID)))
            dataList.append(encode('--' + boundary))
            dataList.append(encode('Content-Disposition: form-data; name=client_project_id;'))

            dataList.append(encode('Content-Type: {}'.format('text/plain')))
            dataList.append(encode(''))

            dataList.append(encode(str(project.pk)))
            dataList.append(encode('--'+boundary+'--'))
            dataList.append(encode(''))
            body = b'\r\n'.join(dataList)
            payload = body
            '''
            payload = {
                'client_id': str(CLIENT_ID),
                'client_project_id': str(project.pk)
            }
            '''
            headers = {
                  'Origin': '{{origin}}',           
                  'Authorization': 'Bearer ' + request.session['access_token'],
                  'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
            }
            #print(payload)
            r = requests.request("GET", url, headers=headers, data=payload, files=[])
            if r.status_code == 200:
                data = r.json()
                for item in data['data']:
                    reviewer, created = Reviewer.objects.update_or_create(
                        reviewer_id = item['reviewer_id'],
                        defaults = {
                            'primary_name': item['reviewer']['primary_name'],
                            'secondary_name': item['reviewer']['secondary_name'],
                            'short_name': item['reviewer']['short_name'],
                            #'project': project
                        })
                    project.reviewers.add(reviewer)
                return Response(data, status=status.HTTP_200_OK)

    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


'''
@api_view(['GET'])
@login_required
def get_approval_flow(request,submission_type_str):
    if submission_type_str=='MAT':
        submission_type = 1
    elif submission_type_str=='MS':
        submission_type = 2
    else:
        return Response({"error": "Submission type not recognized"}, status=status.HTTP_400_BAD_REQUEST)
    #print(submission_type_str)

    if request.method == "GET":
        url = f"https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/flow/{submission_type}/1" #3=document type
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            for item in data['data']:
                flow, created = ApprovalFlow.objects.update_or_create(
                    approval_flow_id = item['id'],
                    defaults = {
                        'name': item['name'],
                        'step_flow': item['step_flow'],
                        'status': item['status'],
                        'remark': item['remark'],
                        'submission_type': submission_type_str
                    })

            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)
'''

@api_view(['PATCH'])
@login_required
def change_submission_ref_no_structure(request,pk):
    if request.method == "PATCH":
        project = Project.objects.get(pk=pk)     
        submissions_under_this_project = Submission.objects.filter(project=project)
        if len(submissions_under_this_project)>0:
            return Response({"error": "This project already has at least one submission, so the submission reference number structure cannot be changed."}, status=status.HTTP_400_BAD_REQUEST)
        if 'submission_ref_no_structure' not in request.data or 'duplication_key' not in request.data:
            return Response({"message": "You must specify both submission_ref_no_structure and duplication_key"}, status=status.HTTP_400_BAD_REQUEST)        
        structure = request.data['submission_ref_no_structure']
        duplication_key = request.data['duplication_key']
        if duplication_key in structure["structure"]:
            if 'field_submission_form' in structure['structure'] and 'field_submission_type' in structure['structure']:
                return Response({"message": "CSF+Submission type pattern (e.g. CSF/MAT) and submission form pattern (e.g. MSF) cannot appear together - please choose either one of the two patterns."})
            project.submission_reference_number_structure = structure
            project.duplication_key = duplication_key
            project.save()
            return Response({"message": "Submission reference number structure changed successfully"})
        else:
            return Response({"error": "The selected duplication key is not present in the submission reference number structure"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Request failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@login_required
def change_title_structure(request,pk):
    if request.method == "PATCH":
        project = Project.objects.get(pk=pk)     
        submissions_under_this_project = Submission.objects.filter(project=project)
        if len(submissions_under_this_project)>0:
            return Response({"error": "This project already has at least one submission, so the title structure cannot be changed."}, status=status.HTTP_400_BAD_REQUEST)
        if 'title_structure' not in request.data:
            return Response({"message": "Title structure is missing"}, status=status.HTTP_400_BAD_REQUEST)        
        structure = request.data['title_structure']
        if structure:
            project.title_structure = structure
            project.save()
            return Response({"message": "Submission title structure changed successfully"})
        else:
            return Response({"error": "Something's wrong"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Request failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def submit_for_approval(request):
    url = 'https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/generic/submit/for/approval'
    if request.method == "POST":
        #system_id = request.POST['system_id']
        #pk = request.POST.get("document_id", 0)
        #submission = Submission.objects.get(pk=pk)      
        system_id = request.data.get("system_id","0")
        submission = Submission.objects.filter(system_id__startswith=system_id).last()      
        system_id = submission.system_id #this is to ensure the last revision is taken, even when the user sends the parent system id in the body of the request
        #pk = submission.pk
        document_id = submission.pk
        is_allowed = check_is_submission_owner(submission,request.user) #decorator doesn't work, so need to check manually
        if not is_allowed:
            return HttpResponseNotAllowed(request.method,{"You do not have permission to perform this action.": "Error"})
        if submission.status==2:
            return HttpResponseNotAllowed(request.method,{"You have already requested approval for this submission.": "Error"})
        elif submission.status==3:
            return HttpResponseNotAllowed(request.method,{"This document has already been submitted.": "Error"})
        elif submission.status==4:
            return HttpResponseNotAllowed(request.method,{"This version of the document has been rejected; please create a new revision in order to request for approval.": "Error"})
        approval_flow_id = submission.approval_flow.pk
        document_id = document_id
        project_id = submission.project.project_id
        revision = submission.rev
        submission_type = submission.submission_type.pk

        payload = {
            'flow_id':str(approval_flow_id),
            'document_type_id':str(submission_type),
            'document_id':str(document_id),
            'project_id':str(project_id),
            'revision':str(revision)
        }
        print(payload)
        headers = {
            'Origin': '{{origin}}',
            'Authorization': 'Bearer ' + request.session['access_token']
        }

        r = requests.request("POST", url, headers=headers, data=payload, files=[])
        if r.status_code == 200:
            submission.status = 2 #now waiting for approval
            submission.save()
            data = r.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            print(r.text)
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        #flow_id=2
        #document_type_id=3
        #document_id=1
        #project_id=1
        #revision=1


@api_view(['POST'])
@login_required
def approve_submission(request):
    url = 'https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/generic/approve/submission'
    if request.method == "POST":
        system_id = request.data.get("system_id","0")
        submission = Submission.objects.filter(system_id__startswith=system_id).last()      
        system_id = submission.system_id #this is to ensure the last revision is taken, even when the user sends the parent system id in the body of the request
        #pk = submission.pk
        if submission.status!=2:
            return HttpResponseNotAllowed(request.method,{"This document has not been submitted yet.": "Error"})
        document_id = submission.pk
        revision = submission.rev
        submission_type = submission.submission_type.pk

        payload = {
            'document_type_id':str(submission_type),
            'document_id':str(document_id),
            'revision':str(revision)
        }
        headers = {
            'Origin': '{{origin}}',
            'Authorization': 'Bearer ' + request.session['access_token']
        }

        r = requests.request("POST", url, headers=headers, data=payload, files=[])
        
        if r.status_code == 200:
            
            #insert signature on cover page
            signoff = SignOff.objects.filter(signoff_id=system_id).first()
            signoff_blocks = signoff.blocks
            new_blocks = []
            for block in signoff_blocks:
                if block["id"] == request.user.emat_user_id:
                    new_value = {'signature': request.user.signature}
                    block.update(new_value)
                new_blocks.append(block)
            signoff.blocks = new_blocks
            signoff.save()

            #now approve if this is the last reviewer
            approval_flow = submission.approval_flow
            step_flow = json.loads(approval_flow.step_flow)
            last_user_id = step_flow[-1]["user"][0]
            if(last_user_id==request.user.emat_user_id): #last user in the step flow, can change status to approved
                submission.status = 3 #now submitted
            submission.save()
            data = r.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            print(r.text)
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def reject_submission(request):
    url = 'https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/generic/reject/submission'
    if request.method == "POST":
        system_id = request.data.get("system_id","0")
        comment = request.data.get("comment","")
        submission = Submission.objects.filter(system_id__startswith=system_id).last()      
        system_id = submission.system_id #this is to ensure the last revision is taken, even when the user sends the parent system id in the body of the request
        if submission.status!=2:
            return HttpResponseNotAllowed(request.method,{"This document has not been submitted yet.": "Error"})
        document_id = submission.pk
        revision = submission.rev
        submission_type = submission.submission_type.pk

        payload = {
            'document_type_id':str(submission_type),
            'document_id':str(document_id),
            'revision':str(revision),
            'note':comment
        }
        headers = {
            'Origin': '{{origin}}',
            'Authorization': 'Bearer ' + request.session['access_token']
        }

        r = requests.request("POST", url, headers=headers, data=payload, files=[])
        if r.status_code == 200:

            #delete all signatures on cover page, apart from the one of the submitter
            signoff = SignOff.objects.filter(signoff_id=system_id).first()
            signoff_blocks = signoff.blocks
            new_blocks = []
            for block in signoff_blocks:
                if block["id"] != submission.submitter.emat_user_id:
                    new_value = {'signature': ''}
                    block.update(new_value)
                new_blocks.append(block)
            signoff.blocks = new_blocks
            signoff.save()

            submission.status = 4 #document has been rejected
            submission.comment = comment #add comment from reviewer
            submission.save()
            data = r.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            print(r.text)
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@login_required
def get_pending_approval_submission(request):
    if request.method == "GET":
        url = "https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/approval-flows/all/pending/approval/submission"
        payload={}
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + request.session['access_token']
        }
        r = requests.request("GET", url, headers=headers, data=payload)
        if r.status_code == 200:
            data = r.json()
            new_data = []
            for item in data['submission_info']:
                submission = Submission.objects.filter(id=item["document_id"]).first()
                new_data.append({
                        "system_id":submission.system_id
                    })
            return Response(new_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def submit_to_srm(request):
    url = 'https://api.sandbox-chunwo.mattex.com.hk/smm-v2/api/v1/submissions/to/srm'
    if request.method == "POST":
        system_id = request.data.get("system_id","0")
        submission = Submission.objects.filter(system_id__startswith=system_id).last()      

        is_allowed = check_is_submission_owner(submission,request.user) #decorator doesn't work, so need to check manually
        if not is_allowed:
            return HttpResponseNotAllowed(request.method,{"You do not have permission to perform this action.": "Error"})
        if submission.status!=3:
            return HttpResponseNotAllowed(request.method,{"This submission did not receive internal approval yet.": "Error"})

        first_submission = Submission.objects.filter(system_id__startswith=system_id).first()

        purpose_id = None 
        for purpose in submission.project.purposes:
            if submission.purpose_chosen.name == purpose.name:
                purpose_id = int(purpose.id)

        payload = {
            'client_id': CLIENT_ID,
            'emat_reviewer_id': submission.target_recipient,
            'client_model_type': submission.submission_type.model_type,
            'client_model_id': first_submission.pk,
            'client_project_id': submission.project.pk,
            'client_version': submission.rev,
            'client_external_version': submission.ext_rev,
            'client_submission_id': submission.pk,
            'submission_no_ref': submission.system_id,
            'name': SUBMISSION_NAME, #???
            'purpose_id': purpose_ID,
            'submitted_by': request.user.emat_user_id,
            'submitted_by_name': request.user.name,
            'final_package': '???', #???
            'submission_cover_page': 'BASE64STRING' #???
        }
        headers = {
            'Origin': '{{origin}}',
            'Authorization': 'Bearer ' + request.session['access_token']
        }

        r = requests.request("POST", url, headers=headers, data=payload, files=[])
        if r.status_code == 200:
            return Response(data, status=status.HTTP_200_OK)
        else:
            print(r.text)
            return Response({"error": "Request failed"}, status=r.status_code)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PATCH'])
@login_required
@permission_classes([TemplateCreatorPermission])
def change_template_status(request,pk):
    if request.method == "PATCH":
        template = Template.objects.get(id=pk)      
        is_allowed = check_is_template_creator(template,request.user) #decorator doesn't work, so need to check manually
        if not is_allowed:
            #return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_400_BAD_REQUEST)
            return HttpResponseNotAllowed(request.method,{"You do not have permission to perform this action.": "Error"})
        new_status = int(request.data['status'])
        if new_status==2:
            try:
                if template.header_template and template.salutation_template and template.title_template and template.attachment_template and template.aboutthissubmission_template:
                    template.status = new_status
                    template.save()
                    return Response({"message": "Template successfully activated"})
                else:
                    return Response({"error": "Some mandatory blocks are missing in the template. In order to activate it, please include all mandatory sections."}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": "Some mandatory blocks are missing in the template. In order to activate it, please include all mandatory sections."}, status=status.HTTP_400_BAD_REQUEST)
        elif new_status==1 or new_status==3:
            template.status = new_status
            template.save()
            response = [model_to_dict(template)]
            return Response({"message": "Template status changed successfully"})
        else:
            return Response({"error": "Not a valid status. Valid status are: 1,2,3"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Request failed"}, status=status.HTTP_400_BAD_REQUEST)



class TemplateView(LoginRequiredMixin,generics.CreateAPIView):
    model = Template
    serializer_class = TemplateSerializer
    fields = '__all__'
    success_url = reverse_lazy('project-list')

    def get_serializer_context(self):
        context = super(TemplateView, self).get_serializer_context()
        #project_id = self.kwargs['project_id']
        #context.update({"project_id": project_id})
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Template info'})
        return context


class TemplateDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = Template
    serializer_class = TemplateSerializer
    permission_classes = (TemplateCommunityPermission,)
    #template_name = "submission_detail.html"
    fields = '__all__'
    #queryset = self.get_queryset()

    def get_queryset(self):
        template = Template.objects.filter(id=self.kwargs.get('pk'))
        return template

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TemplateListView(LoginRequiredMixin,generics.ListAPIView):
    model = Template
    serializer_class = TemplateListSerializer

    def get_queryset(self):
        user = self.request.user
        #queryset = Template.objects.all()
        queryset = Template.objects.filter(Q(community=True) | (Q(community=False) & Q(creator=user)))
        if 'project_id' in self.request.GET:
            project_id = self.request.GET['project_id']
            projects = Project.objects.filter(project_id=str(project_id))
            if len(projects):
                project = projects[0]
                queryset = queryset.filter(project=project)
                #return Template.objects.filter(project=project)
            #else:
            #    return Template.objects.none()
        if 'submission_type' in self.request.GET:
            try:
                submission_type = int(self.request.GET['submission_type'])
            except:
                submission_type = 0
            queryset = queryset.filter(submission_type__submission_types__contains=submission_type)

        if 'status' in self.request.GET:
            status = self.request.GET['status']
            try:
                queryset = queryset.filter(status=int(status))
            except:
                queryset = []

        return queryset
        #return Template.objects.all()


class TemplateUpdateView(LoginRequiredMixin,generics.UpdateAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = (TemplateCreatorPermission,)
    lookup_field = 'pk'

    #def get_queryset(self):
    #    queryset = super(TemplateUpdateView, self).get_queryset()
    #    return queryset.filter(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Template updated successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class SubmissionView(LoginRequiredMixin,generics.CreateAPIView):
    model = Submission
    serializer_class = SubmissionSerializer
    fields = '__all__'
    success_url = reverse_lazy('project-list')

    def create(self, request, *args, **kwargs):
        approval_flow_id = request.data['approval_flow']
        submission_type_id = request.data['submission_type']
        target_recipient_id = request.data['target_recipient']
        purpose_id = None
        try:
            purpose_id = request.data['aboutthissubmission_submission.purpose_chosen']
        except:
            purpose_id = request.data['aboutthissubmission_submission']['purpose_chosen']
        project_id = request.data['project']
        document_number = request.data['document_number']
        discipline_code = request.data['discipline_code']

        #check that the reviewer chosen and the chosen purpose of submission are included in this project
        project = Project.objects.filter(project_id=project_id).first()
        if project: 
            if not project.reviewers.filter(pk=target_recipient_id).exists():
                return Response("The reviewer chosen is not included in this project.", status=400)
            if not project.purposes.filter(pk=purpose_id).exists():
                return Response("The chosen purpose of submission is not included in this project.", status=400)
        else:
            return Response("Please select a valid project.", status=400)

        #check that there is no other document with same document_number under the same project according to the criterium selected (duplication_key)
        duplication_key = project.duplication_key
        if not duplication_key:
            return Response("This project does not have a valid de-duplication key.", status=400)
        else:
            submissions = Submission.objects.filter(project=project) #first select all previous submission under this project
            if duplication_key=='field_project_id':
                pass
            elif duplication_key=='field_submission_type':
                submission_type = SubmissionType.objects.filter(submission_type_id=submission_type_id)
                submissions = submissions.filter(submission_type=submission_type)               
            elif duplication_key=='field_discipline_code':
                submissions = submissions.filter(discipline_code=discipline_code)
            elif duplication_key=='field_year':
                submissions = submissions.filter(year=date.today().year)
            submissions = submissions.filter(document_number=document_number)
            if len(submissions)>0:
                return Response("Another submission with same document number exists under this project for the duplication criterium chosen, please input a different value", status=400)

        #check that the submission type chosen is compatible with the selected approval flow
        approval_flow = ApprovalFlow.objects.filter(approval_flow_id=approval_flow_id).first()
        if approval_flow: 
            if approval_flow.submission_type.pk == int(submission_type_id):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(serializer.data, status=201)
            else:
                return Response("The selected approval flow is not available for the selected submission type.", status=400)
        else:
            return Response("Please select a valid approval flow for this submission", status=400)



    def get_serializer_context(self):
        #template_id = self.kwargs['id']
        context = super(SubmissionView, self).get_serializer_context()
        #context.update({"template_id": template_id})
        return context    


class SubmissionDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = Submission
    serializer_class = SubmissionSerializer
    #permission_classes = (SubmissionCreatorPermission,)
    lookup_field = 'system_id'

    def get_queryset(self):
        submission = Submission.objects.filter(system_id=self.kwargs.get('system_id'))
        return submission

    #def get_object(self):
    #    submission = Submission.objects.get(system_id=self.kwargs.get('system_id'))
    #    return submission

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SubmissionListView(LoginRequiredMixin,generics.ListAPIView):
    model = Submission
    serializer_class = SubmissionListSerializer

    def get_queryset(self):
        #queryset = Submission.objects.all()
        user = self.request.user
        queryset = Submission.objects.filter(Q(submitter=user))
        if 'project_id' in self.request.GET:
            project_id = self.request.GET['project_id']
            projects = Project.objects.filter(project_id=str(project_id))
            if len(projects):
                project = projects[0]
                queryset = queryset.filter(project=project)
        if 'submission_type' in self.request.GET:
            submission_type = self.request.GET['submission_type']
            queryset = queryset.filter(submission_type=submission_type)
        return queryset


class SubmissionUpdateView(LoginRequiredMixin,generics.UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (SubmissionCreatorPermission,)
    lookup_field = 'system_id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status!=1:
            return HttpResponseNotAllowed(request.method,{"This submission has been either submitted or rejected so cannot be modified.": "Error"})

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Submission updated successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class SubmissionRevView(LoginRequiredMixin,generics.CreateAPIView):
    model = Submission
    serializer_class = SubmissionRevSerializer
    fields = '__all__'
    success_url = reverse_lazy('project-list')

    def create(self, request, *args, **kwargs):
        system_id = self.kwargs.get('system_id')
        submission = Submission.objects.filter(system_id=system_id).first()
        if submission.submitter == request.user:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        else:
            return Response("You do not have permission for this action.", status=403)

    def get_serializer_context(self):
        system_id = self.kwargs.get('system_id')
        context = super(SubmissionRevView, self).get_serializer_context()
        context.update({"system_id": system_id})
        return context    

    def form_valid(self, form):
        return JsonResponse(form.data, status=200, safe=False) 

 
class SubmissionRevListView(LoginRequiredMixin,generics.ListAPIView):
    model = Submission
    serializer_class = SubmissionRevListSerializer

    def get_queryset(self):
        system_id = self.kwargs.get('system_id')
        queryset = Submission.objects.filter(system_id__startswith=system_id)
        return queryset


#class SubmissionDeleteView(LoginRequiredMixin,DeleteView):
#    model = Submission
#    success_url = reverse_lazy('submission-list')


class LibraryView(LoginRequiredMixin,generics.CreateAPIView):
    model = NameValuePair
    serializer_class = NamevaluepairSerializer
    fields = '__all__'
    #template_name = 'submission.html'
    success_url = reverse_lazy('submission-list')

    def get_serializer_context(self):
        context = super(LibraryView, self).get_serializer_context()
        return context    

    def form_valid(self, form):
        return JsonResponse(form.data, status=200, safe=False) 


class LibraryListView(LoginRequiredMixin,generics.ListAPIView):
    model = NameValuePair
    serializer_class = NamevaluepairSerializer

    def get_queryset(self):
        #print(self.kwargs)
        if 'contains' in self.request.GET:
            contains = self.request.GET['contains']
            return NameValuePair.objects.filter(name__icontains=contains)
        elif 'startswith' in self.request.GET:
            startswith = self.request.GET['startswith']
            return NameValuePair.objects.filter(name__istartswith=startswith)

        return NameValuePair.objects.all()


class AttachmentFileView(LoginRequiredMixin,generics.CreateAPIView):
    model = AttachmentFile
    serializer_class = AttachmentFileSerializer
    #permission_classes = (AttachmentCreationPermission,)
    fields = '__all__'

    def create(self, request, *args, **kwargs):
        submission_id = request.POST.get('submission')
        submission = Submission.objects.filter(id=submission_id).first()
        if submission.submitter == request.user:
            if not submission.attachment_submission.attachment:
                return Response("This submission cannot include attachments.", status=400)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        else:
            return Response("You do not have permission for this action.", status=403)

    def get_serializer_context(self):
        context = super(AttachmentFileView, self).get_serializer_context()
        return context    

    def form_valid(self, form):
        return JsonResponse(form.data, status=200, safe=False) 


class AttachmentFileListView(LoginRequiredMixin,generics.ListAPIView):
    model = AttachmentFile
    serializer_class = AttachmentFileSerializer

    def get_queryset(self):
        queryset = []
        if 'submission' in self.request.GET:
            system_id = self.request.GET['submission']
            try:
                submission = Submission.objects.get(system_id=system_id)
                queryset = AttachmentFile.objects.filter(submission=submission)
                return queryset
            except:
                return queryset

        return queryset #return no files if no submission specified


class AttachmentDeleteView(LoginRequiredMixin,generics.DestroyAPIView):
    model = AttachmentFile
    serializer_class = AttachmentFileSerializer

    def get_queryset(self):
        attachment = AttachmentFile.objects.filter(id=self.kwargs.get('pk'))
        return attachment

    def destroy(self, request, *args, **kwargs):
        attachment = AttachmentFile.objects.filter(id=self.kwargs['pk']).first()
        submitter = attachment.submission.submitter
        if submitter == request.user:
            return super(AttachmentDeleteView, self).destroy(request, *args, **kwargs)
        else:
            return Response("You do not have permission for this action.", status=403)


class ReplyUpdateView(LoginRequiredMixin,generics.UpdateAPIView):
    #queryset = FutureReply.objects.all()
    serializer_class = FutureReplySubSerializer
    #permission_classes = (SubmissionCreatorPermission,)
    #lookup_field = 'futurereply_id'

    def get_serializer_context(self):
        context = super(ReplyUpdateView, self).get_serializer_context()
        system_id = self.kwargs['system_id']
        context.update({"system_id": system_id})
        return context

    def get_object(self):
        #queryset = self.filter_queryset(self.get_queryset())
        # make sure to catch 404's below
        queryset = FutureReply.objects.all()
        obj = queryset.get(futurereply_id=self.kwargs['system_id'])
        #self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        submission = Submission.objects.get(system_id=instance.pk)
        if not request.user == submission.submitter:
            signature = request.user.signature
            instance.signature = signature
            instance.name = request.user.name
        else:
            instance.signature = None
            instance.name = ""
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "reply submitted successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class SubmissionTypeListView(LoginRequiredMixin,generics.ListAPIView):
    model = SubmissionType
    serializer_class = SubmissionTypeSerializer

    def get_queryset(self):
        queryset = SubmissionType.objects.all()
        return queryset


class SubmissionTypeDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = SubmissionType
    serializer_class = SubmissionTypeSerializer
    fields = '__all__'

    def get_queryset(self):
        submission_type = SubmissionType.objects.filter(submission_type_id=self.kwargs.get('pk'))
        return submission_type

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ApprovalFlowListView(LoginRequiredMixin,generics.ListAPIView):
    model = ApprovalFlow
    serializer_class = ApprovalFlowSerializer

    def get_queryset(self):
        queryset = ApprovalFlow.objects.all()
        if 'submission_type' in self.request.GET:
            submission_type = self.request.GET['submission_type']
            queryset = queryset.filter(submission_type=submission_type)
        return queryset


class ApprovalFlowDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = ApprovalFlow
    serializer_class = ApprovalFlowSerializer
    fields = '__all__'

    def get_queryset(self):
        approval_flow = ApprovalFlow.objects.filter(approval_flow_id=self.kwargs.get('pk'))
        return approval_flow

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TradeListView(LoginRequiredMixin,generics.ListAPIView):
    model = Trade
    serializer_class = TradeSerializer

    def get_queryset(self):
        queryset = Trade.objects.all()
        return queryset


class TradeDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = Trade
    serializer_class = TradeSerializer
    fields = '__all__'

    def get_queryset(self):
        trade = Trade.objects.filter(trade_id=self.kwargs.get('pk'))
        return trade

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ReviewerListView(LoginRequiredMixin,generics.ListAPIView):
    model = Reviewer
    serializer_class = ReviewerSerializer

    def get_queryset(self):
        queryset = Reviewer.objects.all()
        return queryset


class ReviewerDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = Reviewer
    serializer_class = ReviewerSerializer
    fields = '__all__'

    def get_queryset(self):
        reviewer = Reviewer.objects.filter(reviewer_id=self.kwargs.get('pk'))
        return reviewer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProjectListView(LoginRequiredMixin,generics.ListAPIView):
    model = Project
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        return queryset


class ProjectDetailView(LoginRequiredMixin,generics.RetrieveAPIView):

    model = Project
    serializer_class = ProjectSerializer
    fields = '__all__'

    def get_queryset(self):
        project = Project.objects.filter(project_id=self.kwargs.get('pk'))
        return project

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # here the object is retrieved
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


#Functions to create merged pdf
def merger(inputs, output):
    o = open(output, "wb+")
    writer = PdfWriter()
    for inpfn in inputs:
        writer.addpages(PdfReader(inpfn).pages)
    writer.write(o.name)
    o.close()
    return 

def handle_uploaded_file(f, output_name):
    with open(output_name, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path


#to write pdf: https://stackoverflow.com/questions/2899807/using-pisa-to-write-a-pdf-to-disk
#@permission_classes([SubmissionCreatorPermission]) #not working for unknown reason
#to merge pdfs: https://stackoverflow.com/questions/38987854/django-and-weasyprint-merge-pdf
@api_view(['GET'])
@login_required
def render_pdf_view(request,system_id):
    template_path = 'generatepdf.html'
    #submission = get_object_or_404(Submission,system_id)
    client_logo_1_url = None
    client_logo_2_url = None
    client_logo_3_url = None
    contractor_logo_1_url = None
    submission = Submission.objects.get(system_id=system_id) 
    #is_allowed = check_is_submission_owner(submission,request.user) #decorator doesn't work, so need to check manually
    #if not is_allowed:
    #    return HttpResponseNotAllowed(request.method,{"You do not have permission to perform this action.": "Error"})
    #submission_type_verbose = submission.get_submission_type_display()   
    submission_type_verbose = submission.submission_type.display_name
    contractor_logo = ''
    if submission.header_submission:
        if submission.header_submission.client_logo_1:
            client_logo_1_url = submission.header_submission.client_logo_1.url.replace('/media','media')
        if submission.header_submission.client_logo_2:
            client_logo_2_url = submission.header_submission.client_logo_2.url.replace('/media','media')
        if submission.header_submission.client_logo_3:
            client_logo_3_url = submission.header_submission.client_logo_3.url.replace('/media','media')
        if submission.header_submission.contractor_logo_1:
            #contractor_logo_1_url = submission.header_submission.contractor_logo_1.url.replace('/media','media')
            contractor_logo = submission.header_submission.contractor_logo_1.replace('data:image/png;base64,','')

    empty_checkbox_url = 'static/images/empty-checkbox.png'
    full_checkbox_url = 'static/images/full-checkbox.png'

    #this part is to display the blocks in the correct order inside the html template
    try:
        order_of_blocks = submission.order_of_blocks
        sorted_order_of_blocks = dict(sorted(order_of_blocks.items()))
        sorted_blocks = []
        for key,value in sorted_order_of_blocks.items():
            sorted_blocks.append(value)
            #sorted_blocks.append(model_to_dict(getattr(submission,value+'_submission')))
    except:
        sorted_blocks = ["header","salutation","title","aboutthissubmission"]

    try:
        order_of_fields = submission.header_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        header_sorted_fields = []
        for key,value in sorted_order_of_fields.items():
            header_sorted_fields.append(value)
    except:
        header_sorted_fields = ["client_logo","project_name","contractor_logo"]

    try:
        order_of_fields = submission.salutation_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        salutation_sorted_fields = []
        for key,value in sorted_order_of_fields.items():
            salutation_sorted_fields.append(value)
            #salutation_sorted_fields[value] = getattr(submission.salutation_submission,value)
    except:
        salutation_sorted_fields = ["to","attn"]

    try:
        order_of_fields = submission.title_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        title_sorted_fields = []
        for key,value in sorted_order_of_fields.items():
            title_sorted_fields.append(value)
    except:
        title_sorted_fields = ["title","submission_ref_no","free_text_field"]

    try:
        title_free_text_fields = submission.title_submission.free_text_fields
        sorted_order_of_fields = dict(sorted(title_free_text_fields.items()))
        temp_list = []
        for field in sorted_order_of_fields.items():
            temp_list.append((list(field[1].items())[0][0],list(field[1].items())[0][1]))
        title_free_text_sorted_fields = OrderedDict(temp_list)
    except:
        title_free_text_sorted_fields = {}


    '''
    try:
        order_of_fields = submission.reference_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        temp_list = []
        for key,value in sorted_order_of_fields.items():
            temp_list.append((value,submission.reference_submission.reference[value]))
        reference_sorted_fields = OrderedDict(temp_list)
    except:
        reference_sorted_fields = {}#[]

    try:
        order_of_fields = submission.descriptionofcontent_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        temp_list = []
        for key,value in sorted_order_of_fields.items():
            temp_list.append((value,submission.descriptionofcontent_submission.description_of_content[value]))
        descriptionofcontent_sorted_fields = OrderedDict(temp_list)
    except:
        descriptionofcontent_sorted_fields = {}#[]

    '''
    try:
        reference = submission.reference_submission.reference
        sorted_order_of_fields = dict(sorted(reference.items()))
        temp_list = []
        for field in sorted_order_of_fields.items():
            temp_list.append((list(field[1].items())[0][0],list(field[1].items())[0][1]))
        reference_sorted_fields = OrderedDict(temp_list)
    except:
        reference_sorted_fields = {}

    try:
        description_of_content = submission.descriptionofcontent_submission.description_of_content
        sorted_order_of_fields = dict(sorted(description_of_content.items()))
        temp_list = []
        for field in sorted_order_of_fields.items():
            temp_list.append((list(field[1].items())[0][0],list(field[1].items())[0][1]))
        descriptionofcontent_sorted_fields = OrderedDict(temp_list)
    except:
        descriptionofcontent_sorted_fields = {}


    try:
        order_of_fields = submission.aboutthissubmission_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        aboutthissubmission_sorted_fields = []
        for key,value in sorted_order_of_fields.items():
            aboutthissubmission_sorted_fields.append(value)
    except:
        aboutthissubmission_sorted_fields = ["purpose_of_submission","anticipated_date_of_reply","remarks"]

    try:
        order_of_fields = submission.attachment_submission.order_of_fields
        sorted_order_of_fields = dict(sorted(order_of_fields.items()))
        attachment_sorted_fields = []
        for key,value in sorted_order_of_fields.items():
            attachment_sorted_fields.append(value)
    except:
        attachment_sorted_fields = []

    try:
        record_reply = submission.aboutthissubmission_submission.record_reply
        if record_reply:
            order_of_fields = submission.futurereply_submission.order_of_fields
            sorted_order_of_fields = dict(sorted(order_of_fields.items()))
            futurereply_sorted_fields = []
            for key,value in sorted_order_of_fields.items():
                futurereply_sorted_fields.append(value)
        else:
            futurereply_sorted_fields = []
    except:
        futurereply_sorted_fields = ["reply","free_text","name","signature","date"]

    #signature = request.user.signature
    submission_serializer = SubmissionSerializer(submission).data    
    context = {'submission': submission,
                'client_logo_1_url': client_logo_1_url,
                'client_logo_2_url': client_logo_2_url,
                'client_logo_3_url': client_logo_3_url,
                #'contractor_logo_1_url': contractor_logo_1_url,
                'contractor_logo': contractor_logo,
                'submission_type_verbose': submission_type_verbose,
                'sorted_blocks': sorted_blocks,
                'header_sorted_fields': header_sorted_fields,
                'salutation_sorted_fields': salutation_sorted_fields,
                'title_sorted_fields': title_sorted_fields,
                'title_free_text_sorted_fields': title_free_text_sorted_fields,
                'reference_sorted_fields': reference_sorted_fields,
                'descriptionofcontent_sorted_fields': descriptionofcontent_sorted_fields,
                'aboutthissubmission_sorted_fields': aboutthissubmission_sorted_fields,
                'attachment_sorted_fields': attachment_sorted_fields,
                'futurereply_sorted_fields': futurereply_sorted_fields,
                'empty_checkbox_url': empty_checkbox_url,
                'full_checkbox_url': full_checkbox_url}
    #submission_dict = model_to_dict(submission)
    #context = {'submission': submission_dict}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cover-page.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create pdf of submission form (attachments not included)
    pisa_status = pisa.CreatePDF(html, dest=response) #link_callback=link_callback
    # open pdf in browser
    #if pisa_status.err: 
    #    return HttpResponse(status=404)
    #return response

    #save pdf of the submission form (without attachments) first
    #filename = CWKLJV-997-CSF-MAT-232323-2022.pdf
    #filename2 = submission.circulation_identification.replace('-','') + '-' + submission.project.project_code + '-' + str(submission.document_date.replace('-','')) 
    #print(filename2)
    filename = settings.MEDIA_URL + 'images/' + str(system_id) + '.pdf'
    if filename[0] == '/':
        filename = filename[1:]
    with open(filename, 'wb+') as output:
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)

        #pdf = PDF(request.POST, request.FILES)
        #if successfull, merge with attachments:
        if pdf:
            file_list = [filename] #main file
            #f1 = filename #main file
            attachments = submission.attached_files.all()
            for attachment in attachments:
                if attachment.include_in_cover_page:
                    attachment_name = attachment.file.url
                    if attachment_name[0] == '/':
                        attachment_name = attachment_name[1:]
                    file_list.append(attachment_name)

            output = filename.replace('.pdf','') + "_with_attachments.pdf"
            out = merger(file_list, output)

            #save file to google cloud storage
            #blob_url = upload_to_bucket('document/submissions/testfile2', filename, 'sandbox-local-developer')
            
            return FileResponse(open(output, 'rb'), content_type='application/pdf')

            #return render(request, "merger/index.html", {"form": pdf, "out": out.name})        

    #else return error
    return HttpResponse(status=404)
 

'''
class SubmissionHistoryView(LoginRequiredMixin,generics.ListAPIView):
    #model = Submission
    serializer_class = SubmissionSerializer
    #permission_classes = (TemplateCommunityPermission,)
    #template_name = "submission_detail.html"
    fields = '__all__'
    #queryset = self.get_queryset()

    def get_queryset(self):
        submission = Submission.objects.filter(system_id=self.kwargs.get('system_id')).first()
        submission_list = []
        for record in submission.history.all():
            submission_list.append(model_to_dict(record.instance))
        return submission_list
'''

@api_view(['GET'])
@login_required
def get_history(request,system_id):
    if request.method == "GET":
        submission = Submission.objects.filter(system_id=system_id).first()
        submission_list = []
        for record in submission.history.all():
            submission_list.append(model_to_dict(record.instance))
            print(record.instance)
        if submission:
            return JsonResponse(submission_list, safe=False)
    else:
        return Response({"error": "Method not allowed"}, status=status.HTTP_400_BAD_REQUEST)


