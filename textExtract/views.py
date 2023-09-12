from rest_framework import generics
from .models import CardData
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from decouple import config
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
        image_url ='./media/assets/'+str(file_name)
        # image_url ='assets/'+str(file_name)
        form_recognizer_client = FormRecognizerClient(
            endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))
        with open(image_url, "rb") as f:
            try:
                poller = form_recognizer_client.begin_recognize_business_cards(
                    business_card=f, locale="en-US")
                business_cards = poller.result()
            # print(business_cards)
            except:
                return Response({"error_message":"Unable to detect Card. Please place the card properly"})
        for idx, business_card in enumerate(business_cards):
            # print("--------Recognizing business card #{}--------".format(idx +
            #                                                              1))
            contact_names = business_card.fields.get("ContactNames")
            if contact_names:
                for contact_name in contact_names.value:
                    name=contact_name.value["FirstName"].value+contact_name.value["LastName"].value
                    # print("Contact Name: {}{}".format(
                    #     contact_name.value["FirstName"].value,contact_name.value["LastName"].value ))
            else:
                name=''
        
            company_names = business_card.fields.get("CompanyNames")
            if company_names:
                for company_name in company_names.value:
                    company=company_name.value
                    # print("Company Name: {}".format(
                    #     company_name.value))
            else:
                company=''
            departments = business_card.fields.get("Departments")
            if departments:
                for department in departments.value:
                    dprmt=department.value
                    # print("Department: {}".format(
                    #     department.value))
            else:
                dprmt=''
            job_titles = business_card.fields.get("JobTitles")
            if job_titles:
                for job_title in job_titles.value:
                    job=job_title.value
                    # print("Job Title: {}".format(
                    #     job_title.value))
            else:
                job=''
            emails = business_card.fields.get("Emails")
            if emails:
                for email in emails.value:
                    mail=email.value
                    # print("Email: {}".format(
                    #     email.value))
            else:
                mail=''
            websites = business_card.fields.get("Websites")
            if websites:
                for website in websites.value:
                    site=website.value
                    # print("Website: {}".format(
                    #     website.value))
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
                    number=phone.value
                    # print("Mobile phone number: {}".format(
                    #     phone.value))
            else:
                number=''
            faxes = business_card.fields.get("Faxes")
            if faxes:
                for fax in faxes.value:
                    faxNum=fax.value
                    # print("Fax number: {}".format(
                    #     fax.value))
            else:
                faxNum=''
            work_phones = business_card.fields.get("WorkPhones")
            if work_phones:
                for work_phone in work_phones.value:
                    workPhone=work_phone.value
                    # print("Work phone number: {}".format(
                    #     work_phone.value))
            other_phones = business_card.fields.get("OtherPhones")
            if other_phones:
                for other_phone in other_phones.value:
                    otherPhone=other_phone.value
                    # print("Other phone number: {}".format(
                    #     other_phone.value))
            else:
                other_phone=''
            card_data={
                "Name":name,
                "Company Name":company,
                "Department":dprmt,
                "Email":mail,
                "Fax":faxNum,
                "Work Number":number,
                "Website":site,
                "Address":add
            }
            data={
                "status code":200,
                "message":"Success",
                "data":card_data
            }
        return Response(data)