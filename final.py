import pandas as pd
import json
import random
import os

def format_movie_reviews_for_evaluate(fname: str) -> pd.DataFrame: 
    """ Format the movie reviews data for `evaluate` mode with `NLPScholar`

    Parameters:
        fname (str): The name of movie review csv file
    Returns:
        pd.DataFrame: The data in a dataframe with the correct format for
                    NLPScholar

    format_movie_reviews_for_evaluate('final_data/imbd_movie_reviews.csv`')
    should yield a dataframe whose first lines should have this template: 

           id                                               text sentiment
    0       0  One of the other reviewers has mentioned that ...  positive
    1       1  A wonderful little production. The filming tec...  negative


    """
    data = []

    with open(fname, 'r', encoding='utf-8') as file:
        # Assuming the CSV file has columns 'review' and 'sentiment'
        df = pd.read_csv(file)

        for idx, row in df.iterrows():
            text = row['review'].replace('<br />', ' ').strip()
            sentiment = row['sentiment']

            data.append({
                'id': idx,
                'text': text,
                'sentiment': sentiment
            })

    formatted_df = pd.DataFrame(data)
    return formatted_df

def format_fashion_reviews_for_evaluate(fname: str) -> pd.DataFrame: 
    """ Format the movie reviews data for `evaluate` mode with `NLPScholar`

    Parameters:
        fname (str): The name of fashion reviews json file
    Returns:
        pd.DataFrame: The data in a dataframe with the correct format for
                    NLPScholar

    format_fashion_reviews_for_evaluate('final_data/amazon_fashion_reviews.csv`')
    should yield a dataframe whose first lines should have this template: 

           id                                               text sentiment
    0       0  Great product and price!                           positive
    1       1  Stays vibrant after many washes                    negative

    """
    data = []

    with open(fname, 'r', encoding='utf-8') as file:
        for idx, line in enumerate(file):
            review = json.loads(line.strip())

            # Extract necessary fields
            review_text = review.get("reviewText")
            overall = review.get("overall")

            # Skip if reviewText is missing
            if not review_text:
                continue

            # Determine sentiment based on overall rating
            if overall in [1.0, 2.0]:
                sentiment = "negative"
            elif overall == 3.0:
                sentiment = "neutral"
            elif overall in [4.0, 5.0]:
                sentiment = "positive"
            else:
                continue

            data.append({
                "id": idx,
                "text": review_text.strip(),
                "sentiment": sentiment
            })

    formatted_df = pd.DataFrame(data)
    return formatted_df

def format_financial_news_for_evaluate(fname: str) -> pd.DataFrame:
    """ Format the financial news data for `evaluate` mode with `NLPScholar`

    Parameters:
        fname (str): The name of the financial news CSV file
    Returns:
        pd.DataFrame: The data in a dataframe with the correct format for
                      NLPScholar

    Example:
    format_financial_news_for_evaluate('final_data/financial_news.csv')
    should yield a dataframe whose first lines look like:

           id                                               text sentiment
    0       0  The stock market crashed today due to weak ec...  negative
    1       1  The company reported record profits this quar...  positive
    """
    df = pd.read_csv(fname, header=None, names=["sentiment", "text"], encoding='latin-1')

    data = []

    for idx, row in df.iterrows():
        sentiment = row['sentiment'].strip().lower()
        text = row['text'].strip()

        # Skip rows with missing text or sentiment
        if not sentiment or not text:
            continue

        data.append({
            "id": idx,
            "text": text,
            "sentiment": sentiment
        })

    formatted_df = pd.DataFrame(data)
    return formatted_df


def inject_spelling_errors(formatted_df: pd.DataFrame, degree: int) -> pd.DataFrame:
    """
    Inject spelling errors into the `text` column of the input dataframe based on the severity of errors.
    
    Parameters:
        formatted_df (pd.DataFrame): The df containing the columns id, text, and sentiment.
        degree (int): 1 (light), 2 (moderate), 3 (extreme).
    
    Returns:
        pd.DataFrame: The dataframe with spelling errors introduced into the `text` column.
    """
    def introduce_error(word, severity):
        if len(word) < 2:  # Skip very short words
            return word
        
        error_type = random.choice(["substitution", "transposition", "omission", "duplication", "scramble"])
        
        if error_type == "substitution":
            idx = random.randint(0, len(word) - 1)
            replacement = random.choice("abcdefghijklmnopqrstuvwxyz")
            word = word[:idx] + replacement + word[idx + 1:]
        
        elif error_type == "transposition" and len(word) > 2:
            idx = random.randint(0, len(word) - 2)
            word = word[:idx] + word[idx + 1] + word[idx] + word[idx + 2:]
        
        elif error_type == "omission":
            idx = random.randint(0, len(word) - 1)
            word = word[:idx] + word[idx + 1:]
        
        elif error_type == "duplication":
            idx = random.randint(0, len(word) - 1)
            word = word[:idx] + word[idx] * 2 + word[idx + 1:]
        
        elif error_type == "scramble" and severity == 3:
            word = ''.join(random.sample(word, len(word)))  # Shuffle all characters
        
        # For extreme errors, apply multiple modifications
        if severity == 3 and random.random() < 0.5:
            word = introduce_error(word, severity)
        elif severity == 2 and random.random() < 0.2:
            word = introduce_error(word, severity)
        
        return word

    def add_errors_to_text(text, degree):
        words = text.split()
        
        if degree == 1:
            num_words_to_modify = max(1, len(words) // 50)  # ~2% of words
        elif degree == 2:
            num_words_to_modify = max(1, len(words) // 10)  # ~10% of words
        elif degree == 3:
            num_words_to_modify = max(1, len(words) // 5)  # ~20% of words
        
        for _ in range(num_words_to_modify):
            idx = random.randint(0, len(words) - 1)
            words[idx] = introduce_error(words[idx], degree)
        
        return " ".join(words)

    modified_df = formatted_df.copy()
    modified_df["text"] = modified_df["text"].apply(lambda x: add_errors_to_text(x, degree))
    return modified_df


    


if __name__ == "__main__":

    #testing formatting functions
    test_file = "final_data/imdb_movie_reviews.csv"
    formatted_df = format_movie_reviews_for_evaluate(test_file)
    print(formatted_df.head())

    test_file2 = "final_data/amazon_fashion_reviews.json"
    formatted_df2 = format_fashion_reviews_for_evaluate(test_file2)
    print(formatted_df2.head())

    test_file3 = "final_data/financial_news_sentiment.csv"
    formatted_df3 = format_financial_news_for_evaluate(test_file3)
    print(formatted_df3.head())


    #testing spelling error function and helper functions
    modified_df = inject_spelling_errors(formatted_df, 1)
    modified_df2 = inject_spelling_errors(formatted_df, 2)
    modified_df3 = inject_spelling_errors(formatted_df, 3)
    print(modified_df.head())
    print(modified_df2.head())
    print(modified_df3.head())

    modified_df["condition"] = "test"
    modified_df.rename(columns={"id": "textid"}, inplace=True)
    modified_df.rename(columns={"sentiment": "target"}, inplace=True)
    modified_df.to_csv("evaluation_data/modified_imdb_reviews.tsv", sep="\t", index=False)
    




