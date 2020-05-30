from app import app
from app import db, user_datastore, security

from flask import render_template, request, redirect, url_for, flash
from flask_security import login_required, SQLAlchemySessionUserDatastore, utils

from app.models import Post, Tag, User, db_commit
from .forms import PostForm, TagForm, UserForm, RegistrationForm


@app.route('/') # індексна сторінка
@app.route('/index')
def index():
    name = 'Yuriy'
    return render_template('index.html', name=name)

@app.route('/news') # сторінка новин
def news():
    # фільтруємо новини за пошуком
    q = request.args.get('search')

    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)) #.all()
    else:
        posts = Post.query.order_by(Post.created.desc())

    page = request.args.get('page')

    # пагінація сторінок новин
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = posts.paginate(page=page, per_page=7)

    return render_template('news.html', posts=posts, pages=pages)

# http://localhost/post/<Post slug>
@app.route('/post/<slug>') # сторінка поста
def post_detail(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    return render_template('post_detail.html', post=post, tags=tags)

# http://localhost/tag/<Tag slug>
@app.route('/tag/<slug>') # Сторінка новин за тагом
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug==slug).first()
    for i in tag.posts:
        print(i)
    posts = tag.posts
    return render_template('tag_detail.html', posts=posts, tag=tag)

# http://localhost/register
# сторінка генерації реєстрації користувача
@app.route('/register', methods=['GET', 'POST'])  
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        username = request.form['username']
        password = utils.encrypt_password(request.form['password'])
        active = True
        user_datastore.create_user(name=name, email=email, phone=phone, username=username, password=password, active=active)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
                
        return redirect(url_for('security.login'))
    
    name_form = 'user'
    title = 'Register new user'
    form = RegistrationForm()    

    return render_template('create_form.html', form=form, form_type=name_form, title=title)

# http://localhost/create/<form-name> 
# сторінка генерації форм відповідно моделей у forms.py
@app.route('/create/<name_form>', methods=['GET', 'POST'])  
@login_required
def create_form(name_form):
    if request.method == 'POST':
        if name_form == 'post':
            title = request.form['title']
            body = request.form['body']

            post = Post(title=title, body=body)
            db_commit(data=post)

        elif name_form == 'tag':
            name = request.form['name']
            
            tag = Tag(name=name)
            db_commit(data=tag)
        
        return redirect(url_for('news'))

    if name_form == 'post':
        form = PostForm()
        title = 'Create news'
    elif name_form == 'tag':
        form = TagForm()
        title = 'Create new tag'
    else:
        return redirect(url_for('news'))

    return render_template('create_form.html', form=form, form_type=name_form, title=title)
