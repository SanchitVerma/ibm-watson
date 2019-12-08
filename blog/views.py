from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from ibm_watson.tone_analyzer_v3 import ToneInput


authenticator = IAMAuthenticator('A9XFIAUkUL3c-hdjiAcS4jWysL1e2LzAqsSY2PH70xDw')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator
)

language_translator.set_service_url('https://gateway.watsonplatform.net/language-translator/api')
language_translator.set_disable_ssl_verification(True)


authenticator = IAMAuthenticator('CsOX8usWo11kTjTA1u17vrqZn1YJVNjPDZaWLo4FuN4i')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

tone_analyzer.set_service_url('https://gateway.watsonplatform.net/tone-analyzer/api')
tone_analyzer.set_disable_ssl_verification(True)


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text

        translation = language_translator.translate(
            text=post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        print(obj)
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']

        tone_input = ToneInput(post.text)
        tone = tone_analyzer .tone(tone_input=tone_input, content_type="application/json")
        tone2 = str(tone)
        # post.tone3 = (tone2[1:500])
        # print(post.tone3)
        json_data = json.loads(tone2)
        # print(json_data)
        try:
            post.json_score1 = json_data['result']['document_tone']['tones'][0]['score']
            post.json_name1 = json_data['result']['document_tone']['tones'][0]['tone_name']
            post.json_score2 = json_data['result']['document_tone']['tones'][1]['score']
            post.json_name2 = json_data['result']['document_tone']['tones'][1]['tone_name']

        except:
            pass

        post.tone3 = (tone2[1:500])
        # print(post.tone3)

    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    # form = PostForm()
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
