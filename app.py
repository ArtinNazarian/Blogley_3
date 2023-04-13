from flask import Flask, request, redirect, render_template
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUT_TB_INTERCEPT_REDIRECTS']=False

connect_db(app)
app.app_context().push()

# GET /
@app.route("/")
def home():    
    return redirect("/users")

# GET /users  display list of user 
@app.route("/users")
def users():
    users = User.query.order_by(User.first_name, User.last_name).all()   
    return render_template("user.html", users=users)

# GET /users/new show an add form 
@app.route("/users/new", methods=["GET"])
def add_form():
    return render_template("new_user.html")

# POST /users/new  add new users form
@app.route("/users/new", methods=["POST"])
def new_user():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    img_url = request.form['img_url']

    new_user = User(first_name=first_name, last_name=last_name, img_url=img_url)
    db.session.add(new_user)
    db.session.commit()

    return redirect ("/users")

# GET /users/[user-id] show user information
@app.route('/users/<int:user_id>')
def users_show(user_id):
    user = User.query.get_or_404(user_id)
        
    return render_template('user_info.html', user=user)



#GET /users/[user-id]/edit show user edit page
@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_edit.html', user=user)

 
#POST /users/[user-id]/edit edit user information
@app.route("/users/<int:user_id>/edit", methods=["POST"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.img_url = request.form["img_url"]

    db.session.add(user)
    db.session.commit()

    return redirect("/users")

#POST /users/[user-id]/delete delete a user from db
@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect ("/users")

#***********************************************
# Post route

@app.route('/users/<int:user_id>/posts/new')
def user_post_form(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('post_form.html', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def new_post(user_id):
    """Get data from new post form"""
    user = User.query.get_or_404(user_id)
    title = request.form['title']
    content = request.form['content'] 

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=title, content=content, user=user, tags=tags)

    db.session.add(new_post)
    db.session.commit()  

    return redirect(f"/users/{user_id}")


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """Show a specific post"""
    post = Post.query.get_or_404(post_id)
    
    return render_template('post_show.html', post=post)

@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    """show post edit form"""
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('post_edit.html', post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_post(post_id):
    """Update post"""
    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Delete user's post"""
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
  
    return redirect(f'/users/{post.user_id}')


#***********************************************************************
#Tags

@app.route('/tags')
def show_tags():
    """Show list of tags"""
    tags = Tag.query.all()
    return render_template('tag_list.html', tags=tags)

@app.route('/tags/new')
def tag_form():
    """Display new tag form"""
    post = Post.query.all()
    return render_template('tag_add.html')

@app.route('/tags/new', methods=["POST"])
def tag_form_new():
    """read data from tag form"""
    post_ids=[]
    for num in request.form.getlist("posts"):
        post_ids.append(num)
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    name = request.form['tag-name']

    new_tag = Tag(name=name, posts=posts)
    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>')
def tag_info(tag_id):
    """Show details about a tag"""
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_info.html', tag=tag)

@app.route('/tags/<int:tag_id>/edit')
def tag_edit(tag_id):
    """tag edit form"""
    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tag_edit.html',tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tag_edit_post(tag_id):
    post_ids=[]
    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['tag-name']
    for num in request.form.getlist("posts"):
        post_ids.append(num)       
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()
    
    db.session.add(tag)
    db.session.commit()

    return redirect('/tags')

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tag_delete(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect('/tags')




