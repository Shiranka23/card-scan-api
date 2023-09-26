from rest_framework import generics
from .models import CardData
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from uuid import uuid4

from django.http import HttpResponse, HttpResponseNotFound
from pathlib import Path
from os.path import join


# Credentials
API_KEY = config("AZURE_API_KEY")
ENDPOINT = config("AZURE_ENDPOINT")

def get( request, file):
    file_location=join(Path(__file__).resolve().parent.parent, 'media','assets' , file)
    try:    
        with open(file_location, 'rb') as f:
            file_data = f.read()
            ext = file.split(".")[-1]
            response = HttpResponse(content=file_data, content_type=f'image/{ext}')
            return response
    except IOError:
    # handle file not exist case here
        response = HttpResponseNotFound('<h1>File not exist</h1>')
        return response

class TextExtractViewSet(generics.ListAPIView):
    queryset = CardData.objects.all()
    serializer_class = ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Get uploaded file and generate a unique filename
            file = request.data['file']
            filename = file.name
            ext = filename.split('.')[-1]
            file_name = f'{uuid4().hex}.{ext}'
            obj = CardData.objects.create(image=file, name=file_name)
            obj.save()
            image_url = f'/upload/{file_name}'
            current_site = get_current_site(request).domain

            # creating URL of the uploaded image
            formUrls = f'http://{current_site}{image_url}'
            # print(formUrls)

            #  sample docs
            # formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/business-card-english.jpg"
           

            document_analysis_client = DocumentAnalysisClient(
                endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY)
            )

            poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-businessCard", formUrls)
            business_cards = poller.result()
            # print(business_cards)
            card_data = []
            phone_number=[]
            
            # Extract information from the business card
            for idx, business_card in enumerate(business_cards.documents):
                # print("--------Analyzing business card #{}--------".format(idx + 1))
                contact_names = business_card.fields.get("ContactNames")
                if contact_names:
                    for contact_name in contact_names.value:
                        # firstname=[contact_name.value["FirstName"].value if contact_name.value["FirstName"].value else []]
                        # lastname=[contact_name.value["LastName"].value if contact_name.value["LastName"].value else []]
                        if contact_name.value["FirstName"]:
                            # print("firstname: ",contact_name.value["FirstName"].value)
                            firstname=contact_name.value["FirstName"].value
                        else:
                            firstname=" "
                        if contact_name.value["LastName"]:
                            # print("lastname: ",contact_name.value["LastName"].value)
                            lastname=contact_name.value["LastName"].value
                        else:
                            lastname=" "
                        name=firstname+" "+lastname
                else:
                    name=' '
                company_names = business_card.fields.get("CompanyNames")
                if company_names:
                    company=[company_name.value for company_name in company_names.value]
                    # for company_name in company_names.value:
                    # print("company: ",company_name.value)
                        # company = company_name.value
                else:
                    company=''
                departments = business_card.fields.get("Departments")
                if departments:
                    dprmt=[department.value for department in departments.value]
                    # for department in departments.value:
                        # print("department: ",department.value)
                        # dprmt=department.value
                else:
                    dprmt=[]
                job_titles = business_card.fields.get("JobTitles")
                if job_titles:
                    job=[job_title.value for job_title in job_titles.value]
                    # for job_title in job_titles.value:
                        # print("job title: ",job_title.value)
                        # job=job_title.value
                else:
                    job=" "
                emails = business_card.fields.get("Emails")
                if emails:
                    mail=[email.value for email in emails.value]
                    # for email in emails.value:
                        # print("email: ",email.value)
                        # mail=email.value
                else:
                    mail=[]
                websites = business_card.fields.get("Websites")
                if websites:
                    site=[website.value for website in websites.value]
                    # for website in websites.value:
                        # print("website: ",website.value)
                        # site=website.value
                else:
                    site=[]
                addresses = business_card.fields.get("Addresses")
                if addresses:
                    for address in addresses.value:
                        # print("address: ",address.value)
                        add=address.value
                else:
                    add=" "
                mobile_phones = business_card.fields.get("MobilePhones")
                if mobile_phones:
                    for phone in mobile_phones.value:
                        # print("phone: ".phone.content)
                        phone_number.append(phone.content)
                else:
                    phoneNum=[]
                faxes = business_card.fields.get("Faxes")
                if faxes:
                    faxNum=[fax.content for fax in faxes.value]
                    # for fax in faxes.value:
                        # print("fax: ", fax.content)
                        # faxNum=fax.content
                else:
                    faxNum=[]
                work_phones = business_card.fields.get("WorkPhones")
                if work_phones:
                    for work_phone in work_phones.value:
                        # print("work_phone: ",work_phone.content)
                        phone_number.append(work_phone.content)
                else:
                    workPhone=[]
                other_phones = business_card.fields.get("OtherPhones")
                if other_phones:
                    for other_phone in other_phones.value:
                        # print("other phone: ",other_phone.value)
                        phone_number.append(other_phone.value)
                else:
                    otherPhone=[]
               
            card_info={
                "name":name,
                "company":company,
                "address":"add",
                "Phone numbers":phone_number,
                "fax ":faxNum,
                "email":mail,
                "job":job,
                "department":dprmt,
                "website":site,
                "file url":formUrls
            }
            
            card_data.append(card_info)
            response_data = {
                "status_code": 200,
                "message": "Success",
                "data": card_data
            }
            return Response(response_data)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response({"error_message": error_message}, status=500)
