import twfy
import pandas as pd

from sqlalchemy import create_engine


if __name__ == "__main__":
    # engine = create_engine('sqlite:///C:/Users/Jon/Workspace/llm-quantitative-text-mining/data/discordia.db', echo=False)

    # df_debates = pd.read_sql_table('debates', engine)

    list_urls = ["https://www.theyworkforyou.com/debates/?id=2023-11-14b.534.3", "https://www.theyworkforyou.com/debates/?id=2023-11-15b.674.3"]
    df_speeches, df_house_division, df_votes = twfy.get_speeches_divisions_and_votes(list_urls)

    print(df_speeches.shape)
    print(df_votes.shape)