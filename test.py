from unittest import TestCase
from app import app
from models import db, User, Post, Tag

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogley3_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


db.drop_all()
db.create_all()

class UserRouteTest(TestCase):

    def setUp(self):       
        
        Post.query.delete() 
        User.query.delete()    
        Tag.query.delete()    
                      

        user= User(first_name='Jason', last_name='Smith', img_url='https://b.fssta.com/uploads/application/soccer/headshots/884.vresize.350.350.medium.61.png')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user = user
        
        
        post = Post(title = 'Dinner Idea', content = 'Shrimp Tacos', user_id=self.user_id)
        db.session.add(post)
        db.session.commit()

        self.post_id = post.id
        self.post = post

        tag = Tag(name="Happy")
        db.session.add(tag)
        db.session.commit()

        self.tag = tag
        self.tag_id = tag.id

    def tearDown(self):
        db.session.rollback()

    
    def test_users_page(self):
        with app.test_client() as client:
            res = client.get('/users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code,200)
            self.assertIn('<h1>Users</h1>', html)

    def test_user_info(self):
        with app.test_client() as client:
            res = client.get(f'users/{self.user_id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h3>Jason Smith</h3>',html)
            self.assertIn(self.user.img_url, html)

    def test_add_user(self):
        with app.test_client() as client:
            data = {'first_name': 'John', 'last_name':'Adams', 'img_url':'www.img.com'}
            res = client.post("/users/new", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)            
            self.assertEqual(res.status_code, 200)
            self.assertIn(self.user.full_name, html)

    def test_delete_user(self):
        with app.test_client() as client:
            data = {'first_name': 'Sergio', 'last_name':'Ramos', 'img_url':'https://b.fssta.com/uploads/application/soccer/headshots/884.vresize.350.350.medium.61.png'}
            res=client.post(f'/users/{self.user_id}/delete', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            user = User.query.get(self.user_id)
            self.assertNotIn('Sergio Rams',html)

    def test_create_post(self):
        with app.test_client() as client:
            data = {'title':'Books to Read', 'content':'The Alchemist'}
            print(f'*********USER ID {self.user_id} {self.user.first_name}')
            res = client.post(f'/users/{self.user_id}/posts/new', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(self.post.title,html)


    def test_edit_post(self):
        with app.test_client() as client:
            data = {'title':'Dinner Idea', 'content':'Pizza'}            
            res = client.get(f'posts/{self.post_id}/edit', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertIn(self.post.content,html)            
       

    def delete_post(self):
        with app.test_client() as client:
            data = {'title':'Books to Read', 'content':'The Alchemist, Why We Sleep, Who Moved My Cheese'}

            res = client.post(f'/posts/{self.post_id}/delete', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertNotIn('Books to Read',html)

    def test_tag_list(self):
        with app.test_client() as client:
            res = client.get('/tags')
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('<li>Happy</li>', html)

    
 
          

