from flask import *
import sqlite3
import json
import requests
import time
import random
import re
app = Flask(__name__)

@app.route("/login/",methods=['GET','POST'])
def login():
    note=""
    user=request.args.get("user")
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    try:
        anser=_sql.execute("select passwords from user where username=\""+user+"\";").fetchall()[0][0]
    except:
        pass
    _sql.commit()
    if user=="":
        note=note+"用户名为空"
    _pass=request.args.get("pass")
    if _pass=="":
        note=note+"密码为空"
    if user=="" and _pass=="":
        note=""
    if user!="" and _pass!="":
        if user!=None and _pass!=None:
            try:
                
                if str(_pass) !=str(anser):
                    note="密码错误"
                else:
                    cookies=str(time.time())+str(random.choice('abcdefghijklmnopqrstuvwxyz'))
                    _sql.execute("UPDATE user set cookie=\""+cookies+"\" where username=\"admin\"")
                    _sql.commit()
                    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
                    _sql.close()
                    note=	"<script>alert(\"登录成功！\");\nwindow.location.href='/admin/'</script>"
                    rey=make_response( render_template("login.html",logo=logo,note=note,name=sitname))
                    rey.set_cookie("lg",cookies,max_age=31536000)
                    return rey
            except:
                note="账号不存在"
    _sql.commit()
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _sql.close()
    if note !="":
        note="<div class=\"alert alert-danger\">"+note+"</div>"
    return render_template("login.html",logo=logo,note=note,name=sitname,foot=foot)
@app.route("/ys/")
def ys():
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _sql.close()
    return render_template("ys.html",name=sitname,logo=logo,site=request.url.strip("/ys/"),foot=foot)
@app.route("/")
def index():
    texts=[]
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _text=_sql.execute("select title,describe from blog ;").fetchall()
    _sql.close()
    for i in _text:
        p={}
        p["img"]=json.loads(requests.get("https://api.vvhan.com/api/acgimg?type=json").text)["imgurl"]
        p["title"]=i[0]
        p["describe"]=i[1]
        texts.append(p)
    return render_template("index.html",name=sitname,logo=logo,texts=texts,test="",foot=foot)

@app.route("/admin/")
def admin():
    texts=[]
    fls=[]
    sets=[]
    friends=[]
    act=request.args.get("act")
    t=request.args.get("t")
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    usercookies=request.cookies.get("lg")
    admincookies=_sql.execute("select cookie from user where username=\"admin\"").fetchall()[0][0]
    if usercookies != admincookies:
        return redirect("/login/")
    if act=="sc":
        try:
            _sql.execute("DELETE FROM blog WHERE title = \""+t+"\";")
            _sql.commit()
        except:
            pass
    if act=="scfl":
        try:
            _sql.execute("DELETE FROM fl WHERE fl = \""+t+"\";")
            _sql.commit()
        except:
            pass
    if act=="addfl":
        try:
            _sql.execute("insert into fl values (\""+t+"\");")
            _sql.commit()
        except:
            pass
    if act=="scyl":
         _sql.execute("DELETE FROM friend WHERE name = \""+t+"\";")
         _sql.commit()
    if act=="addyl":
        _sql.execute("insert into friend values (\""+request.args.get("url")+"\",\""+request.args.get("img")+"\",\""+request.args.get("name")+"\",\""+request.args.get("describe")+"\");")
        _sql.commit()
    if act == "setchange":
        logos=request.args.get("logo")
        sitnames=request.args.get("sitname")
        _pass=request.args.get("pass")
        _foot=request.args.get("foot")
        _sql.execute("update sets set setting=\""+logos+"\" where key=\"logo\"")
        _sql.commit()
        _sql.execute("update sets set setting=\""+sitnames+"\" where key=\"sitname\"")
        _sql.commit()
        _sql.execute("update sets set setting=? where key=\"foot\"",(_foot,))
        _sql.commit()
        if _pass != "":
            _sql.execute("update user set passwords=\""+_pass+"\" where username=\"admin\"")
            _sql.commit() 
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _text=_sql.execute("select title,reads,lb from blog ;").fetchall()
    _fls=_sql.execute("select fl from fl ;").fetchall()
    _sets=_sql.execute("select key,setting from sets").fetchall()
    _friends=_sql.execute("select url,img,name,describe from friend").fetchall()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    _sql.close()
    for i in _text:
        datas={}
        datas["title"]=i[0]
        datas["read"]=i[1]
        datas["fl"]=i[2]
        texts.append(datas)
    for i in _fls:
        datas={}
        datas["fl"]=i[0]
        sum=0
        for p in _text:
            if p[2]==i[0]:
                sum+=1
        datas["sum"]=str(sum)
        fls.append(datas)
    for i in _sets:
        datas={}
        datas["set"]=i[0]
        datas["value"]=i[1]
        if i[0]=="logo":
            datas["setname"]="logo"
        if i[0]=="sitname":
            datas["setname"]="站点名"
        if i[0]=="foot":
            datas["setname"]="底部"
            if i[1]==None:
                datas["value"]=""
        sets.append(datas)
    sets.append({"set":"pass","value":"","setname":"管理员密码（空为不修改）"})

    for i in _friends:
        datas={}
        datas["url"]=i[0]
        datas["img"]=i[1]
        datas["name"]=i[2]
        datas["describe"]=i[3]
        friends.append(datas)
    return render_template("admin.html",name=sitname,logo=logo,texts=texts,fls=fls,sets=sets,friends=friends,foot=foot)
@app.route("/friend/")
def friend():
    texts=[]
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _friend=_sql.execute("select url,img,name,describe from friend").fetchall()
    _sql.close()
    for i in _friend:
        datas={}
        datas["url"]=i[0]
        datas["img"]=i[1]
        datas["name"]=i[2]
        datas["describe"]=i[3]
        texts.append(datas)
    return render_template("friend.html",name=sitname,logo=logo,texts=texts,foot=foot)
@app.route("/bj/")
def bj():
    texts=[]
    name=request.args.get("name")
    act=request.args.get("act")
    oldname=request.args.get("oldname")
    describe=request.args.get("describe")
    lb=request.args.get("lb")
    body=request.args.get("body")
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    usercookies=request.cookies.get("lg")
    admincookies=_sql.execute("select cookie from user where username=\"admin\"").fetchall()[0][0]
    if usercookies != admincookies:
        return redirect("/login/")
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    _lb=_sql.execute("select fl from fl")
    if act=="change":
        if oldname=="":
            _sql.execute('insert into blog values (?,?,?,0,?);',(name,describe,body,lb))
            _sql.commit()
        else:
            _sql.execute('update blog set title=?,describe=?,body=?,lb=? where title=?;',(name,describe,body,lb,oldname))
            _sql.commit()
    describe=""
    body=""
    lbs=""

    if name !=None:
        describe=_sql.execute("select describe from blog where title=\""+name+"\"").fetchall()[0][0]
        body=_sql.execute("select body from blog where title=\""+name+"\"").fetchall()[0][0]
        lbs=_sql.execute("select lb from blog where title=\""+name+"\"").fetchall()[0][0]
    else:
        name=""
    for i in _lb:
        datas={}
        datas["lb"]=i[0]
        if lbs!="" and lbs==i[0]:
            datas["checked"]="checked"
        else:
            datas["checked"]=""
        texts.append(datas)

    _sql.close()
    return render_template("bj.html",name=sitname,logo=logo,texts=texts,title=name,describe=describe,body=body,foot=foot)
@app.route("/reader/")
def reader():
    _sql=sqlite3.connect("blog.db")
    _sql.cursor()
    foot=_sql.execute("select setting from sets where key=\"foot\"").fetchall()[0][0]
    if foot==None:
        foot=""
    logo=_sql.execute("select setting from sets where key=\"logo\";").fetchall()[0][0]
    sitname=_sql.execute("select setting from sets where key=\"sitname\";").fetchall()[0][0]
    name=request.args.get("name")
    if name==None:
        return redirect("/")
    body=_sql.execute("select body from blog where title=\""+name+"\"").fetchall()[0][0]
    reads=_sql.execute("select reads from blog where title=\""+name+"\"").fetchall()[0][0]
    lb=_sql.execute("select lb from blog where title=\""+name+"\"").fetchall()[0][0]
    reads=str(int(reads)+1)
    _sql.execute("update blog set reads=\""+reads+"\" where title=\""+name+"\";")
    _sql.commit()
    _sql.close()
    return render_template("reader.html",name=sitname,logo=logo,title=name,reads=reads,body=body,lb=lb,foot=foot)
if __name__ == '__main__':
    app.run(debug=True)