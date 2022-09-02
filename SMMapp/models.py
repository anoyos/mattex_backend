from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import FileExtensionValidator
#from simple_history.models import HistoricalRecords
#from jsignature.fields import JSignatureField
import datetime


STATUS = [
    (1,'In progress'),
    (2,'Awaiting approval'),
    (3,'Submitted'),
    (4,'Rejected')
]

TEMPLATE_STATUS = [
    (1,'In progress'),
    (2,'Active'),
    (3,'Inactive')
]

DISCIPLINE_CODE = [
    ('AR', 'Architectural'),
    ('BD', 'Building Services'),
    ('CV', 'Civil'),
    ('LU', 'Landscape'),
    ('ST', 'Structural'),
    ('MA', 'Marine or Water Tributary'),
    ('RD', 'Roadworks'),
    ('DR', 'Drainage works'),
    ('MD', 'Multi Discipline'),
    ('GE', 'Geotechnical works'),
    ('SL', 'Slopworks'),
    ('ME', 'Mechanical-Electrical'),
    ('UU', 'Underground Utility'),
    ('NA', 'Not Applicable')
]

RESPONSIBLE_PARTIES = [
    ('Main Contractor','Main Contractor'),
    ('Sub Contractor','Sub Contractor'),
    ('Property Owner','Property Owner')
]

SUBMISSION_TYPE_ABBREVIATIONS = {
    'Design': 'DES',
    'Method Statement': 'MST',
    'Material Details Page': 'MAT',
    'Programming': 'PROG',
    'Temp. Work Design': 'TWD',
    'General': 'GEN',
    'Shop Drawing': 'SD',
    'Testing Document': 'TD'
}

SUBMISSION_FORM_ABBREVIATIONS = {
    'Design': 'DSF',
    'Material Details Page': 'MSF',
    'General': 'GSF',
    'Shop Drawing': 'SDSF'
}

DUPLICATION_KEYS = [
        ('field_project_id','By Project Id'),
        ('field_submission_type', 'By Submission Type'),
        ('field_discipline_code', 'By Discipline Code'),
        ('field_year', 'By Year')
    ]

'''
PURPOSE_OF_SUBMISSION = [
                    (1,"For Review"),
                    (2,"For Acceptance"),
                    (3,"For Information"),
                    (4,"For Record")
                ]

SUBMISSION_TYPE = [
    ('MAT','Material'),
    ('TWD','Temporary Work Design'),
    ('MS','Method Statement'),
    ('RD','Record'),
    ('SUR','Survey'),
    ('O','Others')
]

'''

def upload_to(instance, filename):
    
    date = str(datetime.datetime.now()).replace('.','_').replace(' ','_')
    url = 'images/image_' + date + filename
    return(url)

# Create your models here.

#check this for upload of multiple files:
#https://stackoverflow.com/a/52016594/15043686

#Table containing info about the project + info to be pre-filled in cover page
class CustomUser(AbstractUser):
    email = models.EmailField("Email", max_length=255, unique=True, null=True)
    emat_user_id = models.IntegerField("Emat user id", unique=True, null=True)
    name = models.CharField("Name", max_length=255, null=True)
    title = models.CharField("Title", max_length=255, null=True)
    job_title = models.CharField("Job title", max_length=255, null=True)
    initials = models.CharField("Initials", max_length=255, null=True)
    status = models.IntegerField("Status", default=1)
    emat_status = models.IntegerField("Emat status", default=1)
    signature = models.TextField("Signature", null=True)
    signature_short = models.TextField("Signature short", null=True)
    emat_admin = models.IntegerField("Emat admin", default=0)
    avatar = models.CharField("Avatar", max_length=255, null=True)

    # add additional fields in here

    def __str__(self):
        return self.email


class Reviewer(models.Model):
    reviewer_id = models.IntegerField("Reviewer id", primary_key=True)
    primary_name = models.CharField("Primary name", max_length=255)
    secondary_name = models.CharField("Secondary name", max_length=255, null=True, blank=True)
    short_name = models.CharField("Short name", max_length=100, null=True, blank=True)
    #project = models.ManyToManyField(Project, null=True, blank=True, related_name='project_reviewer')

    def __str__(self):
        return self.primary_name


class Purpose(models.Model):
    purpose_id = models.IntegerField("Purpose id", primary_key=True)
    name = models.CharField("Name", max_length=255)
    short_name = models.CharField("Short name", max_length=100, null=True, blank=True)
    #project = models.ManyToManyField(Project, null=True, blank=True, related_name='project_reviewer')

    def __str__(self):
        return self.name



class Project(models.Model):
    project_id = models.IntegerField("Project id", primary_key=True)
    project_code = models.CharField("Project code", max_length=50, unique=True)
    project_name = models.TextField("Project name")
    project_display_name = models.TextField("Project display name")
    client = models.CharField("Client", max_length=255, null=True, blank=True)
    division = models.CharField("Division", max_length=255, null=True, blank=True)
    status = models.IntegerField("Status", null=True)
    project_in_charge = models.CharField("Project in charge", max_length=255, null=True, blank=True)
    primary_name = models.CharField("Primary name", max_length=255, null=True, blank=True)
    transaction_type_name = models.CharField("Transaction type name", max_length=255, null=True, blank=True)
    chop = models.TextField("Chop", null=True, blank=True)
    logo = models.TextField("Logo", null=True, blank=True)
    address = models.TextField("Address", null=True, blank=True)
    tel = models.CharField("Tel", max_length=255, null=True, blank=True)
    #purpose = models.JSONField("Purpose", null=True, blank=True)
    reviewers = models.ManyToManyField(Reviewer, null=True, blank=True, related_name='projects')
    purposes = models.ManyToManyField(Purpose, null=True, blank=True, related_name='purpose_projects')
    submission_reference_number_structure = models.JSONField("Submission ref. no. structure", default={"structure":[]})
    duplication_key = models.CharField("De-duplication key", max_length=100, choices=DUPLICATION_KEYS, null=True, blank=True)
    title_structure = models.JSONField("Submission title structure", default={"structure":[]})

    def __str__(self):
        return self.project_name


class SubmissionType(models.Model):
    submission_type_id = models.IntegerField("Submission type id", primary_key=True)
    model_type = models.CharField("Model type", max_length=255)
    display_name = models.CharField("Display name", max_length=255)
    status = models.IntegerField("Status", null=True, blank=True)

    def __str__(self):
        return self.display_name


class ApprovalFlow(models.Model):
    approval_flow_id = models.IntegerField("Project id", primary_key=True)
    name = models.CharField("Name", max_length=250)
    step_flow = models.TextField("Step flow")
    status = models.IntegerField("Status", null=True)
    remark = models.TextField("Remark", null=True)
    #submission_type = models.CharField("Submission type", max_length=100, null=True)
    submission_type = models.ForeignKey(SubmissionType, on_delete=models.DO_NOTHING, related_name='approval_flow_submission_type')

    def __str__(self):
        return self.name


class Trade(models.Model):
    trade_id = models.IntegerField("Trade id", primary_key=True)
    name = models.CharField("Name", max_length=255)
    short_form = models.CharField("Short form", max_length=255, null=True, blank=True)
    status = models.IntegerField("Status", null=True)

    def __str__(self):
        return self.name


#class containing only the metadata of the template
class Template(models.Model): 
    #template_id = models.CharField(max_length=100, primary_key=True, editable=False)
    name = models.CharField("Name", max_length=255, null=False, blank=False, unique=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("Updated at", auto_now=True, editable=False)
    creator = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='creator', editable=False)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='project', blank=True, null=True)
    order_of_blocks = models.JSONField("Order of blocks", null=True)
    status = models.IntegerField("Status", choices=TEMPLATE_STATUS, default=1, editable=False)
    submission_type = models.JSONField("Submission type", default={"submission_types": []}, null=True)
    #submission_type = models.CharField("Submission type", choices=SUBMISSION_TYPE, max_length=50, null=True, blank=True)
    #submission_type = models.ManyToManyField(SubmissionType, null=True, blank=True, related_name='submission_types')
    community = models.BooleanField("Community", default=True)
    circulation_identification_visible = models.BooleanField("Circulation identification visible", default=True, null=True, blank=True)
    signoff_has_submitter = models.BooleanField("Signoff has submitter", default=False, null=True, blank=True)
    #order of blocks ex.: {1:'salutation',2:'title',etc.}

class Submission(models.Model):
    #template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="template", editable=False, null=True, blank=True)
    #System data points
    system_id = models.CharField("System Id", max_length=50, editable=False) #e.g. 0997-MAT-0022-2, system generated ID
    parent_system_id = models.CharField("Parent System Id", max_length=50, editable=False) #e.g. 0997-MAT-0022, system generated ID
    sequence_number = models.IntegerField("Sequence number", default=1, editable=False) #e.g. 0022, system generated
    submission_reference_number = models.CharField("Submission reference number", max_length=255, editable=False, null=True, blank=True) #e.g. CWB/1037/GEN/0001B, system generated according to structure defined in the project
    document_number = models.IntegerField("Document number", null=False, blank=False) #e.g. 0008, this one is inputted manually by the user.

    #document_srm_id = models.IntegerField("Document id for submission to SRM", editable=False, null=True)
    document_date = models.DateField("Document date", auto_now_add=True, editable=False)
    document_edited = models.DateTimeField("Last edit", auto_now=True, editable=False)
    year = models.IntegerField("Year", editable=False)
    status = models.IntegerField("Status", choices=STATUS, default=1, editable=False)
    #associated_content = models.JSONField("Associated content", null=True, blank=True, editable=False)

    #Mandatory data points
    #submission_type = models.CharField("Submission type", max_length=50, null=False, blank=False)
    name = models.CharField("Submission name", max_length=100, null=False, blank=False)
    description = models.TextField("Submission description", null=False, blank=False)
    title = models.CharField("Title", max_length=255, editable=False)

    submitter = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='submitter', editable=False)
    target_recipient = models.ForeignKey(Reviewer, on_delete=models.DO_NOTHING, related_name='target_recipient', null=False, blank=False)     
    submission_type = models.ForeignKey(SubmissionType, on_delete=models.DO_NOTHING, related_name='submission_type')
    discipline_code = models.CharField("Discipline Code", max_length=100, choices=DISCIPLINE_CODE, null=False, blank=False)
    trade = models.ForeignKey(Trade, on_delete=models.DO_NOTHING, related_name='trade', null=False, blank=False)
    responsible_party = models.CharField("Responsible Party", max_length=100, choices=RESPONSIBLE_PARTIES, null=False, blank=False)
    person_in_charge = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='person_in_charge', null=False, blank=False)

    order_of_blocks = models.JSONField("Order of blocks", null=True, blank=True)
    remark = models.TextField("Remark", null=True, blank=True)

    circulation_identification = models.CharField("Circulation identification", max_length=255, editable=False, null=True, blank=True)
    circulation_identification_visible = models.BooleanField("Circulation identification visible", default=True, null=True, blank=True)

    rev = models.IntegerField("Rev.", null=True, blank=True, default=0) #0,1,2...
    ext_rev = models.CharField("External version", max_length=10, default="0", editable=False) #0,A,B...

    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='submission_project')
    approval_flow = models.ForeignKey(ApprovalFlow, on_delete=models.DO_NOTHING, related_name='approval_flow')
    signoff_has_submitter = models.BooleanField("Signoff has submitter", default=False)

    comment = models.TextField("Comment from internal reviewers", null=True, blank=True, editable=False)
    #history = HistoricalRecords()


class Header(models.Model):
    header_id = models.CharField(max_length=100, primary_key=True, editable=False)
    client_logo_1 = models.ImageField("Client logo 1", upload_to=upload_to, null=True, blank=True)
    client_logo_2 = models.ImageField("Client logo 2", upload_to=upload_to, null=True, blank=True)
    client_logo_3 = models.ImageField("Client logo 3", upload_to=upload_to, null=True, blank=True)

    contract_no = models.CharField("Contract number", max_length=100, null=True, blank=True)
    project_name = models.TextField("Project name", null=True, blank=True)
    #has_contractor_logo = models.BooleanField(default=False)
    #contractor_logo_1 = models.ImageField("Contractor logo", upload_to=upload_to, null=True, blank=True)
    contractor_logo_1 = models.TextField("Contractor logo", null=True, blank=True)

    form_control_no = models.CharField("Form control number", max_length=200, null=True, blank=True)
    ctrl_num_visible = models.BooleanField("Form control number visibility", null=True, blank=True, default=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="header_template", editable=False, null=True, blank=True) 
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="header_submission", editable=False, null=True, blank=True)


class Salutation(models.Model):
    salutation_id = models.CharField(max_length=100, primary_key=True, editable=False)
    to = models.CharField("To", max_length=100, null=True, blank=True)
    attn = models.CharField("Attn", max_length=100, null=True, blank=True)
    attn_visible = models.BooleanField("Attn visiblity", null=True, blank=True, default=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="salutation_template", editable=False, null=True, blank=True) 
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="salutation_submission", editable=False, null=True, blank=True)


class Title(models.Model):
    title_id = models.CharField(max_length=100, primary_key=True, editable=False)
    #title = models.CharField("Title", max_length=255, editable=False)
    #project_level_id = models.CharField("Project Level Identification", max_length=200, null=True, blank=True)
    #type_of_submission = models.CharField("Type of submission", choices=SUBMISSION_TYPE, max_length=50, null=True, blank=True)
    #rev = models.IntegerField("Rev.", null=True, blank=True)
    free_text_fields = models.JSONField(null=True, blank=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="title_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="title_submission", editable=False, null=True, blank=True)


class Reference(models.Model):
    reference_id = models.CharField(max_length=100, primary_key=True, editable=False)
    reference = models.JSONField("Reference", null=True, blank=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="reference_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="reference_submission", editable=False, null=True, blank=True)


class Attachment(models.Model):
    attachment_id = models.CharField(max_length=100, primary_key=True, editable=False)
    #This will determine the order of fields
    attachment = models.BooleanField("Attachment", null=True, blank=True)
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="attachment_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="attachment_submission", editable=False, null=True, blank=True)


class DescriptionOfContent(models.Model):
    descriptionofcontent_id = models.CharField(max_length=100, primary_key=True, editable=False)    
    description_of_content = models.JSONField("Description of Content", null=True, blank=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    top_free_text = models.TextField("Top free text", null=True, blank=True)
    show_top_free_text = models.BooleanField("Show top free text", null=True, blank=True, default=False)

    bottom_free_text = models.TextField("Bottom free text", null=True, blank=True)
    show_bottom_free_text = models.BooleanField("Show bottom free text", null=True, blank=True, default=False)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="descriptionofcontent_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="descriptionofcontent_submission", editable=False, null=True, blank=True)


class AboutThisSubmission(models.Model):
    aboutthissubmission_id = models.CharField(max_length=100, primary_key=True, editable=False)
    remarks = models.TextField("Remarks", null=True, blank=True)

    #purpose_of_submission = models.IntegerField("Purpose of submission", 
    #        choices = PURPOSE_OF_SUBMISSION,
    #        null=True, blank=True
    #    )
    purpose_of_submission = models.JSONField("Purpose of submission", null=True, blank=True, editable=False)#default={"For review":False, "For acceptance":False, "For information":False, "For record":False})
    purpose_chosen = models.ForeignKey(Purpose, on_delete=models.CASCADE, related_name="purpose_chosen", null=True, blank=True)
    anticipated_date_of_reply = models.DateField("Anticipated date of reply", null=True, blank=True)
    record_reply = models.BooleanField("Record future reply on Cover", null=True, blank=True)

    #This will determine the order of fields
    order_of_fields = models.JSONField("Order of fields", null=True)

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="aboutthissubmission_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="aboutthissubmission_submission", editable=False, null=True, blank=True)


class FutureReply(models.Model):
    futurereply_id = models.CharField(max_length=100, primary_key=True, editable=False)
    reply = models.JSONField("Reply", null=True, blank=True, default={"Acceptance":False, "Acceptance with comments":False, "Rejected":False})
    free_text = models.JSONField("Free text", null=True, blank=True, default={"Comment":""})
    #comment = models.TextField("Comment", null=True, blank=True)
    name = models.CharField("Name", max_length=200, editable=False, null=True, blank=True)
    signature = models.TextField("Signature", editable=False, null=True, blank=True)
    date = models.DateField("Date", auto_now=True, editable=False)
    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="futurereply_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="futurereply_submission", editable=False, null=True, blank=True)


class SignOff(models.Model):
    signoff_id = models.CharField(max_length=100, primary_key=True, editable=False)
    has_submitter = models.BooleanField("Submitter?", default=False)
    no_of_blocks = models.IntegerField("Number of blocks", default=1, editable=False)
    blocks = models.JSONField("Blocks", default={"blocks":[]})
    approval_flow = models.ForeignKey(ApprovalFlow, on_delete=models.CASCADE, related_name="signoff_approval_flow", editable=False)
    #name = models.CharField("Name", max_length=200, null=True, blank=True, editable=False)
    #title = models.CharField("Title", max_length=200, null=True, blank=True, editable=False)
    #date = models.DateField("Date", auto_now=True, editable=False)
    #signature = models.ImageField("Signature", editable=False, null=True, blank=True) 

    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="signoff_template", editable=False, null=True, blank=True)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="signoff_submission", editable=False, null=True, blank=True)


class AttachmentFile(models.Model): #these can be attached during submission filling
    title = models.CharField("Title", max_length=100, null=False, blank=False)
    file = models.FileField("File", upload_to=upload_to, null=False, validators=[FileExtensionValidator(['pdf'])])
    submission = models.ForeignKey(Submission, null=False, blank=False, on_delete=models.CASCADE, related_name='attached_files')
    remarks = models.TextField("Remarks", null=True, blank=True)
    include_in_cover_page = models.BooleanField("Include in cover page", default=True)
    uploaded_at = models.DateTimeField("Uploaded at", auto_now_add=True, editable=False)

class NameValuePair(models.Model):
    name = models.CharField("Name", max_length=200, null=False, blank=False)
    creator = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name='namevaluepair_creator', editable=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True, editable=False)

'''
class Comment(models.Model): #to store submission comments
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_author', editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField("Comment", null=False, blank=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True, editable=False)
    updated_at = models.DateTimeField("Updated at", auto_now=True, editable=False)
'''