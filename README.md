# Introduction
This application shows the user the questions and answers appearing in an Amazon product's Questions and Answers section.
The necessary information is the product's asin, **a 10 character long identifier**, which can be found in the product's URL.

**Examples:**
- in the following URL: https://www.amazon.com/Echo-Dot/dp/B07FZ8S74R,
  B07FZ8S74R is the product's asin.
- in the following URL: https://www.amazon.com/gp/product/B08BHZ4MHF,
  B08BHZ4MHF is the product's asin.

# Running the Application
In order to run the application, follow these steps:
1. Go to the directory in which you would like to download the application.
2. Clone the repository.
3. Go to the downloaded directory.
4. Install the required packages.
5. Run the application.
6. Copy the URL from the last line, and paste it in a browser (works on Chrome, Firefox and Edge).
7. Enter the desired asin in the box.
8. Press the *Submit Query* button.
9. Enjoy the Q&A!

These are the relevant terminal/command prompt commands for steps 2-5, respectively:

git clone https://github.com/Gil3co/AmazonQandA.git

cd AmazonQandA

pip install -r requirements.txt

flask run
