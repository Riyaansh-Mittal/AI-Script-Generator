from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import os
# import google.generativeai as genai
from .models import BlogPost
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
# genai.configure(api_key="GEMINI_API_KEY")
# model = genai.GenerativeModel("gemini-1.5-flash")
from openai import OpenAI
client = OpenAI(
  api_key='XAI_API_KEY',
  base_url="https://api.x.ai/v1",
)

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            # Extract data from FormData
            prompt = request.POST.get('prompt', None)  # Text prompt from the form
            link = request.POST.get('link', None)  # External link
            link_name = request.POST.get('link_name', None)  # Name for the external link
            file = request.FILES.get('file', None)  # Uploaded file (PDF/TXT)
            file_name = file.name if file else None
            print(file_name)
        except Exception as e:
            return JsonResponse({'error': f'Invalid data sent: {str(e)}'}, status=400)

        content = ""

        # Fetch content from link if provided
        if link:
            content += fetch_content_from_link(link)

        # Fetch content from file if provided
        if file:
            content += extract_text_from_file(file)

        # Append prompt if provided
        if prompt:
            content += f"\n\n{prompt}"

        # If no content is provided from any source, return an error
        if not content:
            return JsonResponse({'error': "No valid content provided"}, status=400)

        final_content = generate_blog_from_prompt(content)

        if not final_content:
            return JsonResponse({'error': "Failed to generate Script"}, status=500)

        # Save blog article to the database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            generated_content=final_content,
            external_link=link,
            external_link_name=link_name,
            file_name=file_name
        )
        new_blog_article.save()

        # Return generated blog article as a response
        return JsonResponse({'content': final_content, 'id': new_blog_article.id})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def fetch_content_from_link(link):
    """
    Fetches and extracts data from heading tags, p tags, and span tags of an external link (e.g., blog or article).
    """
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data from heading tags (h1 to h6), p tags, and span tags
        extracted_content = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']):
            text = tag.get_text(strip=True)
            if text:  # Add only non-empty text
                extracted_content.append(text)

        # Combine extracted content into a single string
        content = "\n".join(extracted_content)

        return f"Content fetched from: {link}\n\n{content}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching content from {link}: {str(e)}"

def extract_text_from_file(file):
    """
    Extracts text from the uploaded file (PDF, TXT, etc.)
    """
    file_extension = file.name.split('.')[-1].lower()
    file_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    if file_extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == 'txt':
        return extract_text_from_txt(file_path)
    return ""

def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF file """
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_txt(txt_path):
    """ Extracts text from a TXT file """
    try:
        with open(txt_path, 'r') as file:
            text = file.read()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from TXT file: {e}")
        return ""

def generate_blog_from_prompt(content):
    try:
        # response = model.generate_content(content)
        response = client.chat.completions.create(
        model="grok-2-latest",
        messages=[
            {"role": "system", "content": "You are a script writer who creates engaging scripts based on provided content."},
            {"role": "user", "content": content}
        ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating content with Google Gemini: {e}")
        return ""


def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')

