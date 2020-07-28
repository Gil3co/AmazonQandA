from flask import render_template, redirect, url_for
from app import app
from app.forms import QandAForm
from bs4 import BeautifulSoup
import requests
from collections import namedtuple

GENERIC_AMAZON_URL = "https://www.amazon.com/gp/product/{}"
RESULT_ERROR = "A problem with the query has occurred. <br> This is the " \
               "given asin: {}. If this is a correct asin, please refresh the " \
               "page. Otherwise, go back and insert a correct asin."
PARSER = "html.parser"
LAZY_LOAD_CLASS = "cdQuestionLazySeeAll"
RAW_RESULTS_CLASS = "a-fixed-left-grid-col a-col-right"
RAW_RESULTS_STYLE = "padding-left:1%;float:left;"
QUESTION_CLASS = "a-declarative"
RAW_ANSWERS_CLASS = "a-fixed-left-grid-col a-col-right"
RAW_ANSWERS_STYLE = "padding-left:0%;float:left;"
LONG_ANSWER_CLASS = "noScriptDisplayLongText"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
}

def get_QandA(s, url):
    ret = []
    Result = namedtuple("Result", "question answer")
    s.headers = HEADERS
    s.post(url)
    tries = 0
    while not ret and tries < 5:
        response = s.get(url)
        soup = BeautifulSoup(response.text, PARSER)
        ret = soup.find_all("div", {"class": LAZY_LOAD_CLASS})
        tries += 1
    if tries == 5:
        return []
    next_link = ret[0].contents[1].attrs["href"]
    next_response = s.get(next_link)
    next_soup = BeautifulSoup(next_response.text, PARSER)
    raw_results = next_soup.find_all("div", {"class": RAW_RESULTS_CLASS,
                                             "style": RAW_RESULTS_STYLE})
    results = []
    for tag in raw_results:
        try:
            q = tag.find_all("span", {"class": QUESTION_CLASS})
            if not q:
                continue
            question = q[0].text.strip()
            raw_answers = tag.find_all("div", {"class": RAW_ANSWERS_CLASS,
                                               "style": RAW_ANSWERS_STYLE})
            if not len(raw_answers) > 1:
                continue

            ans2 = raw_answers[1].find_all("span", {"class":
                                                            LONG_ANSWER_CLASS})
            if not ans2:
                answer = raw_answers[1].find("span").text.strip()
            else:
                answer = ans2[0].text.strip()
            results.append(Result(question=question, answer=answer))
        except:
            continue
    return results


@app.route("/query/<given_asin>")
def query(given_asin):
    with requests.Session() as s:
        url = GENERIC_AMAZON_URL.format(given_asin)
        results = get_QandA(s, url)
    if not results:
        return RESULT_ERROR.format(given_asin)
    return render_template("query_result.html", results=results,
                           asin=given_asin)


@app.route('/', methods=['GET', 'POST'])
# @app.route('/asin', methods=['GET', 'POST'])
def asin():
    form = QandAForm()
    if form.validate_on_submit():
        return redirect(url_for('query', given_asin=form.asin.data))
    return render_template('QandA.html', title="asin", form=form)
