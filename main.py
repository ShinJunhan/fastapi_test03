# main.py

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

# fastapi 객체 생성
app = FastAPI()
# jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")

'''
    # 클라이언트가 서버에 요청하는 방식
        1) get : 주소창에 직접 입력 또는 링크 클릭을 통해 요청
        2) post : 
        3) put
        4) delete
        5) patch
'''
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        # 응답에 필요한 data를 context 로 전달할 수 있다
        context={
            "fortuneToday":"동쪽으로 가면 귀인을 만나요"
        }
    )

# get 방식 /posts 요청 처리
@app.get("/post", response_class=HTMLResponse)
def getPosts(request: Request, db:Session = Depends(get_db)):
    # DB에서 글목록이 있으면 가져오기 위한 sql 문 준비
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        ORDER BY num DESC
    """)
    # 글 목록을 얻어와서
    result = db.execute(query)
    posts = result.fetchall()
    # 응답하기
    return templates.TemplateResponse(
        request=request,
        name="post/list.html", # templates/post/list.html jinja2 를 해석한 결과를 응답
        context={
            "posts":posts
        }
    )

@app.get("/post/new", response_class=HTMLResponse)
def postNewForm(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")

@app.post("/post/new")
def postNew(writer: str = Form(...), title: str = Form(...), content: str = Form(...),
            db: Session = Depends(get_db)):
    # DB에 저장할 sql 문 준비
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()

    # 특정 경로로 요청을 다시 하도록 리다이렉트 응답을 준다.
    return RedirectResponse("/post", status_code=302)
    