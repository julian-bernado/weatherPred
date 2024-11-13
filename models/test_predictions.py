import pandas as pd

row1 = [i*10 for i in range(10)]
row2 = [j/8 for j in range(10, 20)]

df_dict = {
        "dog": row1,
        "cat": row2
        }

df = pd.DataFrame(data = df_dict)

df.to_csv("predictions/test_predictions.csv")
