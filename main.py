from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from tweepy import API, Cursor, OAuthHandler, Stream
from tweepy.streaming import StreamListener
import tweepy
import json

###twitter API Tokens
access_token = "1713619092-rNn56braFDEwRLyAGh9IbWZ8BlqaHqEhYtIx5em"
access_token_secret = "pt3Kevia17SPtO2x7BgrVryi57i4S7snP2fciBKrtxxXa"
consumer_key = "YAPz4IkJ57pW1ODjdgJ1htuob"
consumer_secret = "1M4v1J90uONGrH092pDDbx1wSMjgPX194ZkKJ6TZm7PSXHHg8W"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
tweet_api = tweepy.API(auth, wait_on_rate_limit=True)

### flask and db stuff
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

###Database Tables
#user db table
class UserModel(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    user_is_employer = db.Column(db.Integer, nullable=False) # 1 = Employer, 0 = Job Seeker 
    user_list_of_applications = db.Column(db.String, nullable=True) # comma deliminated list of job_id's
    user_list_of_interviews = db.Column(db.String, nullable=True) # comma deliminated list of job_id's

    def __repr__(self):
        return f"User(name = {name})"

#job posting db table
class JobPostingModel(db.Model):
    __tablename__ = 'JobPostings'
    job_id = db.Column(db.Integer, primary_key=True)
    job_owner = db.Column(db.Integer, nullable=False) # user_id of the owner
    job_title = db.Column(db.String, nullable=False)
    job_description = db.Column(db.String, nullable=True)
    job_list_of_applicants = db.Column(db.String, nullable=True) # comma deliminated list of user_id's
    job_list_of_interviews = db.Column(db.String, nullable=True) # comma deliminated list of user_id's

    def __repr__(self):
        return f"Job(user_id = {job_owner}, title = {job_title}, description = {job_description}, list_of_applicants = {job_list_of_applicants}, list_of_interviews = {job_list_of_interviews})"

###Argument Parseres
#Find Tweets Parser
find_tweets_args = reqparse.RequestParser()
find_tweets_args.add_argument("subject", type=str, help="Subject for the search is required", required=True)
#find_tweets_args.add_argument("startDate", type=str, help="Start date for search is required", required=True)
number_of_tweets_to_find = 10

#User Put Args
user_put_args = reqparse.RequestParser()
user_put_args.add_argument("user_name", type=str, help="User Name is required", required=True)
user_put_args.add_argument("user_is_employer", type=int, help="Is Employer field is required. (0 = Employer, 1 = Job Seeker)", required=True)

#User Patch Args
user_patch_args = reqparse.RequestParser()
user_patch_args.add_argument("user_application", type=str, help="Job ID of the applied job.", required=False)
user_patch_args.add_argument("user_interview", type=str, help="Job ID of the job to interview.", required=False)

#Job Posting Put Args
job_put_args = reqparse.RequestParser()
job_put_args.add_argument("job_owner", type=int, help="User ID of the job owner is required.", required=True)
job_put_args.add_argument("job_title", type=str, help="Job Title is required.", required=True)
job_put_args.add_argument("job_description", type=str, help="Job Description is required.", required=True)

#Job Postings Patch Args
job_patch_args = reqparse.RequestParser()
job_patch_args.add_argument("job_applicant", type=str, help="User ID of job applicant.", required=False)
job_patch_args.add_argument("job_interview", type=str, help="User ID of interviewee.", required=False)

#Job Postings Get Args
job_get_args = reqparse.RequestParser()
job_get_args.add_argument("job_get_flag", type=str, help="Flag Options: 'a' - returns all job postings, 'user_id' - returns that users jobs.", required=True)

###Resource Fields
resource_field_user = {
    'user_id' : fields.Integer,
    'user_name' : fields.String,
    'user_is_employer' : fields.Integer,
    'user_list_of_applications' : fields.String,
    'user_list_of_interviews' : fields.String
}

resource_field_job = {
    'job_id' : fields.Integer,
    'job_owner' : fields.Integer,
    'job_title' : fields.String,
    'job_description' : fields.String,
    'job_list_of_applicants' : fields.String,
    'job_list_of_interviews' : fields.String
}

### Restful Stuff
#twitter scrapper REST
class TwitterScrapper(Resource):
    
    def get(self):
        args = find_tweets_args.parse_args()

        # Creation of query method using parameters
        #tweets = tweepy.Cursor(tweet_api.search,q=args['subject'],geocode="45.501689,-73.567256,300km").items(number_of_tweets_to_find)
        tweets = tweepy.Cursor(tweet_api.search,q=args['subject']).items(number_of_tweets_to_find)
 
        # Pulling information from tweets iterable object
        tweets_list = [[tweet.id, tweet.text, tweet.user.location, tweet.user.screen_name] for tweet in tweets]
        print(tweets_list)
        return json.dumps(tweets_list)
                

#User REST
class User(Resource):
    @marshal_with(resource_field_user)
    def put(self, u_id):
        args = user_put_args.parse_args()
        result = UserModel.query.filter_by(user_id=u_id).first()
        if result:
            abort(409, message="User ID taken.")

        user = UserModel(user_id=u_id, user_name=args['user_name'], user_is_employer=args['user_is_employer'])
        db.session.add(user)
        db.session.commit()
        return user, 201

    @marshal_with(resource_field_user)
    def patch(self, u_id):
        args = user_patch_args.parse_args()
        result = UserModel.query.filter_by(user_id=u_id).first()
        if not result:
            abort(404, message="User ID not founnd. Cannot Update.")

        if args['user_application']:
            if result.user_list_of_applications:
                result.user_list_of_applications = result.user_list_of_applications + "," + args['user_application']
            else:
                result.user_list_of_applications = args['user_application']
        
        if args['user_interview']:
            if result.user_list_of_interviews:
                result.user_list_of_interviews = result.user_list_of_interviews + "," + args['user_interview']
            else:
                result.user_list_of_interviews = args['user_interview']    

        db.session.commit()

        return result

#Job REST
class Job(Resource):
    @marshal_with(resource_field_job)
    def get(self,j_id):
        args = job_get_args.parse_args()
        if args['job_get_flag'] == "a":
            jobs = JobPostingModel.query.all()

        elif intTryParse(args['job_get_flag']):
            user = UserModel.query.filter_by(user_id=int(args['job_get_flag'])).first()
            if not user:
                abort(404, message="User ID does not exist.")

            elif user.user_is_employer == 1:
                jobs = JobPostingModel.query.filter_by(job_owner=int(args['job_get_flag'])).first()

            else:
                jobs = JobPostingModel.query.filter(JobPostingModel.job_list_of_applicants.contains(args['job_get_flag']))

        else:
            abort(422, message="Flag is incorrect. Flag Options: 'a' - returns all job postings, 'user_id' - returns that users jobs.")


        return jobs

    @marshal_with(resource_field_job)
    def put(self, j_id):
        args = job_put_args.parse_args()
        result = JobPostingModel.query.filter_by(job_id=j_id).first()
        if result:
            abort(409, message="Job ID already exsists. Job not Created.")
        
        job = JobPostingModel(job_id=j_id, job_owner=args['job_owner'], job_title=args['job_title'], job_description=args['job_description'])
        db.session.add(job)
        db.session.commit()
        return job, 201

    @marshal_with(resource_field_job)
    def patch(self, j_id):
        args = job_patch_args.parse_args()
        result = JobPostingModel.query.filter_by(job_id=j_id).first()
        if not result:
            abort(404, message="Job ID doesnt exist. Job not Updated.")
        
        if args['job_applicant']:
            if result.job_list_of_applicants:
                result.job_list_of_applicants = result.job_list_of_applicants + "," + args['job_applicant']
            else:
                result.job_list_of_applicants = args['job_applicant']
        
        if args['job_interview']:
            if result.job_list_of_interviews:
                result.job_list_of_interviews = result.job_list_of_interviews + "," + args['job_interview']
            else:
                result.job_list_of_interviews = args['job_interview'] 

        db.session.commit()
        return result



#twitter search target
api.add_resource(TwitterScrapper, "/twittersearch/")

#user target
api.add_resource(User, "/user/<int:u_id>")

#job target
api.add_resource(Job, "/job/<int:j_id>")

#int parser
def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

#degub MODE
if __name__ == "__main__":
    app.run(debug=True)