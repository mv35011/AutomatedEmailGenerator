from django.shortcuts import render, redirect
from .llm_mechs import Chain
from .portfolio import Portfolio
from .utils import clean_text
from langchain_community.document_loaders import WebBaseLoader
from django.urls import reverse
import markdown
import re

def home(request):

    return redirect(reverse('members:generate_email'))


def generate_email(request):
    generated_email = ""
    error_message = ""

    if request.method == 'POST':
        try:
            website_url = request.POST.get('website_url')

            loader = WebBaseLoader(website_url)
            pages = loader.load()
            cleaned_text = clean_text(pages[0].page_content)

            chain = Chain()
            portfolio = Portfolio()

            jobs = chain.extract_jobs(cleaned_text)
            if jobs:
                relevant_links = portfolio.query_link(jobs[0].get('skills', ''))

                raw_email = chain.write_mail(jobs[0], relevant_links)


                escaped_email = raw_email.replace('<', '&lt;').replace('>', '&gt;')

                processed_email = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped_email)

                processed_email = processed_email.replace('\n', '<br>')

                generated_email = processed_email
            else:
                error_message = "No job information could be extracted from the provided URL."

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"

    return render(request, 'members/email_generator.html', {
        'generated_email': generated_email,
        'error_message': error_message
    })