from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.images import ImageFile
from .models import Post, Group, Comment, Follow
import tempfile


class ProfileTest(TestCase):
    def setUp(self):
        self.client_auth = Client()
        self.client_unauth = Client()
        self.user = User.objects.create_user(username='test1', password='trebnhop')
        self.author = User.objects.create_user(username='author', password='authorno1')
        self.group = Group.objects.create(title='test_group', slug='test_group')
        self.post = Post.objects.create(author=self.author, group=self.group, text='Post No 1')
        self.client_auth.force_login(self.user)

    def test_signup(self):
        response = self.client_auth.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        response = self.client_auth.post(reverse('new_post'),
        {'text': 'test post'}, follow=True)
        expected_response = self.client_auth.get(reverse('index')) 
        post = Post.objects.get(author=self.user, text='test post')
        self.assertEqual(response.content, expected_response.content)
        self.assertIn(post, Post.objects.all())

    def test_new_post_unauthorized(self):
        response = self.client_unauth.post(reverse('new_post'),
        {'text': 'test post'}, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
        self.assertEqual(Post.objects.count(), 1)

    def assert_post_view(self, user, post):
        exp_view1 = self.client_auth.get(reverse('index'))
        exp_view2 = self.client_auth.get(reverse('profile', args=[user.username]))
        exp_view3 = self.client_auth.get(reverse('post', args=[user.username, post.id]))
        self.assertContains(exp_view1, post.text)
        self.assertContains(exp_view2, post.text)
        self.assertContains(exp_view3, post.text)


    def test_new_post_view(self):
        post = Post.objects.create(
            text='test post NEW!!!',
            author=self.user,
            group=self.group
        )
        self.assert_post_view(self.user, post)

    def test_edit_post_view(self):
        post = Post.objects.create(
            text='test post NEW!!!',
            author=self.user,
            group=self.group
        )
        self.client.post(
            reverse('post_edit', args=[self.user.username, post.id]),
            {'text': 'test post NEW!!!UPDATE!!!!'}, follow=True
        )
        self.assert_post_view(self.user, post)

    def test_page_not_found_view(self):
        response = self.client_auth.get('testfault')
        self.assertEqual(response.status_code, 404)

    def test_image_view(self):
        post = Post.objects.create(
            text='post with image',
            author=self.user,
            group=self.group,
            image = ImageFile(tempfile.NamedTemporaryFile(), 'test.jpeg')
        )
        exp_view1 = self.client_auth.get(reverse('index'))
        exp_view2 = self.client_auth.get(reverse('profile',
            args=[self.user.username]))
        exp_view3 = self.client_auth.get(reverse('post',
            args=[self.user.username, post.id]))
        exp_view4 = self.client_auth.get(reverse('group',
            args=[self.group.slug]))
        self.assertContains(exp_view1, '<img')
        self.assertContains(exp_view2, '<img')
        self.assertContains(exp_view3, '<img')
        self.assertContains(exp_view4, '<img')

    def test_not_image(self):
        fake_img = tempfile.NamedTemporaryFile()
        self.client_auth.post(reverse('new_post'),
        {'text': 'post without image', 'image': fake_img})
        self.assertEqual(Post.objects.count(), 1)

    def test_follow(self):
        self.client_auth.get(reverse('profile_follow',
            args=[self.author.username]))
        self.assertTrue(Follow.objects.count() == 1)
        self.client_auth.get(reverse('profile_unfollow',
            args=[self.author.username]))
        self.assertTrue(Follow.objects.count() == 0)

    def test_follow_update(self):
        self.client_auth.get(reverse('profile_follow',
            args=[self.author.username]))
        post = Post.objects.create(
            text='Post No 2',
            author=self.author,
            group=self.group
        )
        post.save()
        response = self.client_auth.get(reverse('follow_index'))
        self.assertContains(response, post.text)

    def test_comment(self):
        self.client_auth.post(reverse('add_comment',
            args=[self.author.username, self.post.id]), {'text': 'Comment No 1'})
        self.client_unauth.post(reverse('add_comment',
            args=[self.author.username, self.post.id]), {'text': 'Comment No 2'})
        self.assertEqual(self.post.comments.count(), 1)
