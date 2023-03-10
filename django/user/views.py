from django.shortcuts import render, get_object_or_404, redirect

# from django.http import HttpResponse
# Create your views here.
from .models import Question
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .forms import QuestionForm, AnswerForm

# from django.http import HttpResponseNotAllowed
from django.core.paginator import Paginator  # 페이징 라이브러리
from django.contrib.auth.decorators import (
    login_required,
)  # @login_required 애너테이션이 붙은 함수는 로그인이 필요한 함수를 의미


def index(request):
    page = request.GET.get("page", "1")  # 페이지
    question_list = Question.objects.order_by("-create_date")
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {"question_list": page_obj}
    return render(request, "user/question_list.html", context)


@csrf_exempt
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    context = {"question": question}
    return render(request, "user/question_detail.html", context)


@login_required(login_url="common:login")  # 로그아웃인 상태에서 작성시 로그인화면으로
def answer_create(request, question_id):
    # question = get_object_or_404(Question, pk=question_id)
    # question.answer_set.create(content=request.POST.get('content'), create_date=timezone.now())
    # return redirect('user:detail', question_id=question.id)
    # -----------------위나 아래와 같은 방식으로도 사용 가능----------------
    # question = get_object_or_404(Question, pk=question_id)
    # answer = Answer(question=question, content=request.POST.get('content'), create_date=timezone.now())
    # answer.save()
    # return redirect('user:detail', question_id=question.id)
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user  # author 속성에 로그인 계정 저장
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect("user:detail", question_id=question.id)
    else:
        form = AnswerForm()  # 로그아웃시에 답변을 등록하더라도 오류가 안생기고 상세화면으로 돌아감 아래는 오류발생시키는 코드
        # return HttpResponseNotAllowed('Only POST is possible.')
    context = {"question": question, "form": form}
    return render(request, "user/question_detail.html", context)


@login_required(login_url="common:login")  # 로그아웃인 상태에서 작성시 로그인화면으로
def question_create(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():  # 폼이 유효하다면
            question = form.save(commit=False)  # 임시 저장하여 question 객체를 리턴받는다.
            question.author = request.user  # author 속성에 로그인 계정 저장
            question.create_date = timezone.now()  # 실제 저장을 위해 작성일시를 설정한다.
            question.save()  # 데이터를 실제로 저장한다.
            return redirect("user:index")
    else:
        form = QuestionForm()
    context = {"form": form}
    return render(request, "user/question_form.html", context)
