from rest_framework import serializers
from django.forms.models import model_to_dict
from drf_writable_nested.serializers import WritableNestedModelSerializer

from SMMapp.models import *

import uuid
import base64
import json
from collections import OrderedDict

from datetime import date


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = '__all__'
        read_only_fields = ['contract_no','project_name','template', 'contractor_logo_1']


class SalutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salutation
        fields = '__all__'
        read_only_fields = ['template']


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ['template']



class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'
        read_only_fields = ['template']



class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['template','attachment']




class DescriptionOfContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptionOfContent
        fields = '__all__'
        read_only_fields = ['template']



class AboutThisSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutThisSubmission
        fields = '__all__'
        read_only_fields = ['template','purpose_of_submission','anticipated_date_of_reply','record_reply']



class FutureReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = FutureReply
        fields = '__all__'
        read_only_fields = ['template','reply','free_text','name','signature','date']


class TemplateListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False, source='get_status_display')
    class Meta:
        model = Template
        fields = ('id','name','status','submission_type','project','status')


class TemplateSerializer(WritableNestedModelSerializer):
    status = serializers.CharField(read_only=True)#, source='get_status_display')
    header_template = HeaderSerializer(required=False, allow_null=True)
    salutation_template = SalutationSerializer(required=False, allow_null=True)
    title_template = TitleSerializer(required=False, allow_null=True)
    reference_template = ReferenceSerializer(required=False, allow_null=True)
    attachment_template = AttachmentSerializer(required=False, allow_null=True)
    descriptionofcontent_template = DescriptionOfContentSerializer(required=False, allow_null=True)
    aboutthissubmission_template = AboutThisSubmissionSerializer(required=False, allow_null=True)
    futurereply_template = FutureReplySerializer(required=False, allow_null=True)

    class Meta:
        model = Template
        #depth = 1
        fields = '__all__'
        read_only_fields = ['status']
        extra_fields = ['header_template','salutation_template',
                        'title_template','reference_template',
                        'attachment_template','descriptionofcontent_template',
                        'aboutthissubmission_template','futurereply_template']

    def create(self, validated_data):
        creator =  self.context['request'].user

        header_data = None
        salutation_data = None
        title_data = None
        reference_data = None
        attachment_data = None
        descriptionofcontent_data = None
        aboutthissubmission_data = None
        futurereply_data = None
        if 'header_template' in validated_data:
            header_data = validated_data.pop('header_template')
        if 'salutation_template' in validated_data:
            salutation_data = validated_data.pop('salutation_template')
        if 'title_template' in validated_data:
            title_data = validated_data.pop('title_template')
        if 'reference_template' in validated_data:
            reference_data = validated_data.pop('reference_template')
        if 'attachment_template' in validated_data:
            attachment_data = validated_data.pop('attachment_template')
        if 'descriptionofcontent_template' in validated_data:
            descriptionofcontent_data = validated_data.pop('descriptionofcontent_template')
        if 'aboutthissubmission_template' in validated_data:
            aboutthissubmission_data = validated_data.pop('aboutthissubmission_template')
        if 'futurereply_template' in validated_data:
            futurereply_data = validated_data.pop('futurereply_template')

        template = Template.objects.create(
                #template_id = template_id,
                creator = creator,
                #project = project,
                status = 1,
                #rev = 0,
                **validated_data)
        template_id = template.id

        #a template can have no projects associated
        project_name = ''
        project_code = ''
        contractor_logo = ''

        try:
            project = template.project
            project_name = project.project_name
            project_code = project.project_code
            contractor_logo = project.logo
        except:
            pass

        if header_data:
            header = Header.objects.create(
                    header_id = template_id,
                    template = template, 
                    project_name = project_name,
                    contract_no = project_code,
                    contractor_logo_1 = contractor_logo,
                    **header_data)
        if salutation_data:
            salutation = Salutation.objects.create(
                    salutation_id = template_id,
                    template=template, 
                    **salutation_data)
        if title_data:
            title = Title.objects.create(
                    title_id = template_id,
                    template=template, 
                    **title_data)
        if reference_data:
            reference = Reference.objects.create(
                    reference_id = template_id,
                    template=template, 
                    **reference_data)
        if attachment_data:
            attachment = Attachment.objects.create(
                    attachment_id = template_id,
                    template=template, 
                    **attachment_data)
        if descriptionofcontent_data:
            descriptionofcontent = DescriptionOfContent.objects.create(
                    descriptionofcontent_id = template_id,
                    template=template, 
                    **descriptionofcontent_data)
        if aboutthissubmission_data:
            aboutthissubmission = AboutThisSubmission.objects.create(
                    aboutthissubmission_id = template_id,
                    template=template, 
                    **aboutthissubmission_data)
        if futurereply_data:
            futurereply = FutureReply.objects.create(
                    futurereply_id = template_id,
                    template=template, 
                    **futurereply_data)

        return template



    def update(self, instance, validated_data):
        creator =  self.context['request'].user

        header_data = None
        salutation_data = None
        title_data = None
        reference_data = None
        attachment_data = None
        descriptionofcontent_data = None
        aboutthissubmission_data = None
        futurereply_data = None
        if 'header_template' in validated_data:
            header_data = validated_data.pop('header_template')
        if 'salutation_template' in validated_data:
            salutation_data = validated_data.pop('salutation_template')
        if 'title_template' in validated_data:
            title_data = validated_data.pop('title_template')
        if 'reference_template' in validated_data:
            reference_data = validated_data.pop('reference_template')
        if 'attachment_template' in validated_data:
            attachment_data = validated_data.pop('attachment_template')
        if 'descriptionofcontent_template' in validated_data:
            descriptionofcontent_data = validated_data.pop('descriptionofcontent_template')
        if 'aboutthissubmission_template' in validated_data:
            aboutthissubmission_data = validated_data.pop('aboutthissubmission_template')
        if 'futurereply_template' in validated_data:
            futurereply_data = validated_data.pop('futurereply_template')

        #instance.status = validated_data.get('status', instance.status)
        instance.name = validated_data.get('name', instance.name)
        instance.order_of_blocks = validated_data.get('order_of_blocks', instance.order_of_blocks)
        instance.submission_type = validated_data.get('submission_type', instance.submission_type)
        instance.community = validated_data.get('community',instance.community)
        try:
            instance.project = validated_data.get('project', instance.project)
        except:
            pass
        instance.save()

        project_name = ''
        project_code = ''
        contractor_logo = ''
        try:
            project = instance.project
            project_name = project.project_name
            project_code = project.project_code
            contractor_logo = project.logo
        except:
            pass

        template_id = instance.id

        if header_data:
            header = Header.objects.update_or_create(
                    header_id=template_id,
                    defaults = {
                        'project_name' : project_name,
                        'contract_no' : project_code,
                        'contractor_logo_1' : contractor_logo,
                        'template' : instance,
                        **header_data}
                        )
        elif validated_data.get('project', instance.project):
            header = Header.objects.get(header_id=template_id)
            header.project_name = project_name
            header.contract_no = project_code
            header.contractor_logo_1 = contractor_logo
            header.save()

        if salutation_data:
            salutation = Salutation.objects.update_or_create(
                    salutation_id=template_id,
                    defaults = {
                        'template' : instance,
                        **salutation_data}
                        )
        if title_data:
            title = Title.objects.update_or_create(
                    title_id=template_id,
                    defaults = {
                        'template' : instance,
                        **title_data}
                        )
        if reference_data:
            reference = Reference.objects.update_or_create(
                    reference_id=template_id,
                    defaults = {
                        'template' : instance,
                        **reference_data}
                        )
        if attachment_data:
            attachment = Attachment.objects.update_or_create(
                    attachment_id=template_id,
                    defaults = {
                        'template' : instance,
                        **attachment_data}
                        )
        if descriptionofcontent_data:
            descriptionofcontent = DescriptionOfContent.objects.update_or_create(
                    descriptionofcontent_id=template_id,
                    defaults = {
                        'template' : instance,
                        **descriptionofcontent_data}
                        )
        if aboutthissubmission_data:
            aboutthissubmission = AboutThisSubmission.objects.update_or_create(
                    aboutthissubmission_id=template_id,
                    defaults = {
                        'template' : instance,
                        **aboutthissubmission_data}
                        )
        if futurereply_data:
            futurereply = FutureReply.objects.update_or_create(
                    futurereply_id=template_id,
                    defaults = {
                        'template' : instance,
                        **futurereply_data}
                        )

        return instance



class HeaderSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = '__all__'
        read_only_fields = ['contract_no','project_name','contractor_logo_1']


class SalutationSubSerializer(serializers.ModelSerializer):
    to = serializers.CharField(required=True)
    class Meta:
        model = Salutation
        fields = '__all__'


class TitleSubSerializer(serializers.ModelSerializer):
    #title = serializers.CharField(required=True)
    class Meta:
        model = Title
        fields = '__all__'
        #read_only_fields = ['type_of_submission','rev']



class ReferenceSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'


class AttachmentSubSerializer(serializers.ModelSerializer):
    attachment = serializers.BooleanField(required=True)
    class Meta:
        model = Attachment
        fields = '__all__'


class DescriptionOfContentSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptionOfContent
        fields = '__all__'


class AboutThisSubmissionSubSerializer(serializers.ModelSerializer):
    #purpose_of_submission = serializers.IntegerField(required=True)#, source='get_purpose_of_submission_display')
    anticipated_date_of_reply = serializers.DateField(required=True)
    record_reply = serializers.BooleanField(required=True)
    class Meta:
        model = AboutThisSubmission
        fields = '__all__'


class FutureReplySubSerializer(serializers.ModelSerializer):
    class Meta:
        model = FutureReply
        fields = '__all__'
        read_only_fields = ['signature','name']
    '''
    def create(self, validated_data):
        system_id =  self.context['system_id']

        reply = FutureReply.objects.create(
                signature = signature,
                **validated_data)

        return reply
    '''
    

class SignOffSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignOff
        fields = '__all__'


class AttachmentSubmissionForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        queryset = Submission.objects.filter(submitter=self.context['request'].user)
        return(queryset)


class AttachmentFileSerializer(serializers.ModelSerializer):
    submission = AttachmentSubmissionForeignKey()
    class Meta:
        model = AttachmentFile
        fields = ('id','title','file','remarks','submission','include_in_cover_page')


class SubmissionListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False, source='get_status_display')
    class Meta:
        model = Submission
        fields = ('system_id','status','submission_type','project')


class SubmissionRevListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False, source='get_status_display')
    class Meta:
        model = Submission
        fields = ('system_id','status','submission_type','project','rev')


class SubmissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionType
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)#, source='get_status_display')
    header_submission = HeaderSubSerializer()
    salutation_submission = SalutationSubSerializer()
    title_submission = TitleSubSerializer()
    reference_submission = ReferenceSubSerializer(required=False, allow_null=True)
    attachment_submission = AttachmentSubSerializer()
    descriptionofcontent_submission = DescriptionOfContentSubSerializer(required=False, allow_null=True)
    aboutthissubmission_submission = AboutThisSubmissionSubSerializer()
    futurereply_submission = FutureReplySubSerializer(required=False, allow_null=True)
    signoff_submission = SignOffSubSerializer(read_only=True)
    attached_files = AttachmentFileSerializer(required=False, allow_null=True, many=True, read_only=True)
    #comments = CommentSerializer(required=False, allow_null=True, many=True, read_only=True)

    class Meta:
        model = Submission
        #depth = 1
        fields = '__all__'
        read_only_fields = ['rev','status','comment']
        extra_fields = ['header_submission','salutation_submission',
                        'title_submission','reference_submission',
                        'attachment_submission','descriptionofcontent_submission',
                        'aboutthissubmission_submission', 'futurereply_submission',
                        'attached_files','signoff_submission']


        #"structure": ["field_contractor","-","field_project_id","-",
        #"CSF","/","field_submission_type","-",
        #"field_discipline_code","-","field_document_no","-",
        #"field_ext_trig_id","/","field_year"]
    

    def create(self, validated_data):
        submitter =  self.context['request'].user
        #template_id = self.context.get('template_id')
        #template = Template.objects.get(template_id=template_id)
        #order_of_blocks = template.order_of_blocks

        header_data = None
        salutation_data = None
        title_data = None
        reference_data = None
        attachment_data = None
        descriptionofcontent_data = None
        aboutthissubmission_data = None
        futurereply_data = None
        if 'header_submission' in validated_data:
            header_data = validated_data.pop('header_submission')
        if 'salutation_submission' in validated_data:
            salutation_data = validated_data.pop('salutation_submission')
        if 'title_submission' in validated_data:
            title_data = validated_data.pop('title_submission')
        if 'reference_submission' in validated_data:
            reference_data = validated_data.pop('reference_submission')
        if 'attachment_submission' in validated_data:
            attachment_data = validated_data.pop('attachment_submission')
        if 'descriptionofcontent_submission' in validated_data:
            descriptionofcontent_data = validated_data.pop('descriptionofcontent_submission')
        if 'aboutthissubmission_submission' in validated_data:
            aboutthissubmission_data = validated_data.pop('aboutthissubmission_submission')
        if 'futurereply_submission' in validated_data:
            futurereply_data = validated_data.pop('futurereply_submission')

        submission = Submission(
                submitter = submitter,
                status = 1,
                rev = 0,
                year = date.today().year,
                #order_of_blocks=order_of_blocks, 
                **validated_data)
        last_submission = Submission.objects.filter(project=submission.project).last()

        last_sequence_number = 1
        if last_submission:
            last_sequence_number = last_submission.sequence_number + 1
        system_id = str(submission.project.project_code) + '-' + str(SUBMISSION_TYPE_ABBREVIATIONS[submission.submission_type.display_name]) + '-' + str(last_sequence_number).zfill(4)
        submission.system_id = system_id
        submission.parent_system_id = system_id
        submission.sequence_number = last_sequence_number
        
        #generate submission_reference_number
        submission_ref_no = ""
        component_list = submission.project.submission_reference_number_structure["structure"]
        for component in component_list:
            if 'field' in component:
                if component.lower()=='field_contractor':
                    submission_ref_no += submission.target_recipient.short_name
                elif component.lower()=='field_project_id':
                    submission_ref_no += submission.project.project_code
                elif component.lower()=='field_submission_type':
                    submission_ref_no += SUBMISSION_TYPE_ABBREVIATIONS[submission.submission_type.display_name]
                elif component.lower()=='field_submission_form':
                    submission_ref_no += SUBMISSION_FORM_ABBREVIATIONS[submission.submission_type.display_name]
                elif component.lower()=='field_discipline_code':
                    submission_ref_no += submission.discipline_code
                elif component.lower()=='field_document_no':
                    submission_ref_no += str(submission.document_number).zfill(4)
                elif component.lower()=='field_ext_trig_id':
                    submission_ref_no += str(submission.ext_rev)
                elif component.lower()=='field_year':
                    submission_ref_no += str(submission.year)
            else:
                submission_ref_no += component

        submission.submission_reference_number = submission_ref_no

        #generate title from structure
        generated_title = ""
        component_list = submission.project.title_structure["structure"]
        for component in component_list:
            if 'field' in component:
                if component.lower()=='field_submission_type':
                    generated_title += submission.submission_type.display_name
                elif component.lower()=='field_submission_type_abbr':
                    generated_title += SUBMISSION_TYPE_ABBREVIATIONS[submission.submission_type.display_name]
                elif component.lower()=='field_discipline_code':
                    generated_title += submission.discipline_code
                elif component.lower()=='field_document_no':
                    generated_title += str(submission.document_number).zfill(4)
                elif component.lower()=='field_submission_name':
                    generated_title += submission.name
                elif component.lower()=='field_srm_version_number':
                    generated_title += str(submission.ext_rev)
            else:
                generated_title += component

        submission.title = generated_title
        #submission.document_srm_id = submission.id
        #submission_id = submission.id
        submission.save()

        signoff_has_submitter = False
        if True: #'signoff_has_submitter' in validated_data:
            signoff_has_submitter = validated_data.get('signoff_has_submitter', submission.signoff_has_submitter)
            submission.signoff_has_submitter = signoff_has_submitter
            submission.approval_flow = validated_data.get('approval_flow', submission.approval_flow)
            approval_flow = submission.approval_flow
            if approval_flow:
                step_flow = json.loads(approval_flow.step_flow)
                signoff_number_of_blocks = len(step_flow)
                if signoff_has_submitter:
                    signoff_number_of_blocks += 1
                signoff_blocks = []
                #add submitter block
                if submission.signoff_has_submitter:
                    signoff_blocks.append({
                            'id':submitter.emat_user_id,
                            'name':submitter.name,
                            'initials':submitter.initials,
                            'job_title':submitter.job_title,
                            'signature':submitter.signature
                        })
                circular_identification_list = []
                for block in step_flow:
                    user_id = block["user"][0]
                    user = CustomUser.objects.filter(emat_user_id=user_id).first()                    
                    signoff_blocks.append({
                        'id':user.emat_user_id,
                        'name':user.name,
                        'initials':user.initials,
                        'job_title':user.job_title,
                        'signature':''
                    })
                    label = block["label"]
                    circular_identification_list.append(user.initials)
                circular_identification = ""
                for initials in reversed(circular_identification_list):
                    circular_identification += initials
                    circular_identification += "-"
                if circular_identification[-1]=="-":
                    circular_identification = circular_identification[:-1]
                submission.circulation_identification = circular_identification
                sign_off = SignOff(
                        signoff_id = system_id,
                        no_of_blocks = signoff_number_of_blocks,
                        blocks = signoff_blocks,
                        approval_flow = approval_flow
                    )
            submission.save()
            if sign_off:
                sign_off.submission = submission
                sign_off.save()

        if header_data:
            header = Header.objects.create(
                    header_id = submission.system_id,
                    submission=submission, 
                    project_name = submission.project.project_name,
                    contract_no = submission.project.project_code,
                    contractor_logo_1 = submission.project.logo,
                    **header_data)
        if salutation_data:
            salutation = Salutation.objects.create(
                    salutation_id = submission.system_id,
                    submission=submission, 
                    **salutation_data)

        if title_data:
            title = Title.objects.create(
                    title_id = submission.system_id,
                    submission=submission, 
                    **title_data)

        if reference_data:
            reference = Reference.objects.create(
                    reference_id = submission.system_id,
                    submission=submission, 
                    **reference_data)
        if attachment_data:
            attachment = Attachment.objects.create(
                    attachment_id = submission.system_id,
                    submission=submission, 
                    **attachment_data)
        if descriptionofcontent_data:
            descriptionofcontent = DescriptionOfContent.objects.create(
                    descriptionofcontent_id = submission.system_id,
                    submission=submission, 
                    **descriptionofcontent_data)
        purposes = submission.project.purposes.all()
        purpose_dict = {}
        for purpose in purposes:
            purpose_dict[purpose.name] = False
        if aboutthissubmission_data:
            aboutthissubmission = AboutThisSubmission.objects.create(
                    aboutthissubmission_id = submission.system_id,
                    submission=submission,
                    purpose_of_submission = purpose_dict,
                    **aboutthissubmission_data)
            if futurereply_data and aboutthissubmission.record_reply:
                futurereply = FutureReply.objects.create(
                        futurereply_id = submission.system_id,
                        submission=submission, 
                        #signature=submitter.signature,
                        **futurereply_data)
            if aboutthissubmission.purpose_chosen.name in aboutthissubmission.purpose_of_submission:
                aboutthissubmission.purpose_of_submission[aboutthissubmission.purpose_chosen.name] = True
                aboutthissubmission.save()

        return submission



    def update(self, instance, validated_data):
        creator =  self.context['request'].user

        header_data = None
        salutation_data = None
        title_data = None
        reference_data = None
        attachment_data = None
        descriptionofcontent_data = None
        aboutthissubmission_data = None
        futurereply_data = None
        if 'header_submission' in validated_data:
            header_data = validated_data.pop('header_submission')
        if 'salutation_submission' in validated_data:
            salutation_data = validated_data.pop('salutation_submission')
        if 'title_submission' in validated_data:
            title_data = validated_data.pop('title_submission')
        if 'reference_submission' in validated_data:
            reference_data = validated_data.pop('reference_submission')
        if 'attachment_submission' in validated_data:
            attachment_data = validated_data.pop('attachment_submission')
        if 'descriptionofcontent_submission' in validated_data:
            descriptionofcontent_data = validated_data.pop('descriptionofcontent_submission')
        if 'aboutthissubmission_submission' in validated_data:
            aboutthissubmission_data = validated_data.pop('aboutthissubmission_submission')
        if 'futurereply_submission' in validated_data:
            futurereply_data = validated_data.pop('futurereply_submission')

        instance.description = validated_data.get('description', instance.description)
        instance.project = validated_data.get('project', instance.project)
        instance.target_recipient = validated_data.get('target_recipient', instance.target_recipient)
        instance.submission_type = validated_data.get('submission_type', instance.submission_type)
        try:
            instance.circulation_identification_visible = validated_data.get('circulation_identification_visible', instance.circulation_identification_visible)
        except:
            pass
        #instance.order_of_blocks = validated_data.get('order_of_blocks', instance.order_of_blocks) #cannot change order of blocks in submission mode

        project = instance.project
        project_name = project.project_name
        project_code = project.project_code
        contractor_logo = project.logo
        system_id = instance.system_id

        signoff_has_submitter = instance.signoff_has_submitter
        if 'signoff_has_submitter' in validated_data:
            signoff_has_submitter = validated_data.get('signoff_has_submitter', instance.signoff_has_submitter)
            instance.signoff_has_submitter = signoff_has_submitter
            instance.approval_flow = validated_data.get('approval_flow', instance.approval_flow)
            approval_flow = instance.approval_flow
            if approval_flow:
                step_flow = json.loads(approval_flow.step_flow)
                signoff_number_of_blocks = len(step_flow)
                if instance.signoff_has_submitter:
                    signoff_number_of_blocks += 1
                signoff_blocks = []
                #add submitter block
                if instance.signoff_has_submitter:
                    signoff_blocks.append({
                            'id':creator.emat_user_id,
                            'name':creator.name,
                            'initials':creator.initials,
                            'job_title':creator.job_title,
                            'signature':creator.signature
                        })
                circular_identification_list = []
                for block in step_flow:
                    user_id = block["user"][0]
                    user = CustomUser.objects.filter(emat_user_id=user_id).first()                    
                    signoff_blocks.append({
                        'id':user.emat_user_id,
                        'name':user.name,
                        'initials':user.initials,
                        'job_title':user.job_title,
                        'signature':''
                    })
                    label = block["label"]
                    circular_identification_list.append(user.initials)
                circular_identification = ""
                for initials in reversed(circular_identification_list):
                    circular_identification += initials
                    circular_identification += "-"
                if circular_identification[-1]=="-":
                    circular_identification = circular_identification[:-1]
                instance.circulation_identification = circular_identification
                instance.save()
                sign_off,exist = SignOff.objects.update_or_create(
                        signoff_id = system_id,
                        defaults = {
                            'no_of_blocks': signoff_number_of_blocks,
                            'blocks': signoff_blocks,
                            'submission': instance,
                            'approval_flow': approval_flow
                        }
                    )
        instance.save()

        if header_data:
            header,exist = Header.objects.update_or_create(
                    header_id=system_id,
                    defaults = {
                        'project_name' : project_name,
                        'contract_no' : project_code,
                        'contractor_logo_1' : contractor_logo,
                        'submission' : instance,
                        **header_data}
                        )
        elif validated_data.get('project', instance.project):
            header = Header.objects.get(header_id=system_id)
            header.project_name = project_name
            header.contract_no = project_code
            header.contractor_logo_1 = contractor_logo
            header.save()

        if salutation_data:
            salutation,exist = Salutation.objects.update_or_create(
                    salutation_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **salutation_data}
                        )
        if title_data:
            title,exist = Title.objects.update_or_create(
                    title_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **title_data}
                        )
        if reference_data:
            reference,exist = Reference.objects.update_or_create(
                    reference_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **reference_data}
                        )
        if attachment_data:
            attachment,exist = Attachment.objects.update_or_create(
                    attachment_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **attachment_data}
                        )
        if descriptionofcontent_data:
            descriptionofcontent,exist = DescriptionOfContent.objects.update_or_create(
                    descriptionofcontent_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **descriptionofcontent_data}
                        )
        purposes = instance.project.purposes.all()
        purpose_dict = {}
        for purpose in purposes:
            purpose_dict[purpose.name] = False
        if aboutthissubmission_data:
            aboutthissubmission,exist = AboutThisSubmission.objects.update_or_create(
                    aboutthissubmission_id=system_id,
                    defaults = {
                        'submission' : instance,
                        'purpose_of_submission': purpose_dict,
                        **aboutthissubmission_data}
                        )
        aboutthissubmission = AboutThisSubmission.objects.filter(aboutthissubmission_id=system_id).first()
        if aboutthissubmission.purpose_chosen.name in aboutthissubmission.purpose_of_submission:
            aboutthissubmission.purpose_of_submission[aboutthissubmission.purpose_chosen.name] = True
            aboutthissubmission.save()
        if futurereply_data and aboutthissubmission.record_reply:
            futurereply,exist = FutureReply.objects.update_or_create(
                    futurereply_id=system_id,
                    defaults = {
                        'submission' : instance,
                        **futurereply_data}
                        )

        return instance



class SubmissionRevSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)#, source='get_status_display')
    description = serializers.CharField(required=False, allow_null=True)
    header_submission = HeaderSubSerializer(required=False, allow_null=True)
    salutation_submission = SalutationSubSerializer(required=False, allow_null=True)
    title_submission = TitleSubSerializer(required=False, allow_null=True)
    reference_submission = ReferenceSubSerializer(required=False, allow_null=True)
    attachment_submission = AttachmentSubSerializer(required=False, allow_null=True)
    descriptionofcontent_submission = DescriptionOfContentSubSerializer(required=False, allow_null=True)
    aboutthissubmission_submission = AboutThisSubmissionSubSerializer(required=False, allow_null=True)
    futurereply_submission = FutureReplySubSerializer(required=False, allow_null=True)
    signoff_submission = SignOffSubSerializer(read_only=True)
    attached_files = AttachmentFileSerializer(required=False, allow_null=True, many=True, read_only=True)
    #comments = CommentSerializer(required=False, allow_null=True, many=True, read_only=True)

    class Meta:
        model = Submission
        #depth = 1
        fields = '__all__'
        read_only_fields = ['rev','status','comment','approval_flow', 
                            'submission_type', 'target_recipient', 
                            'project', 'name', 'discipline_code',
                            'responsible_party', 'trade', 'person_in_charge',
                            'document_number'
                            ]
        extra_fields = ['header_submission','salutation_submission',
                        'title_submission','reference_submission',
                        'attachment_submission','descriptionofcontent_submission',
                        'aboutthissubmission_submission', 'futurereply_submission',
                        'attached_files', 'signoff_submission']

    
    def create(self, validated_data):
        submitter =  self.context['request'].user
        system_id = self.context['system_id']

        header_data = None
        salutation_data = None
        title_data = None
        reference_data = None
        attachment_data = None
        descriptionofcontent_data = None
        aboutthissubmission_data = None
        futurereply_data = None
        if 'header_submission' in validated_data:
            header_data = validated_data.pop('header_submission')
        if 'salutation_submission' in validated_data:
            salutation_data = validated_data.pop('salutation_submission')
        if 'title_submission' in validated_data:
            title_data = validated_data.pop('title_submission')
        if 'reference_submission' in validated_data:
            reference_data = validated_data.pop('reference_submission')
        if 'attachment_submission' in validated_data:
            attachment_data = validated_data.pop('attachment_submission')
        if 'descriptionofcontent_submission' in validated_data:
            descriptionofcontent_data = validated_data.pop('descriptionofcontent_submission')
        if 'aboutthissubmission_submission' in validated_data:
            aboutthissubmission_data = validated_data.pop('aboutthissubmission_submission')
        if 'futurereply_submission' in validated_data:
            futurereply_data = validated_data.pop('futurereply_submission')
        #if 'approval_flow' in validated_data: #remove, we can't change approval flow at this point
        #    approval_flow = validated_data.pop('approval_flow')

        prev_submission = Submission.objects.filter(system_id__startswith=system_id).last()
        prev_rev = prev_submission.rev
        rev = prev_rev + 1

        first_submission = Submission.objects.filter(system_id__startswith=system_id).first()

        description = prev_submission.description
        if 'description' in validated_data:
            description_data = validated_data.pop('description')
            description = description_data

        signoff_has_submitter = prev_submission.signoff_has_submitter
        if 'signoff_has_submitter' in validated_data:
            signoff_has_submitter_data = validated_data.pop('signoff_has_submitter')
            signoff_has_submitter = signoff_has_submitter_data

        submission = Submission(
                submitter = submitter,
                status = 1, #new revision starts with 'in progress'
                rev = rev,
                submission_reference_number = prev_submission.submission_reference_number,
                approval_flow = prev_submission.approval_flow, #the approval flow cannot be changed at this point
                name = prev_submission.name,
                title = prev_submission.title,
                submission_type = prev_submission.submission_type, #the submission type cannot be changed at this point 
                target_recipient = prev_submission.target_recipient,
                discipline_code = prev_submission.discipline_code,
                trade = prev_submission.trade,
                responsible_party = prev_submission.responsible_party,
                person_in_charge = prev_submission.person_in_charge,
                document_number = prev_submission.document_number,
                remark = prev_submission.remark,
                project = prev_submission.project,
                description = description,
                signoff_has_submitter = signoff_has_submitter,
                year = prev_submission.year,
                comment = '', #reviewer comment from previous revision is deleted                
                **validated_data)

        if 'order_of_blocks' not in validated_data:
            submission.order_of_blocks = prev_submission.order_of_blocks

        prev_system_id = system_id
        system_id = system_id + '-' + str(rev)
        submission.system_id = system_id
        submission.parent_system_id = first_submission.parent_system_id
        submission.sequence_number = first_submission.sequence_number

        #submission.document_srm_id = first_submission.id
        submission.circulation_identification = prev_submission.circulation_identification
        submission.save()

        if header_data:
            header = Header.objects.create(
                    header_id = submission.system_id,
                    submission=submission, 
                    project_name = submission.project.project_name,
                    contract_no = submission.project.project_code,
                    contractor_logo_1 = submission.project.logo,
                    **header_data)
        else:
            header = Header.objects.filter(header_id__startswith=prev_system_id).last()
            header.pk = system_id
            header.submission = submission
            header.save()

        if salutation_data:
            salutation = Salutation.objects.create(
                    salutation_id = submission.system_id,
                    submission=submission, 
                    **salutation_data)
        else:
            salutation = Salutation.objects.filter(salutation_id__startswith=prev_system_id).last()
            salutation.pk = system_id
            salutation.submission = submission
            salutation.save()

        if title_data:
            title = Title.objects.create(
                    title_id = submission.system_id,
                    submission=submission, 
                    **title_data)
        else:
            title = Title.objects.filter(title_id__startswith=prev_system_id).last()
            title.pk = system_id
            title.submission = submission
            title.save()

        if reference_data:
            reference = Reference.objects.create(
                    reference_id = submission.system_id,
                    submission=submission, 
                    **reference_data)
        else:
            reference = Reference.objects.filter(reference_id__startswith=prev_system_id).last()
            reference.pk = system_id
            reference.submission = submission
            reference.save()

        if attachment_data:
            attachment = Attachment.objects.create(
                    attachment_id = submission.system_id,
                    submission=submission, 
                    **attachment_data)
        else:
            attachment = Attachment.objects.filter(attachment_id__startswith=prev_system_id).last()
            attachment.pk = system_id
            attachment.submission = submission
            attachment.save()

        if descriptionofcontent_data:
            descriptionofcontent = DescriptionOfContent.objects.create(
                    descriptionofcontent_id = submission.system_id,
                    submission=submission, 
                    **descriptionofcontent_data)
        else:
            descriptionofcontent = DescriptionOfContent.objects.filter(descriptionofcontent_id__startswith=prev_system_id).last()
            descriptionofcontent.pk = system_id
            descriptionofcontent.submission = submission
            descriptionofcontent.save()

        if aboutthissubmission_data:
            aboutthissubmission_prev = AboutThisSubmission.objects.filter(aboutthissubmission_id__startswith=prev_system_id).last()
            aboutthissubmission = AboutThisSubmission.objects.create(
                    aboutthissubmission_id = submission.system_id,
                    submission=submission, 
                    **aboutthissubmission_data)
            aboutthissubmission.purpose_of_submission = aboutthissubmission_prev.purpose_of_submission
            aboutthissubmission.save()
            if futurereply_data and aboutthissubmission.record_reply:
                futurereply = FutureReply.objects.create(
                        futurereply_id = submission.system_id,
                        submission=submission, 
                        **futurereply_data)
        else:
            aboutthissubmission = AboutThisSubmission.objects.filter(aboutthissubmission_id__startswith=prev_system_id).last()
            aboutthissubmission.pk = system_id
            aboutthissubmission.submission = submission
            aboutthissubmission.save()
            if aboutthissubmission.record_reply:
                futurereply = FutureReply.objects.filter(futurereply_id__startswith=prev_system_id).last()
                json_reply = futurereply.reply
                futurereply.pk = system_id
                futurereply.submission = submission
                futurereply.name = ""
                #futurereply.comment = ""
                futurereply.date = None
                futurereply.signature = ""
                new_reply = {}
                new_free_text = {}
                for key,value in json_reply.items():
                    new_reply[key] = False
                for key,value in futurereply.free_text.items():
                    new_free_text[key] = ""
                futurereply.reply = new_reply
                futurereply.free_text = new_free_text
                futurereply.save()

        signoff = SignOff.objects.filter(signoff_id__startswith=prev_system_id).last()
        signoff.pk = system_id
        signoff.submission = submission
        signoff.save()

        attached_files = prev_submission.attached_files
        for file in attached_files.all():
            file.pk = None
            file.submission = submission
            file.save()

        return submission


class NamevaluepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = NameValuePair
        fields = '__all__'

    def create(self, validated_data):
        creator =  self.context['request'].user

        namevaluepair = NameValuePair.objects.create(
                creator = creator,
                **validated_data)

        return namevaluepair


class ApprovalFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalFlow
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'


class ReviewerSerializer(serializers.ModelSerializer):
    #project_reviewers = serializers.HyperlinkedRelatedField(many=True, view_name='project-details', read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Reviewer
        #fields = '__all__'
        fields = ('reviewer_id','primary_name','secondary_name','short_name','projects')
