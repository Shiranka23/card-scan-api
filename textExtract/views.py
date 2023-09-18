from rest_framework import generics
from .models import CardData
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient, DocumentAnalysisClient

import json
from uuid import uuid4


# credentials
API_KEY = config("AZURE_API_KEY")
ENDPOINT = config("AZURE_ENDPOINT")


class TextExtractViewSet(generics.ListAPIView):
    queryset = CardData.objects.all()
    serializer_class = ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        file = request.data['file']
        filename = request.data['file'].name
        ext = filename.split()[-1]
        file_name = '{}.{}'.format(uuid4().hex, ext)
        obj = CardData.objects.create(image=file, name=file_name)
        obj.save()
        image_url = './media/assets/'+str(file_name)
        current_site = get_current_site(request).domain
        # sample document
        # formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/business-card-english.jpg"
        formUrl ="http://"+str(current_site)+image_url
        # formUrl ='https://mikesblog.com/wp-content/uploads/2019/10/shad-mike-michelini-chinese-business-card.jpg'
        # print(formUrl)
        try:
            document_analysis_client = DocumentAnalysisClient(
                endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY)
            )
            poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-businessCard", formUrl)
            business_cards = poller.result()
        except:
            return({"error_message":"Please place your card properly.."})
        for idx, business_card in enumerate(business_cards.documents):
            # print("--------Analyzing business card #{}--------".format(idx + 1))
            contact_names = business_card.fields.get("ContactNames")
            if contact_names:
                for contact_name in contact_names.value:
                    print(
                        "Contact First Name: {} ".format(
                            contact_name.value["FirstName"].value,
                        )
                    )
                    name=contact_name.value["FirstName"].value+contact_name.value['LastName'].value
                    print(
                        "Contact Last Name: {} ".format(
                            contact_name.value["LastName"].value,
                        )
                    )
            else:
                name=''
                    
            company_names = business_card.fields.get("CompanyNames")
            if company_names:
                for company_name in company_names.value:
                    print(
                        "Company Name: {} ".format(
                            company_name.value
                        )
                    )
                    company=company_name.value
            else:
                company=''
            departments = business_card.fields.get("Departments")
            if departments:
                for department in departments.value:
                    print(
                        "Department: {} ".format(
                            department.value
                        )
                    )
                    dprmt=department.value
            else:
                dprmt=''
            job_titles = business_card.fields.get("JobTitles")
            if job_titles:
                for job_title in job_titles.value:
                    print(
                        "Job Title: {} ".format(
                            job_title.value
                        )
                    )
                    job=job_title.value
            else:
                job=''
            emails = business_card.fields.get("Emails")
            if emails:
                for email in emails.value:
                    print(
                        "Email: {} ".format(email.value)
                    )
                    mail=email.value
            else:
                mail=''
            websites = business_card.fields.get("Websites")
            if websites:
                for website in websites.value:
                    print(
                        "Website: {} ".format(
                            website.value
                        )
                    )
                    site=website.value
            else:
                site=''
            addresses = business_card.fields.get("Addresses")
            if addresses:
                for address in addresses.value:
                    add=address.value
                    # print("Address: {}".format(
                    #     address.value))
            else:
                add=''
                    
            mobile_phones = business_card.fields.get("MobilePhones")
            if mobile_phones:
                for phone in mobile_phones.value:
                    print(
                        "Mobile phone number: {} ".format(
                            phone.content
                        )
                    )
                    phone=phone.content
            else:
                phone=''
            faxes = business_card.fields.get("Faxes")
            if faxes:
                for fax in faxes.value:
                    print(
                        "Fax number: {} ".format(
                            fax.content
                        )
                    )
                    faxNum=fax.content
            else:
                faxNum=''
            work_phones = business_card.fields.get("WorkPhones")
            if work_phones:
                for work_phone in work_phones.value:
                    print(
                        "Work phone number: {} ".format(
                            work_phone.content
                        )
                    )
                    workPhone=work_phone.content
            workPhone=''
            other_phones = business_card.fields.get("OtherPhones")
            if other_phones:
                for other_phone in other_phones.value:
                    print(
                        "Other phone number: {} ".format(
                            other_phone.value
                        )
                    )
                    otherPhone=other_phone.value
            else:
                otherPhone=''
            print("----------------------------------------")

            card_data = {
                "Name": name,
                "Company Name": company,
                "Department": dprmt,
                "Job Titles": job,
                "Email": mail,
                "Fax": faxNum,
                "Work Number": phone,
                "Other Number": otherPhone,
                "Website": site,
                # "Address": add
            }
            # card_data=json.dumps(card_data, default=str)
            # card_data=json.load(card_data)
            # print(card_data)
            data = {
                "status code": 200,
                "message": "Success",
                "data": card_data
            }
        return Response(data)
