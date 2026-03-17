import mysql.connector

# Connect to MySQL (XAMPP)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = conn.cursor()

# Create Database
cursor.execute("CREATE DATABASE IF NOT EXISTS news_system")
cursor.execute("USE news_system")

# -----------------------------
# UserAccount
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS UserAccount(
    userID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    pwd VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    userType VARCHAR(20),
    accountStatus VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME,
    gender VARCHAR(10),
    dateOfBirth DATE,
    profileImage VARCHAR(255)
)
""")

# -----------------------------
# ArticleCategory
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ArticleCategory(
    categoryID INT AUTO_INCREMENT PRIMARY KEY,
    categoryName VARCHAR(100),
    categoryStatus VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME,
    created_by INT,
    updated_by INT,
    FOREIGN KEY(created_by) REFERENCES UserAccount(userID),
    FOREIGN KEY(updated_by) REFERENCES UserAccount(userID)
)
""")

# -----------------------------
# UserCategoryInterest
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS UserCategoryInterest(
    userInterestID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    categoryID INT,
    FOREIGN KEY(userID) REFERENCES UserAccount(userID),
    FOREIGN KEY(categoryID) REFERENCES ArticleCategory(categoryID)
)
""")

# -----------------------------
# CompanyProfile
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS CompanyProfile(
    profileID INT AUTO_INCREMENT PRIMARY KEY,
    companyName VARCHAR(150),
    description TEXT,
    mission TEXT,
    vision TEXT,
    contactEmail VARCHAR(100),
    contactPhone VARCHAR(20),
    updated_at DATETIME,
    updated_by INT
)
""")

# -----------------------------
# Article
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Article(
    articleID INT AUTO_INCREMENT PRIMARY KEY,
    articleTitle VARCHAR(255),
    content TEXT,
    created_at DATETIME,
    articleStatus VARCHAR(20),
    created_by INT,
    updated_at DATETIME,
    categoryID INT,
    reviewPriority VARCHAR(20),
    credibilityScore FLOAT,
    aiReview TEXT,
    FOREIGN KEY(created_by) REFERENCES UserAccount(userID),
    FOREIGN KEY(categoryID) REFERENCES ArticleCategory(categoryID)
)
""")

# -----------------------------
# ArticleImage
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ArticleImage(
    imageID INT AUTO_INCREMENT PRIMARY KEY,
    articleID INT,
    imageURL VARCHAR(255),
    uploaded_at DATETIME,
    FOREIGN KEY(articleID) REFERENCES Article(articleID)
)
""")

# -----------------------------
# ArticleAnalytics
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ArticleAnalytics(
    analyticsID INT AUTO_INCREMENT PRIMARY KEY,
    articleID INT,
    views INT DEFAULT 0,
    likes INT DEFAULT 0,
    shares INT DEFAULT 0,
    lastUpdated DATETIME,
    FOREIGN KEY(articleID) REFERENCES Article(articleID)
)
""")

# -----------------------------
# Comment
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Comment(
    commentID INT AUTO_INCREMENT PRIMARY KEY,
    articleID INT,
    userID INT,
    commentText TEXT,
    created_at DATETIME,
    commentStatus VARCHAR(20),
    FOREIGN KEY(articleID) REFERENCES Article(articleID),
    FOREIGN KEY(userID) REFERENCES UserAccount(userID)
)
""")

# -----------------------------
# ReportCategory
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ReportCategory(
    reportCategoryID INT AUTO_INCREMENT PRIMARY KEY,
    categoryName VARCHAR(100),
    categoryStatus VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME,
    created_by INT,
    updated_by INT,
    FOREIGN KEY(created_by) REFERENCES UserAccount(userID),
    FOREIGN KEY(updated_by) REFERENCES UserAccount(userID)
)
""")

# -----------------------------
# ReportedArticle
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ReportedArticle(
    reportID INT AUTO_INCREMENT PRIMARY KEY,
    articleID INT,
    author INT,
    userID INT,
    reason INT,
    optionalComment TEXT,
    reported_at DATETIME,
    reportStatus VARCHAR(20),
    reviewed_by INT,
    reviewed_at DATETIME,
    FOREIGN KEY(articleID) REFERENCES Article(articleID),
    FOREIGN KEY(userID) REFERENCES UserAccount(userID),
    FOREIGN KEY(reason) REFERENCES ReportCategory(reportCategoryID)
)
""")

# -----------------------------
# ProductFeature
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS ProductFeature(
    featureID INT AUTO_INCREMENT PRIMARY KEY,
    featureName VARCHAR(100),
    featureDescription TEXT,
    featureImage VARCHAR(255),
    featureStatus VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME
)
""")

# -----------------------------
# Testimonial
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Testimonial(
    testimonial_ID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    rating INT,
    comment TEXT,
    created_at DATETIME,
    semanticScore FLOAT,
    combinedScore FLOAT,
    FOREIGN KEY(userID) REFERENCES UserAccount(userID)
)
""")

# -----------------------------
# SubscriptionPlan
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS SubscriptionPlan(
    planID INT AUTO_INCREMENT PRIMARY KEY,
    planName VARCHAR(100),
    planDescription TEXT,
    price DECIMAL(10,2),
    billingCycle VARCHAR(20),
    planStatus VARCHAR(20)
)
""")

# -----------------------------
# Subscription
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Subscription(
    subscriptionID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    planID INT,
    startDate DATE,
    expireDate DATE,
    billingInfo TEXT,
    status VARCHAR(20),
    FOREIGN KEY(userID) REFERENCES UserAccount(userID),
    FOREIGN KEY(planID) REFERENCES SubscriptionPlan(planID)
)
""")

# -----------------------------
# Session
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Session(
    sessionID INT AUTO_INCREMENT PRIMARY KEY,
    accountID INT,
    accountType VARCHAR(20),
    loginTime DATETIME,
    expiryTime DATETIME,
    sessionStatus VARCHAR(20)
)
""")

# -----------------------------
# Favourite
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Favourite(
    favouriteID INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    articleID INT,
    saved_at DATETIME,
    FOREIGN KEY(userID) REFERENCES UserAccount(userID),
    FOREIGN KEY(articleID) REFERENCES Article(articleID)
)
""")

# -----------------------------
# SystemLog
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS SystemLog(
    logID INT AUTO_INCREMENT PRIMARY KEY,
    accountID INT,
    accountType VARCHAR(20),
    action VARCHAR(255),
    targetID INT,
    targetType VARCHAR(50),
    created_at DATETIME
)
""")

# -----------------------------
# AutoPublishRule
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS AutoPublishRule(
    rule_ID INT AUTO_INCREMENT PRIMARY KEY,
    minCredibilityScore FLOAT,
    updated_at DATETIME,
    ruleStatus VARCHAR(20),
    updated_by INT
)
""")

# -----------------------------
# AIModel
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS AIModel(
    modelID INT AUTO_INCREMENT PRIMARY KEY,
    modelName VARCHAR(100),
    modelVersion VARCHAR(50),
    modelStatus VARCHAR(20),
    trained_at DATETIME,
    deployed_at DATETIME,
    validationScore FLOAT
)
""")

# -----------------------------
# AITrainerAccount
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS AITrainerAccount(
    trainerID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    pwd VARCHAR(255),
    phone VARCHAR(20),
    accountStatus VARCHAR(20)
)
""")

conn.commit()
print("All tables created successfully!")

cursor.close()
conn.close()