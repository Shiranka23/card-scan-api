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
        formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/business-card-english.jpg"
        # formUrl ="http://"+str(current_site)+image_url
        # print(formUrl)
        document_analysis_client = DocumentAnalysisClient(
            endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY)
        )

        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-businessCard", formUrl)
        business_cards = poller.result()

        for idx, business_card in enumerate(business_cards.documents):
            print("--------Analyzing business card #{}--------".format(idx + 1))
            contact_names = business_card.fields.get("ContactNames")
            if contact_names:
                for contact_name in contact_names.value:
                    print(
                        "Contact First Name: {} has confidence: {}".format(
                            contact_name.value["FirstName"].value,
                            contact_name.value[
                                "FirstName"
                            ].confidence,
                        )
                    )
                    print(
                        "Contact Last Name: {} has confidence: {}".format(
                            contact_name.value["LastName"].value,
                            contact_name.value[
                                "LastName"
                            ].confidence,
                        )
                    )
            company_names = business_card.fields.get("CompanyNames")
            if company_names:
                for company_name in company_names.value:
                    print(
                        "Company Name: {} has confidence: {}".format(
                            company_name.value, company_name.confidence
                        )
                    )
            departments = business_card.fields.get("Departments")
            if departments:
                for department in departments.value:
                    print(
                        "Department: {} has confidence: {}".format(
                            department.value, department.confidence
                        )
                    )
            job_titles = business_card.fields.get("JobTitles")
            if job_titles:
                for job_title in job_titles.value:
                    print(
                        "Job Title: {} has confidence: {}".format(
                            job_title.value, job_title.confidence
                        )
                    )
            emails = business_card.fields.get("Emails")
            if emails:
                for email in emails.value:
                    print(
                        "Email: {} has confidence: {}".format(email.value, email.confidence)
                    )
            websites = business_card.fields.get("Websites")
            if websites:
                for website in websites.value:
                    print(
                        "Website: {} has confidence: {}".format(
                            website.value, website.confidence
                        )
                    )
            addresses = business_card.fields.get("Addresses")
            if addresses:
                for address in addresses.value:
                    print(
                        "Address: {} has confidence: {}".format(
                            address.value, address.confidence
                        )
                    )
            mobile_phones = business_card.fields.get("MobilePhones")
            if mobile_phones:
                for phone in mobile_phones.value:
                    print(
                        "Mobile phone number: {} has confidence: {}".format(
                            phone.content, phone.confidence
                        )
                    )
            faxes = business_card.fields.get("Faxes")
            if faxes:
                for fax in faxes.value:
                    print(
                        "Fax number: {} has confidence: {}".format(
                            fax.content, fax.confidence
                        )
                    )
            work_phones = business_card.fields.get("WorkPhones")
            if work_phones:
                for work_phone in work_phones.value:
                    print(
                        "Work phone number: {} has confidence: {}".format(
                            work_phone.content, work_phone.confidence
                        )
                    )
            other_phones = business_card.fields.get("OtherPhones")
            if other_phones:
                for other_phone in other_phones.value:
                    print(
                        "Other phone number: {} has confidence: {}".format(
                            other_phone.value, other_phone.confidence
                        )
                    )
            print("----------------------------------------")

            card_data = {
                "Name": contact_names,
                "Company Name": company_names,
                "Department": departments,
                "Job Titles": job_titles,
                "Email": emails,
                "Fax": faxes,
                "Work Number": work_phones,
                "Website": websites,
                "Address": addresses
            }
            data = {
                "status code": 200,
                "message": "Success",
                "data": card_data
            }
        return Response(data)
