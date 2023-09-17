from rest_framework import generics
from .models import CardData
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from decouple import config
from django.contrib.sites.shortcuts import get_current_site
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import json
from uuid import uuid4


# credentials
API_KEY=config("AZURE_API_KEY")
ENDPOINT=config("AZURE_ENDPOINT")


class TextExtractViewSet(generics.ListAPIView):
    queryset = CardData.objects.all()
    serializer_class = ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        file=request.data['file']
        filename=request.data['file'].name
        ext=filename.split()[-1]
        file_name = '{}.{}'.format(uuid4().hex, ext)
        # print(file_name)
        obj=CardData.objects.create(image=file,name=file_name)
        obj.save()
        print(obj.image.url)
        image_url ='./media/assets/'+str(file_name)
        # image_url ='assets/'+str(file_name)
        current_site=get_current_site(request).domain
        formUrl =str(current_site)+image_url
        print(formUrl)
        form_recognizer_client = FormRecognizerClient(
            endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))
        with open(image_url, "rb") as f:
            try:

                # poller = form_recognizer_client.begin_recognize_business_cards(
                poller = form_recognizer_client.begin_analyze_document_from_url("prebuilt-businessCard", formUrl)
                business_cards = poller.result()
            except:
                return Response({"error_message":"Unable to detect Card. Please place the card properly"})
            print(business_cards[0].fields.keys())
            for idx, business_card in enumerate(business_cards.documents):
                print("--------Analyzing business card #{}--------".format(idx + 1))
                contact_names = business_card.fields.get("ContactNames")
                if contact_names:
                    for contact_name in contact_names.value:
                        contact_names= contact_name.value["FirstName"].value + contact_name.value["LastName"].value
                        print(
                            "Contact Name: {} {}".format(
                                contact_name.value["FirstName"].value,
                                contact_name.value["LastName"].value
                                # contact_name.value[
                                #     "FirstName"
                                # ].confidence,
                            )
                        )
                    
                company_names = business_card.fields.get("CompanyNames")
                if company_names:
                    for company_name in company_names.value:
                        company_names=company_name.value
                        print(
                            "Company Name: {} ".format(
                                company_name.value, #company_name.confidence
                            )
                        )
                departments = business_card.fields.get("Departments")
                if departments:
                    for department in departments.value:
                        departments=department.value
                        print(
                            "Department: {} ".format(
                                department.value, #department.confidence
                            )
                        )
                job_titles = business_card.fields.get("JobTitles")
                if job_titles:
                    for job_title in job_titles.value:
                        job_titles=job_title.value
                        print(
                            "Job Title: {}".format(
                                job_title.value,# job_title.confidence
                            )
                        )
                emails = business_card.fields.get("Emails")
                if emails:
                    for email in emails.value:
                        emails=email.value
                        print(
                            "Email: {} ".format(email.value, #email.confidence 
                                                                )
                        )
                websites = business_card.fields.get("Websites")
                if websites:
                    for website in websites.value:
                        websites=website.value
                        print(
                            "Website: {} ".format(
                                website.value
                            )
                        )
                addresses = business_card.fields.get("Addresses")
                if addresses:
                    for address in addresses.value:
                        addresses=address.value
                        print(
                            "Address: {} ".format(
                                address.value
                            )
                        )
                mobile_phones = business_card.fields.get("MobilePhones")
                if mobile_phones:
                    for phone in mobile_phones.value:
                        mobile_phones=phone.content
                        print(
                            "Mobile phone number: {} ".format(
                                phone.content
                            )
                        )
                faxes = business_card.fields.get("Faxes")
                if faxes:
                    for fax in faxes.value:
                        faxes=fax.content
                        print(
                            "Fax number: {} ".format(
                                fax.content
                            )
                        )
                work_phones = business_card.fields.get("WorkPhones")
                if work_phones:
                    for work_phone in work_phones.value:
                        work_phones=work_phone.content
                        print(
                            "Work phone number: {} ".format(
                                work_phone.content
                            )
                        )
                other_phones = business_card.fields.get("OtherPhones")
                if other_phones:
                    for other_phone in other_phones.value:
                        other_phones=other_phone.value
                        print(
                            "Other phone number: {} ".format(
                                other_phone.value
                            )
                        )
                print("----------------------------------------")
            card_data={
                "Name":contact_names,
                "Company Name":company_names,
                "Department":departments,
                "Job Titles":job_titles,
                "Email":emails,
                "Fax":faxes,
                "Work Number":work_phones,
                "Website":websites,
                "Address":addresses
            }
            data={
                "status code":200,
                "message":"Success",
                "data":card_data
            }
        return Response(data)