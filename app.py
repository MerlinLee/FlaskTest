import os

from flask import Flask, make_response, request, render_template, flash, redirect, url_for, request, send_from_directory, send_file, jsonify,abort,send_from_directory
from flask_login import current_user, login_user, logout_user, login_required, login_manager, LoginManager
import time
import os
from werkzeug.utils import secure_filename
import base64
from models import User

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF','mp4'])


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
# 用户记录表
users = [
    {'username': 'Tom', 'password': '111111'},
    {'username': 'Michael', 'password': '123456'}
]

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]
# 通过用户名，获取用户记录，如果不存在，则返回None
def query_user(username):
    for user in users:
        if user['username'] == username:
            return user

# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
@login_manager.user_loader
def load_user(username):
    if query_user(username) is not None:
        curr_user = User()
        curr_user.id = username
        return curr_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_info = request.form.to_dict()
    current_user = User()
    current_user.id = user_info.get("username")
    if current_user.is_authenticated:
        return "Authenticated User"
    if request.method == "POST":
        login_user(current_user)
        return user_info.get("username")

@app.route("/api/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        abort(404)

@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        token = base64.b64encode(b'new_filename').decode('ascii')
        print('/api/download/' + new_filename)
        return jsonify({'code': 0, 'errmsg': "上传成功", 'token': token, 'fileName': '/api/download/' + new_filename})
    else:
        return jsonify({"code": 1001, "errmsg": "上传失败"})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user = User(request.form['username'], request.form['password'])
        flash('User successfully registered')
        return request.form['username']
@login_required
@app.route('/forget', methods=['POST'])
def forget():
    email_info = request.form.to_dict()
    return jsonify({'response': 'False'})



if __name__ == '__main__':
    app.run(debug=True)


