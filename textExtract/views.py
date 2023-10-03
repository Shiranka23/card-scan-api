from rest_framework import generics
from rest_framework.response import Response

from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.sites.shortcuts import get_current_site

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

import json
import logging
from os.path import join
from pathlib import Path
from decouple import config

# ise delete krna hai
from PIL import Image

from .models import CardData
from .serializers import ImageUploadSerializer
from .decoder import decode_base64_file


# Credentials
API_KEY = config("AZURE_API_KEY")
ENDPOINT = config("AZURE_ENDPOINT")

def get( request, file):
    file_location=join(Path(__file__).resolve().parent.parent, 'media','assets' , file)
    try:    
        with open(file_location, 'rb') as f:
            file_data = f.read()
            ext = file.split(".")[-1]
            # print(ext)
            response = HttpResponse(content=file_data, content_type=f'image/{ext}')
            return response
    except IOError:
    # handle file not exist case here
        response = HttpResponseNotFound('<h1>File not exist</h1>')
        return response


def analyze_business_card(form_urls):
    try:
        document_analysis_client = DocumentAnalysisClient(
            endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY)
        )

        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-businessCard", form_urls)
        business_cards = poller.result()

        card_data = []

        for idx, business_card in enumerate(business_cards.documents):
            contact_names = business_card.fields.get("ContactNames")
            name = ""
            if contact_names:
                for contact_name in contact_names.value:
                    if contact_name.value.get("FirstName"):
                        firstname = contact_name.value["FirstName"].value
                    else:
                        firstname = " "
                    if contact_name.value.get("LastName"):
                        lastname = contact_name.value["LastName"].value
                    else:
                        lastname = " "
                    name = firstname + " " + lastname
            else:
                name = ' '

            company_names = business_card.fields.get("CompanyNames")
            company = [company_name.value for company_name in company_names.value] if company_names else []

            departments = business_card.fields.get("Departments")
            dprmt = [department.value for department in departments.value] if departments else []

            job_titles = business_card.fields.get("JobTitles")
            job = [job_title.value for job_title in job_titles.value] if job_titles else []

            emails = business_card.fields.get("Emails")
            mail = [email.value for email in emails.value] if emails else []

            websites = business_card.fields.get("Websites")
            site = [website.value for website in websites.value] if websites else []

            addresses = business_card.fields.get("Addresses")
            add =[address.content for address in addresses.value ]  if addresses else " "


            mobile_phones = business_card.fields.get("MobilePhones")
            phone_number = [phone.content for phone in mobile_phones.value] if mobile_phones else []

            faxes = business_card.fields.get("Faxes")
            faxNum = [fax.content for fax in faxes.value] if faxes else []

            work_phones = business_card.fields.get("WorkPhones")
            workPhone = [work_phone.content for work_phone in work_phones.value] if work_phones else []

            other_phones = business_card.fields.get("OtherPhones")
            otherPhone = [other_phone.value for other_phone in other_phones.value] if other_phones else []

            card_info = {
                "name": name,
                "company": company,
                "address": add,
                "phoneNumbers": phone_number,
                "fax": faxNum,
                "email": mail,
                "job": job,
                "department": dprmt,
                "website": site,
            }

            card_data.append(card_info)

        return card_data
    except Exception as e:
        raise e


class TextExtractViewSet(generics.ListAPIView):
    queryset = CardData.objects.all()
    serializer_class = ImageUploadSerializer

    def post(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            # Get base64 image string and generate a unique filename
            data = json.loads(request.body.decode('utf-8'))
            photo = data.get('picture')
            image = photo.get('photo')
            file, file_name = decode_base64_file(image)
            file_size = Image.open(file)
            width, height = file_size.size

            # Create a CardData object and save the image
            obj = CardData.objects.create(image=file, name=file_name)
            obj.save()
            image_url = f'/upload/{file_name}'
            current_site = get_current_site(request).domain

            # Creating URL of the uploaded image
            form_urls = f'http://{current_site}{image_url}'

            # Analyze the business card using Azure Document Analysis
            card_data = analyze_business_card(form_urls)

            # Delete the CardData object and its associated image
            instance = CardData.objects.get(name=file_name)
            instance.image.delete()
            instance.delete()

            response_data = {
                "status_code": 200,
                "message": "Success",
                "data": card_data
            }
            return Response(response_data)
        except Exception as e:
            error_message = str(e)
            logger.error(str(e), exc_info=True, stacklevel=2)
            return Response({"error_message": error_message}, status=500)