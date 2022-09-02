# Submission Management Module

## Dowloand and run repo
```
git clone #this repo
git remote add origin #this repo
git checkout develop
```
NOTE: Before running the app, you also need to create a .env file containing the environment variables. Please look at settings.py ('databases' section) to check the list of environment variables you need to set.
Example:
```
MYSQL_DATABASE=mattex
MYSQL_USER=django
MYSQL_PASSWORD=django-password
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE_HOST=localhost
MYSQL_DATABASE_PORT=3306
```
Then for running the app, you have 2 options:

### 1) Easy way: using DOCKER
Install and run Docker Desktop. Then from inside the repo, run the run_app.sh file, it will create the docker image and run the app. Then you can access it with your browser at http://127.0.0.1:8000, as simple as that.

### 2) Complicate way (for developing)
```
pip install -r requirements.txt
```
Then you need to create a database called 'mattex' inside your local mysql. Afterwards, remind to start the mysql service:
```
sudo service mysql start
```
And then run migrations:
```
python manage.py makemigrations
python manage.py migrate
```
And finally run the app with:
```
python manage.py runserver
```
Then you can access the app in your browser at the address http://127.0.0.1:8000



## List of APIs (provisory)


```
login/
```
POST API to retrieve user token from e-mat system
Body example (for contractor)
```
{"email":"contractor-a@mattex.com","password":"78907890Ab"}
```
For approver:
```
{
    "email":"smm-approver@mattex.com",
    "password":"78907890Ab"
}
```
General manager:
```
{
    "email":"g-manager@mattex.com",
    "password":"78907890Ab"
}
```

After calling this api, access token is stored in request.session

```
logout/
```
POST API to logout

```
get-project-list/
```
GET API to retrieve list of projects with all their info - this API does NOT fetch data inside the local database.

```
get-and-fetch-project-list/
```
GET API to retrieve and fetch list of projects with all their info into the local database

```
project-list/
```
GET API to show list of projects already saved in the local database

```
get-and-fetch-project-details/1/
```
GET API to retrieve all the details of project with project_id=1 from e-mat and store it inside the local database. IMPORTANT: this API must be called when a user select a project for creating a new submission, in order to fetch data from e-mat to local database. The response of this API does not show the full data of the project (e.g. purpose, reviewers...)

```
project-details/1/
```
GET API to show the details of project with project_id=1 from local database. This API shows the full data of the project (e.g. purpose, reviewers..)


```
get-user-list/1/
```
GET API to show list of users for the project with project id=1. It does NOT fetch the data into the database.

```
get-and-fetch-user-list/1/
```
GET API to show list of users for the project with project id=1 and fetching them in the local database. IMPORTANT: must be called in order to allow submitter to select 'person-in-charge' when creating a new submission.


```
user-detail/8869/
```
GET API to retrieve details of user with id=8869, including his signature, and storing all their details into the database.

```
get-submission-type-list/
```
GET API to retrieve all possible submission types from eMat system. This API is also responsible for fetching all approval flows (for every submission type) from eMat system to local database. IMPORTANT: this API must be called every time at the beginning of the session, to fetch/update all submission types and approval flows into local database.

```
submission-type-list/
```
GET API to visualize all submission types currently stored into the database.

```
submission-type/1
```
GET API to visualize detail of a specific submission-type (e.g. in this case, the submission-type with id=1)

```
get-trade-list/
```
GET API to retrieve all trades from eMat system. IMPORTANT: this API must be called every time at the beginning of the session, to fetch/update all trades into local database.

```
trade-list/
```
GET API to visualize all trades currently stored into the database.


```
get-approval-flow?submission_type=1
```
GET API to retrieve list of approval flows saved in the database. Can specify the submission type.

```
approval-flow/2
```
GET API to visualize detail of a specific approval flow (e.g. in this case, the approval flow with id=2)


```
get-reviewer-list/1
```
GET API to retrieve all reviewers for project with id=1 from e-mat system and fetching them into the local database. IMPORTANT: this API must be called when a user selects a project for creating a new submission, in order to fetch the reviewers for that project inside the local database.

```
reviewer-list/
```
GET API to show the list of reviewers saved in the local database.


```
change-submission-ref-no-structure/1/
```
PATCH API to change the structure of the submission reference number of a certain project (in this case, the project with id=1). An example of submission reference number is 'CWB/1037/GEN/0001B'. This is generated automatically for all submissions based on the structure determined from this API.
The body of the request must contain a field called 'structure' which is a list of the various components to be included in the submission reference number (in the order determined by the list), as well as free texts. The following example contains all the possible components that can be included:
```
{ 
    "submission_ref_no_structure": 
    {
        "structure": 
            [
                "field_contractor",
                "-",
                "field_project_id",
                "-",
                "CSF",
                "/",
                "field_submission_type",
                "-",
                "field_submission_form",
                "-",
                "field_discipline_code",
                "-",
                "field_document_no",
                "-",
                "field_ext_trig_id",
                "/",
                "field_year"]
    },
    "duplication_key":"field_project_id"
 }
 ```
 Those components that starts with 'field_' are just keywords for the backend to process the actual value depending on the project/submission (for instance, 'field_submission_type' will be replaced with 'MAT' if the submission is of type 'Material'), while those components without the word 'field' will be treated as free text and will be copied into the submission reference number without any processing. It is not necessary to include all components as in the example above. In reality "field_submission_form" and "field_submission_type" cannot appear together - there are in fact only 2 options mutually exclusive for this part: 1) CSF/field_submission_type (e.g. CSF/MAT, or 2) field_submission_form only (e.g. MSF). The body of the request must contain another field, called "duplication_key", whose value SHOULD MATCH one of the fields in the "structure" list. This field is the one that is used for the de-duplication mechanism for the 'system_id' inputted by the user. E.g. if 'field_project_id' is selected, it means that there could be no 2 submissions with same system_id under this project (e.g. MAT-0008 and SD-0008 are NOT possible). If 'field_submission_type' is selected instead, there could be 2 submissions with same system_id as long as they have different submission types (e.g. MAT-0008 and SD-0008 are possible), and so on. For this field, only 5 options are possible: "field_project_id", "field_submission_type", "field_submission_form", "field_discipline_code", "field_year".


```
change-title-structure/1/
```
PATCH API to change the structure of the title for a certain project (in this case, the project with id=1). The API works in a similar way to the 'change-submission-ref-no-structure': the body of the request has a similar structure, although the  fields are different. A complete example is the following:
```
{
    "title_structure": 
    {
        "structure": 
            [
                "field_submission_type",
                "-",
                "field_submission_type_abbr",
                " for ", 
                "field_submission_name",
                "-",
                "field_document_no",
                "-",
                "field_discipline_code",
                ", (ver. ",
                "field_srm_version_number",
                ")"
            ]
    } 
}
```


```
template/
```
POST API to add a new template (project is selected in the form)
Body of the POST request must be a JSON like:
```
{
    "header_template": {
        "client_logo_1": null,
        "client_logo_2": null,
        "client_logo_3": null,
        "form_control_no": "",
        "ctrl_num_visible": true
    },
    "salutation_template": {
        "attn": "",
        "attn_visible": true,
        "to": ""
    },
    "title_template": {
        "free_text_fields": null
    },
    "reference_template": {
        "reference": {
            "1": {"Specification reference": ""},
            "2": {"Drawing reference": ""}
        }
    },
    "attachment_template": {},
    "descriptionofcontent_template": {
        "description_of_content": null
    },
    "aboutthissubmission_template": {
        "remarks": ""
    },
    "futurereply_template": {},
    "name": "template_name",
    "order_of_blocks": {
        "1": "header",
        "2": "salutation",
        "3": "title",
        "4": "descriptionofcontent",
        "5": "reference",
        "6": "aboutthissubmission"
    },
    "submission_type" : { "submission_types" :[1,3]},
    "project": null,
    "community": true
}
```
Sections can be pulled off from the JSON if that section should not appear in the cover page. Pay attention to the format of 'order_of_blocks', which determines the order of the various blocks as they will appear in the final cover page.

```
template-list?project_id=1&submission_type=1&status=2
```
GET API to view list of templates - accept project_id, submission type and status as query. Note: only templates with community=true are visible to anyone - if community=false, they are only visible to the creator.

```
template-detail/1
```
GET API to view details of template with id=1. Note: only templates with community=true are visible to anyone - if community=false, they are only visible to the creator.

```
template-update/1
```
PATCH/PUT API to update fields of template with id=1. Both PATCH and PUT methods work. API only available to the creator of the template. Note: template status cannot be changed through this API - must use the API below.

```
change-template-status/<int:pk>/
```
PATCH API to change template status (1=in progress, 2=active, 3=inactive). In order to activate the template, certain blocks must be present (header, salutation, title, attachment, aboutthissubmission), otherwise the API returns error.

```
submission/
```
POST API to add a new submission package - working in the same way as the template API. Sections can be removed (same as template), but when they are added, some fields may be mandatory (see Confluence/figma) for details. 
VERY IMPORTANT: before calling this API, the user must select a project in frontend, and at that point the following 3 APIs must be called - IN THIS SPECIFIC ORDER:
1) 'get-reviewer-list' passing the id of the project, in order to fetch the list of reviewers (on the client side, in SRM) for that project. 
2) 'get-and-fetch-project-details' passing the id of the project, in order to fetch the project data inside the local db.
3) 'get-user-list/<project_id>', This is a necessary step in order to fetch the list of internal approvers and options for the 'person-in-charge' field, otherwise the backend won't be able to create the 'signoff blocks' because the users are not present in the database. (in order to see which users are in the approval-flow, please user the approval-flow API)

Body of the request - this is a minimal example:
```
{
    "header_submission": {
        "client_logo_1": "http://127.0.0.1:8000/media/images/image_2022-06-06_123031_829120client_logo_1.PNG",
        "client_logo_2": null,
        "client_logo_3": null,
        "form_control_no": "PM-07",
        "ctrl_num_visible": true
    },
    "salutation_submission": {
        "to": "AECOM - 12/F, Grand Central Plaza, Tower 2, 138 Shatin runserveral Committee Road Shatin, HK",
        "attn": "Ms. Cherry Yau - Project Manager’s Delegate",
        "attn_visible": true
    },
    "title_submission": {
        "free_text_fields": {
            "1": {
                "Material specification": "TWD - Temp. Work Design, MS - Method Statement, MAT - Material, RD - Record, SUR - Survey, PROG - Programming, REP - Report, QUA - Quality, O - Others"
            },
            "2": {
                "Another free text": "Sample text"
            }
       }
    },
    "reference_submission": {
        "reference": {
            "1": {
                "Specification reference": "S16 - Ironmonger"
            },
            "2": {
                "Drawing reference": "S17"
            }
        }
    },
    "attachment_submission": {
        "attachment": false
    },
    "descriptionofcontent_submission": {
        "description_of_content": {
            "1":{"Description": "We propose Essential Trading Co. Ltd. as the supplier of Ductile Iron Pipe and Fitting (BSEN545) for Watermain. The            related documents are attached for your review and approval."},
            "2":{"1": "Supplier Information"},
            "3":{"2": "Catalogue & Shop Drawing"},
            "4":{"3": "Test Report"},
            "5":{"4": "WSD GA Approval Letter"},
            "6":{"5": "WRAS Certificate"},
            "7":{"6": "ISO Certificate"},
            "8":{"7": "Job Reference(s) and Job Approval Letter"}
        },
        "top_free_text": "This is the free text on top",
        "show_top_free_text": true,
        "bottom_free_text": "This is the free text on bottom",
        "show_bottom_free_text": true
    },
    "aboutthissubmission_submission": {
        "purpose_chosen": 2,
        "anticipated_date_of_reply": "2022-06-09",
        "record_reply": false,
        "remarks": ""
    },
    "futurereply_submission": {
        "reply": {"Rejected":false,"Accepted":false,"Accepted with comments":true},
        "free_text": {"Comment":""},
        "name": "",
        "signature": "",
        "date": "2022-07-19"
    },
    "order_of_blocks": {
        "1": "header",
        "2": "salutation",
        "3": "title",
        "4": "descriptionofcontent",
        "5": "reference",
        "6": "aboutthissubmission"
    },
    "name": "Steel Fabric Mesh",
    "description": "We propose Essential Trading Co. Ltd. as the supplier of Ductile Iron Pipe and Fitting (BSEN545) for Watermain.\r\nThe related documents are attached for your review and approval.’",
    "discipline_code": "AR",
    "responsible_party": "Main Contractor",
    "remark": "",
    "circulation_identification_visible": true,
    "signoff_has_submitter": true,
    "target_recipient": 30,
    "submission_type": 1,
    "trade": 1,
    "person_in_charge": 1,
    "project": 1,
    "approval_flow": 3,
    "document_number": 1
}
```
This structure, especially "order_of_blocks", must be copied from the associated template. Note: 'order_of_fields' is no longer necessary - it can be null, the pdf will be generated according to the default order. Note2: look carefully at the structure of the JSON in 'free_text_fields' of 'title_submission' block, 'description_of_content' in 'descriptionofcontent_submission' block and 'reference' in 'reference_submission' block - They are JSON of JSON files, with the key being the position of the field and the value being another json inf the form {'field name':'value'}.
The field "purpose_of_submission" inside "about this submission" is a JSON containing a list of the purposes for that particular project chosen - it is filled automatically in the backend. "purpose_chosen" instead is the choice of the user (it is a foreign key). To visualize the possible choices, you need to open the 'project-details' API of the corresponding project. The same API can be used to visualize the list of reviewers associated to that project.


```
submission-list/?submission_type=1&project_id=1
```
GET API to show list of submission packages - query by submission type (check the submission-list API to see correspondence between number and type) and project id. A user can only see the submission created by them.

```
submission-detail/<system_id>/
```
GET API to add visualize detail of a submission package with specific system_id. A user can only see the submission created by them.

```
submission-update/<system_id>/
```
PATCH/PUT API to update submission package with specific system_id - both PATCH and PUT methods work. A user can only update the submission created by them. This API must be called to edit the document BEFORE the request of internal approval (if the document has been already submitted for internal approval and rejected, please use the 'submission-rev' API below)


```
submission-rev/<system_id>/
```
POST API to create a new version of a certain submission package with system_id (e.g.:submission-rev/0997-MAT-0001/). The new submission created will have same system_id with an additional incremental integer: 0997-MAT-0001-1, 0997-MAT-0001-2, etc... while the 'parent system_id' is the same as the parent submission.
This API must be called AFTER the document has been rejected by an internal reviewer, because it needs to create a new version (revision) of the submission, so the 'submission-update' API is not suitable for this purpose.
In the body of the request, you can specify just the fields you want to change wrt the previous revision - all the others will be copied from the previous revision (so technically you can just sent an empty json as body in the request - but in this case, the submission will be identical to its previous version, so most likely it won't pass approval).
Note: always use the parent system_id of the original submission (e.g. 0997-MAT-0001) in the parameter passed in the url. DO NOT use the system_id of the child submissions.

```
submission-rev-list/<system_id>/
```
GET API to list all versions of a certain submission package, based on its system_id


```
pdf/<system_id>/
```
GET API to generate pdf with submission form of submission with specific system_id. It includes also the attachments.


```
attachment/
```
POST API to attach a file to a submission package. Note: a user can only attach files to a submission they created.
Example body of the request:
{
    "title": "Additional document",
    "file": "Base64 string of the file",
    "remarks": "Some comment",
    "submission": 1,
    "include_in_cover_page": true
}
The "submission" field is the ID of the submission (NOT the system id!). To find the ID of the submission please use the 'submission-detail' API.


```
attachment-delete/<attachment_id>
```
DELETE API to delete a file attached to a submission package. Note: a user can only delete files to a submission they created.


```
attachment-list/?submission=0968-14
```
GET API to show list of attachments for a specific submission

```
reply/0997-18
```
POST API to add a reply/comment/approval to a submission package (will only be available to the reviewer later on).
The 'reply' field must be a JSON file similar to this: {"Rejected":false,"Accepted":false,"Accepted with comments":true}

```
library/
```
POST API to add a new name-value pair into the library - e.g. if want to inser 'color' as a key in the library, send post request with body: 
```
{"name":"color"}
```

```
library-list?startswith=something
```
GET API to see list of name-value pairs stored in the library. Accept 'contains' and 'startswith' as query (case-insensitive)


```
submit-for-approval/
```
POST API to submit a submission package for approval. The body of the request must contain the system_id, as follows:
{"system_id":"0997-TD-0001"}. The last revision of the submission (e.g. v2, so 0997-TD-0003-2) will be the one submitted for approval.
If request is successfull, it will change the status of the submission document from 1 ('In progress') to 2 ('awaiting approval'). 

```
approve-submission/
```
POST API to internally approve a submission. The body of the request must contain the system_id, as follows:
{"system_id":"0997-MAT-0003"}
If request is successfull, it will change the status of the submission document from 2 ('Awaiting approval') to 3 ('Submitted') and add the signature of that reviewer on cover page. NOTE: if there are 2 or more approvers in the approval flow of this document, the status of the submission will be changed to 3 only after it has been approved by the last reviewer.

```
reject-submission/
```
POST API to internally reject a submission. The body of the request must contain the system_id and (optionally) a comment, as follows:
```
{
    "system_id":"0997-18",
    "comment":"I don't like this submission"
}
```
After calling the API, it will change the status of the submission document from 2 ('Awaiting approval') to 1 ('In progress'), and all signatures of the reviewers will be canceled from the cover page (and the comment will be saved in the submission)

```
get-pending-approval-submission/
```
GET API that allows a reviewer to see which submissions are waiting for approval.


