"""
This code sample shows Prebuilt Business Card operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
# endpoint = "09ac8dbcca144ea5bf73de60b3948294"
endpoint = "https://biz-card.cognitiveservices.azure.com/"
key = "09ac8dbcca144ea5bf73de60b3948294"

# sample document
# formUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/business-card-english.jpg"
formUrl ="https://imagetolink.com/ib/gw9fThY2Lw.jpg"
# imageUrl ="http://127.0.0.1:8000/bizcard.jpg"

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
# imageUrl ="http://127.0.0.1:8000/bizcard.jpg"
poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-businessCard", formUrl)
business_cards = poller.result()

for idx, business_card in enumerate(business_cards.documents):
    print("--------Analyzing business card #{}--------".format(idx + 1))
    contact_names = business_card.fields.get("ContactNames")
    if contact_names:
        for contact_name in contact_names.value:
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
            print(
                "Company Name: {} ".format(
                    company_name.value, #company_name.confidence
                )
            )
    departments = business_card.fields.get("Departments")
    if departments:
        for department in departments.value:
            print(
                "Department: {} ".format(
                    department.value, #department.confidence
                )
            )
    job_titles = business_card.fields.get("JobTitles")
    if job_titles:
        for job_title in job_titles.value:
            print(
                "Job Title: {}".format(
                    job_title.value,# job_title.confidence
                )
            )
    emails = business_card.fields.get("Emails")
    if emails:
        for email in emails.value:
            print(
                "Email: {} ".format(email.value, #email.confidence 
                                                      )
            )
    websites = business_card.fields.get("Websites")
    if websites:
        for website in websites.value:
            print(
                "Website: {} ".format(
                    website.value
                )
            )
    addresses = business_card.fields.get("Addresses")
    if addresses:
        for address in addresses.value:
            print(
                "Address: {} ".format(
                    address.value
                )
            )
    mobile_phones = business_card.fields.get("MobilePhones")
    if mobile_phones:
        for phone in mobile_phones.value:
            print(
                "Mobile phone number: {} ".format(
                    phone.content
                )
            )
    faxes = business_card.fields.get("Faxes")
    if faxes:
        for fax in faxes.value:
            print(
                "Fax number: {} ".format(
                    fax.content
                )
            )
    work_phones = business_card.fields.get("WorkPhones")
    if work_phones:
        for work_phone in work_phones.value:
            print(
                "Work phone number: {} ".format(
                    work_phone.content
                )
            )
    other_phones = business_card.fields.get("OtherPhones")
    if other_phones:
        for other_phone in other_phones.value:
            print(
                "Other phone number: {} ".format(
                    other_phone.value
                )
            )
    print("----------------------------------------")
