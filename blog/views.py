from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View

from .models import Category, Topic, Post, User
from .form import NewCategoryForm, NewTopicForm, PostForm, EditCategory, EditTopicForm


def index(request):
    categories = Category.objects.all()
    return render(request, 'blog/index.html', {'categories': categories})


@login_required(login_url='/auth/login/')
def new_category(request):
    if request.method == 'POST':
        form = NewCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog:index')
    else:
        form = NewCategoryForm()
    return render(request, 'blog/new_category.html', {'form': form})


@login_required
def delete_category(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    category.delete()
    return redirect('blog:index')


@login_required
def edit_category(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    if request.method == 'POST':
        form = EditCategory(request.POST)
        if form.is_valid():
            category.name = form.cleaned_data.get('name')
            category.description = form.cleaned_data.get('description')
            category.save()
            return redirect('blog:index')
    else:
        form = EditCategory()
    return render(request, 'blog/edit_category.html', {'form': form, 'category_pk': category_pk})


def topics(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    queryset = category.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    return render(request, 'blog/topics.html', {'topics': topics, 'category': category})


@login_required
def new_topic(request, category_pk):
    category = get_object_or_404(Category, pk=category_pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.starter = request.user
            topic.save()
            Post.objects.create(topic=topic, message=form.cleaned_data.get('message'),
                                created_by=request.user)
            return redirect('blog:topic_posts', category_pk=category.pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'blog/new_topic.html', {'form': form, 'category': category})


class TopicPosts(View):
    form_class = PostForm

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, category__pk=self.kwargs['category_pk'], pk=self.kwargs['topic_pk'])
        form = PostForm()
        # Using session to control view counting system
        session_key = 'viewed_topic_{}'.format(topic.pk)
        if not request.session.get(session_key, False):
            topic.views += 1
            topic.save()
            request.session[session_key] = True
        queryset = topic.posts.order_by('id')
        first_post = queryset.first()
        # Paginate posts
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/topic_posts.html', {'form': form,
                                                         'topic': topic,
                                                         'posts': posts,
                                                         'first_post': first_post})

    def post(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, category__pk=self.kwargs['category_pk'], pk=self.kwargs['topic_pk'])
        form = PostForm(request.POST)
        post = form.save(commit=False)
        post.topic = topic
        if self.request.user.is_authenticated:
            post.created_by = self.request.user
        else:
            guest = User.objects.get(username='Guest')
            post.created_by = guest
            post.custom_name = form.cleaned_data['created_by']
            post.site = form.cleaned_data['site']
            post.email = form.cleaned_data['email']
        post.save()
        # Update 'last_updated' column
        topic.last_updated = timezone.now()
        topic.save()
        # Go to last post after reply
        topic_url = reverse('blog:topic_posts', kwargs={'category_pk': self.kwargs['category_pk'],
                                                        'topic_pk': self.kwargs['topic_pk']})
        topic_post_url = '{url}?page={page}#{id}'.format(
            url=topic_url,
            id=post.pk,
            page=topic.get_page_count()
        )
        return redirect(topic_post_url)


def reply_topic(request, category_pk, topic_pk):
    topic = get_object_or_404(Topic, category__pk=category_pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            # Update 'last_updated' column
            topic.last_updated = timezone.now()
            topic.save()
            # Go to last post after reply
            topic_url = reverse('blog:topic_posts', kwargs={'category_pk': category_pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'blog/reply_topic.html', {'form': form, 'topic': topic})


@login_required
def edit_topic(request, category_pk, topic_pk):
    topic = get_object_or_404(Topic, category__pk=category_pk, pk=topic_pk)
    if request.method == 'POST':
        form = EditTopicForm(request.POST)
        if form.is_valid():
            topic.subject = form.cleaned_data.get('subject')
            topic.save()
            return redirect('blog:topics', category_pk=category_pk)
    else:
        form = EditTopicForm()
    return render(request, 'blog/edit_topic.html', {'form': form, 'category_pk': category_pk, 'topic_pk': topic_pk})


@login_required
def delete_topic(request, category_pk, topic_pk):
    topic = get_object_or_404(Topic, category__pk=category_pk, pk=topic_pk)
    topic.delete()
    return redirect('blog:topics', category_pk=category_pk)


@login_required
def delete_post(request, category_pk, topic_pk, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    post.delete()
    return redirect('blog:topic_posts', category_pk=category_pk, topic_pk=topic_pk)


@login_required
def edit_post(request, category_pk, topic_pk, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post.updated_by = request.user
            post.updated_at = timezone.now()
            post.message = form.cleaned_data.get('message')
            post.save()
            return redirect('blog:topic_posts', category_pk=category_pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})
