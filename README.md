# FYP-26-S1-02
News Release System Design and Implementation. Today's news release system is different from traditional media. Traditional media mainly focus on dissemination of news information, while modern news release systems not only offer users the ability to read and browse news content, but also allow users to express their views and to communicate with other users. The system function can be divided into two main components, which are a management part and a display part. The news release system should allow the non-registered users to read news articles. But for non-registered users, they will not be able to comment on the news. If a registered user logs in, they will be allowed to comment on news articles, publish their own news pieces, and share the updates with other users in real-time. Additionally, ordinary registered users can manage their personal news articles. These articles can also be subject to management by the administrator, which ensures the security and standardisation of the system

## HOW TO RUN DATABASE ##
1. Install Python MySQL Connector
pip install mysql-connector-python

2. Run the file in cmd. (see where u locate ur file)

3. It is put in github alr. 
—> cd C:\Users\babyc\Documents\GitHub\FYP-26-S1-02
—> python create_database.py
—> expected output: All tables created successfully!

4. open XAMPP → phpMyAdmin 
will see the database (news_system)

## HOW TO INSTALL FLASK ##
pip install flask mysql-connector-python

## HOW TO RUN THE APP ##
python app.py
http://127.0.0.1:5000

## HOW TO INSTALL TEXTBLOB ##
pip install textblob
python -m textblob.download_corpora