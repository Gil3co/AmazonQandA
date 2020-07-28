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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36", }


def get_QandA(s, url):
    """
    Uses the session to request the content of the given URL, in order to
    find the questions and answers of the relevant Amazon product.
    :param s: the session
    :param url: the requested URL
    :return: a list of tuples, each containing a single question and a
    single answer
    """
    Result = namedtuple("Result", "question answer")
    s.headers = HEADERS
    s.post(url)
    first_tries = 0
    first_res = []
    while not first_res and first_tries < 5:  # requests sometimes don't work
        #  on the first try, so several tries might be necessary in order to
        # get the content of the URL
        first_response = s.get(url)
        first_soup = BeautifulSoup(first_response.text, PARSER)
        # answers are not found on the page's URL, but are lazy loaded,
        # so in order to get the questions and answers, one must find the next
        # link and request its content
        first_res = first_soup.find_all("div", {"class": LAZY_LOAD_CLASS})
        first_tries += 1
    if first_tries == 5:
        return []

    next_url = first_res[0].contents[1].attrs["href"]
    next_tries = 0
    raw_results = []
    while not raw_results and next_tries < 5:
        next_response = s.get(next_url)
        next_soup = BeautifulSoup(next_response.text, PARSER)
        raw_results = next_soup.find_all("div", {"class": RAW_RESULTS_CLASS,
                                                 "style": RAW_RESULTS_STYLE})
        next_tries += 1
    if next_tries == 5:
        return []
    # at this point raw_results should contain the raw questions and answers
    results = []
    for tag in raw_results:
        # each tag contains a single question and its answer (if it exists)
        q = tag.find_all("span", {"class": QUESTION_CLASS})
        if not q:  # might return an empty list -> no question in this tag
            continue
        question = q[0].text.strip()
        raw_answer = tag.find_all("div", {"class": RAW_ANSWERS_CLASS,
                                          "style": RAW_ANSWERS_STYLE})
        if not len(raw_answer) > 1:  # if len == 1, there is no answer
            continue

        # answers might be long, and therefore the page itself contains a
        # "see more" option. if so, the the next line would return the raw
        # answer itself.
        ans2 = raw_answer[1].find_all("span", {"class": LONG_ANSWER_CLASS})
        if not ans2:
            answer = raw_answer[1].find("span").text.strip()
        else:
            answer = ans2[0].text.strip()
        results.append(Result(question=question, answer=answer))
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
def asin():
    form = QandAForm()
    if form.validate_on_submit():
        return redirect(url_for('query', given_asin=form.asin.data))
    return render_template('QandA.html', title="asin", form=form)
