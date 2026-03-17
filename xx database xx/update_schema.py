import mysql.connector
from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="news_system"
    )


ALTER_QUERIES = [
    "ALTER TABLE `UserAccount`pyt CHANGE `created_at` `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `UserAccount` CHANGE `updated_at` `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE `UserAccount` CHANGE `accountStatus` `accountStatus` ENUM('Active','Suspended') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Active'",

    "ALTER TABLE `AIModel` CHANGE `trained_at` `trained_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `AIModel` CHANGE `deployed_at` `deployed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `AIModel` CHANGE `modelStatus` `modelStatus` ENUM('Active','Archived') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Active'",

    "ALTER TABLE `Article` CHANGE `articleTitle` `articleTitle` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Article` CHANGE `content` `content` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Article` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `Article` CHANGE `articleStatus` `articleStatus` ENUM('Active','Suspended','Draft') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Article` CHANGE `created_by` `created_by` INT(11) NOT NULL",
    "ALTER TABLE `Article` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",

    "ALTER TABLE `ArticleAnalytics` CHANGE `lastUpdated` `lastUpdated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",

    "ALTER TABLE `ArticleCategory` CHANGE `categoryName` `categoryName` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ArticleCategory` CHANGE `categoryStatus` `categoryStatus` ENUM('Active','Inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Active'",
    "ALTER TABLE `ArticleCategory` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `ArticleCategory` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE `ArticleCategory` CHANGE `updated_by` `updated_by` INT(11) NOT NULL",
    "ALTER TABLE `ArticleCategory` CHANGE `created_by` `created_by` INT(11) NOT NULL",

    "ALTER TABLE `ArticleImage` CHANGE `uploaded_at` `uploaded_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",

    "ALTER TABLE `AutoPublishRule` CHANGE `minCredibilityScore` `minCredibilityScore` FLOAT NOT NULL",
    "ALTER TABLE `AutoPublishRule` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE `AutoPublishRule` CHANGE `ruleStatus` `ruleStatus` ENUM('Active','Archived') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `AutoPublishRule` CHANGE `updated_by` `updated_by` INT(11) NOT NULL",

    "ALTER TABLE `Comment` CHANGE `articleID` `articleID` INT(11) NOT NULL",
    "ALTER TABLE `Comment` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `Comment` CHANGE `commentText` `commentText` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Comment` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",

    "ALTER TABLE `CompanyProfile` CHANGE `companyName` `companyName` VARCHAR(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `description` `description` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `mission` `mission` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `vision` `vision` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `contactEmail` `contactEmail` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `contactPhone` `contactPhone` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `CompanyProfile` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE `CompanyProfile` CHANGE `updated_by` `updated_by` INT(11) NOT NULL",

    "ALTER TABLE `Favourite` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `Favourite` CHANGE `articleID` `articleID` INT(11) NOT NULL",
    "ALTER TABLE `Favourite` CHANGE `saved_at` `saved_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",

    "ALTER TABLE `ProductFeature` CHANGE `featureName` `featureName` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ProductFeature` CHANGE `featureDescription` `featureDescription` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ProductFeature` CHANGE `featureImage` `featureImage` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ProductFeature` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `ProductFeature` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",

    "ALTER TABLE `ReportCategory` CHANGE `categoryName` `categoryName` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ReportCategory` CHANGE `categoryStatus` `categoryStatus` ENUM('Active','Inactive') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'Active'",
    "ALTER TABLE `ReportCategory` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `ReportCategory` CHANGE `updated_at` `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "ALTER TABLE `ReportCategory` CHANGE `created_by` `created_by` INT(11) NOT NULL",
    "ALTER TABLE `ReportCategory` CHANGE `updated_by` `updated_by` INT(11) NOT NULL",

    "ALTER TABLE `ReportedArticle` CHANGE `articleID` `articleID` INT(11) NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `author` `author` INT(11) NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `reason` `reason` INT(11) NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `reported_at` `reported_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "ALTER TABLE `ReportedArticle` CHANGE `reportStatus` `reportStatus` ENUM('Completed','Pending Review') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `reviewed_by` `reviewed_by` INT(11) NOT NULL",
    "ALTER TABLE `ReportedArticle` CHANGE `reviewed_at` `reviewed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",

    "ALTER TABLE `Subscription` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `Subscription` CHANGE `planID` `planID` INT(11) NOT NULL",
    "ALTER TABLE `Subscription` CHANGE `startDate` `startDate` DATE NOT NULL",
    "ALTER TABLE `Subscription` CHANGE `expireDate` `expireDate` DATE NOT NULL",
    "ALTER TABLE `Subscription` CHANGE `billingInfo` `billingInfo` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Subscription` CHANGE `status` `status` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",

    "ALTER TABLE `SubscriptionPlan` CHANGE `planName` `planName` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `SubscriptionPlan` CHANGE `planDescription` `planDescription` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `SubscriptionPlan` CHANGE `price` `price` DECIMAL(10,2) NOT NULL",
    "ALTER TABLE `SubscriptionPlan` CHANGE `billingCycle` `billingCycle` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `SubscriptionPlan` CHANGE `planStatus` `planStatus` VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",

    "ALTER TABLE `SystemLog` CHANGE `accountID` `accountID` INT(11) NOT NULL",

    "ALTER TABLE `Testimonial` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `Testimonial` CHANGE `rating` `rating` INT(11) NOT NULL",
    "ALTER TABLE `Testimonial` CHANGE `comment` `comment` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `Testimonial` CHANGE `created_at` `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",

    "ALTER TABLE `UserAccount` CHANGE `username` `username` VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `UserAccount` CHANGE `email` `email` VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `UserAccount` CHANGE `pwd` `pwd` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `UserAccount` CHANGE `userType` `userType` ENUM('System Admin','Premium','Free','AI Trainer') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL",
    "ALTER TABLE `UserAccount` CHANGE `gender` `gender` ENUM('Male','Female') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL",

    "ALTER TABLE `UserCategoryInterest` CHANGE `userID` `userID` INT(11) NOT NULL",
    "ALTER TABLE `UserCategoryInterest` CHANGE `categoryID` `categoryID` INT(11) NOT NULL",
]


def run_migration():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for i, query in enumerate(ALTER_QUERIES, start=1):
            try:
                print(f"Running {i}/{len(ALTER_QUERIES)}:")
                print(query)
                cursor.execute(query)
                conn.commit()
                print("✅ Success\n")
            except Error as e:
                print(f"❌ Failed: {e}\n")
                conn.rollback()

    except Error as e:
        print(f"Database connection error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    run_migration()
