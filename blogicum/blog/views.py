from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User


class IndexList(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    ordering = ('-pub_date',)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(comment_count=Count('comment'))
        return queryset.select_related(
            'author', 'location', 'category'
        ).filter(is_published=True,
                 category__is_published=True,
                 pub_date__lte=timezone.now())


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('blog:profile')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class CategoryList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        return category.posts.select_related(
            'author', 'location', 'category'
        ).filter(is_published=True, pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(
            Category.objects.values('id', 'title', 'description').filter(
                is_published=True
            ),
            slug=self.kwargs['category_slug'],
        )
        context['category'] = category
        return context


class ProfileList(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs['username']
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            queryset = Post.objects.filter(author=self.author)
        else:
            queryset = super().get_queryset().filter(author=self.author)
        queryset = queryset.annotate(comment_count=Count('comment'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        context['user'] = self.request.user
        return context


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class CommentAdd(LoginRequiredMixin, CreateView):
    post_obj = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "id"
    template_name = "blog/comment.html"
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        comment_pk = self.kwargs.get(self.pk_url_kwarg)
        author = get_object_or_404(self.model, pk=comment_pk).author
        if author != self.request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        self.post_data = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, args, **kwargs)

    def get_success_url(self):
        pk = self.post_data.pk
        return reverse("blog:post_detail", kwargs={"pk": pk})


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        comment_pk = self.kwargs.get(self.pk_url_kwarg)
        author = get_object_or_404(self.model, pk=comment_pk).author
        if author != self.request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        self.post_data = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})
