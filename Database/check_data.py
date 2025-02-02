import pandas as pd

def count_nan_users(df, column_name):
    return df[column_name].isna().sum()

def count_total_users(df, column_name):
    return df[column_name].nunique()

if __name__ == "__main__":
    all_proposals = pd.read_csv('data/all_proposals.csv')
    all_projects = pd.read_csv('data/all_projects.csv')
    all_comments = pd.read_csv('data/all_comments.csv')

    proposal_users = all_proposals[['Author']].rename(columns={'Author': 'username'})
    proposal_users['verified_status'] = 'not verified'

    # print(proposal_users)
    print(f"Number of NaN users in proposals: {count_nan_users(proposal_users, 'username')}")
    print(f"Number of NaN users in comments: {count_nan_users(all_comments, 'Username')}")
    print(f"Total number of users in proposals: {count_total_users(proposal_users, 'username')}")
    print(f"Total number of users in comments: {count_total_users(all_comments, 'Username')}")
    # print(f"Number of NaN: {count_nan_users(all_projects, 'Project Titlef')}")


    proposal_users = all_proposals[['Author']].rename(columns={'Author': 'username'})
    proposal_users['verified_status'] = 'not verified'
    
    comment_users = all_comments[['Username']].rename(columns={'Username': 'username'})
    comment_users['verified_status'] = 'not verified'
    
    users = pd.concat([proposal_users, comment_users]).fillna('Unknown').drop_duplicates()
    print(f"Total number of unique users: {users['username'].nunique()}")




    #125
