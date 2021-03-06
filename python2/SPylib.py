import time, random, cPickle, sys, tweepy

def test(api):
	public_tweets = api.home_timeline()
	for tweet in public_tweets:
		print tweet.text

def getIds():
	try:
		with open("tweets.csv", "r") as t:
			lines = t.read()

		lines = lines.replace('"', '')
		lines = lines.split("\n")

		with open("ids.txt", "w") as id:
			for line in lines:
				line = line.split(",")
				if line[0].isdigit():
					id.write(line[0]+"\n")
				try:
					if line[6].isdigit():
						id.write(line[6]+"\n")
				except IndexError:
					continue

	except FileNotFoundError as e:
		print "You have to ask twitter for the file of tweets (Go to your twitter's configuration) and put it in this folder"
		sys.exit(1)

def limit_handled(cursor):
	while True:
		try:
			yield cursor.next()
		except tweepy.RateLimitError:
			print "Rate limit reached wait 15 minutes..."
			time.sleep(15*60)
		except tweepy.TweepError:
			print "Make sure you have a stable connection to Internet..."
			time.sleep(5)

def delTweetsFromFile(api):
	''' You have to download the file twitter provides with all the tweet you've made and put it on this folder '''
	getIds()
	with open("ids.txt", "r") as leTweets:
		a = leTweets.read()

	a = a.split("\n")

	num = 0
	for i in a:
		try:
			api.destroy_status(str(i))
			num+=1
			print "Done #%d" % num
		except Exception as e:
			num+=1
			print e
	print num

def delAllTweets(api):
	''' This function deletes every tweet in the time line, deleting tweet by tweet '''
	del_total = 0
	print "Getting all tweets in current timeline..."
	allTweets = []
	try:
		while True:
			timeline = api.user_timeline(count = 350)
			if len(timeline) < 1:
				print "There is no timeline"
				break

			else:
				allTweets.extend(timeline)

		print "Found: %d\nRemoving..." % (len(allTweets))
		for t in allTweets: # Delete tweets one by one
			api.destroy_status(t.id)
			del_total += 1
			print "tweet #%d deleted" % del_total

		print "Every available tweet in your account has been removed!"
	
	except tweepy.TweepError:
		print "Make sure you have a stable connection to Internet..."
		time.sleep(5)
	except tweepy.RateLimitError:
		print "Rate limit reached, wait 15mins..."
		time.sleep(15 * 60)


def tweetFromList(api):
	''' This tweets a list of tweets in the tweetList every different tweet is on a different line '''
	num_line = 0

	with open('numero.pickle', 'rb') as fLoad:
		line_number = int(cPickle.load(fLoad))

	with open('tweetList.txt', 'r') as tweetsFile:
		f = tweetsFile.readlines()

	hashtag = raw_input("Enter a hashtag if you want to use one for all of the tweets else just press enter: ")
	try:
		for line in f:
			line = line+" "+hashtag
			line = line.strip()
			line = line.strip('\n')

			if num_line == line_number and line != f[-1] and len(line) <= 140:
				num_line+=1
				line_number+=1

				with open('numero.pickle', 'wb') as fWrite:
					_pickle.dump(num_line, fWrite)

				api.update_status(status=line)
				print line
				wating_dig = int(random.random()*5+15) * 60
				print wating_dig/60
				time.sleep(wating_dig) # n minutes

			elif line == f[-1] and len(line) <= 140:
				num_line = 0
				with open('numero.pickle', 'wb') as fWrite:
					_pickle.dump(num_line, fWrite)

				api.update_status(status=line)
				print line

			else:
				if len(line) >140:
					line_number+=1
				num_line+=1
				print "Next Line %d" % (num_line)
				continue

	except tweepy.TweepError:
		print "Make sure you have a stable connection to Internet..."
		time.sleep(5)

	except tweepy.RateLimitError:
		print "Rate limit reached, wait 15mins..."
		time.sleep(15 * 60)

def unfollowNonFollowers(api):
	num = 0
	followers = []
	friends = []
	print "Loading followers.."
	
	for follower in limit_handled(tweepy.Cursor(api.followers).items()):
		followers.append(follower)
		print "Follower: %s" % follower.screen_name
		time.sleep(1)

	print "Found %s followers, finding friends.." % len(followers)
	for friend in limit_handled(tweepy.Cursor(api.friends).items()):
		friends.append(friend)
		print "Friend: %s" % friend.screen_name
		time.sleep(1)

	# creating dictionaries based on id's is handy too

	friend_dict = {}
	for friend in friends:
		friend_dict[friend.id] = friend

	follower_dict = {}
	for follower in followers:
		follower_dict[follower.id] = follower

	# now we find all your "non_friends" - people who don't follow you
	# even though you follow them.

	non_friends = [friend for friend in friends if friend.id not in follower_dict]

	# Double Check cuz... you know... users...

	print "Unfollowing %s people who don't follow you back" % len(non_friends)
	print "This will take approximately %s minutes." % (len(non_friends) / 60.0)
	answer = raw_input("Are you sure? [Y/n]: ").lower()
	if answer and answer[0] != "y":
		sys.exit(1)

	for nf in non_friends:
		try:
			nf.unfollow()
			print "%s was unfollowed" % nf.screen_name
			time.sleep(random.randint(1, 3))
		except tweepy.TweepError:
			print "Failed... Wait 5s...."
			time.sleep(5)
			nf.unfollow()
	print "Succesfully unfollowed non-followers!"

def unfollowAll(api):
	''' This will unfollow every friend '''
	print "Setting up..."
	# Double Check cuz... you know... users...
	answer = raw_input("Are you sure? There is no coming back after this [Y/n]: ").lower()
	if answer and answer[0] != "y":
		sys.exit(1)

	for friend in limit_handled(tweepy.Cursor(api.friends).items()):
		print "Unfollowing %s" % friend.screen_name
		friend.unfollow()
		time.sleep(1)

def sendDMToAll(api):
	''' This function takes as an argument the message to send to every contact possible as a DM '''
	def DirectMessage(userId, messageText):
		api.send_direct_message(screen_name=userId, text=messageText)

	followers = list()
	def GetFollowers():
		for follower in limit_handled(tweepy.Cursor(api.followers).items()):  # For each follower i have
			followers.append(follower.screen_name)
		return followers # Return list of new followers

	try:
		GetFollowers()
		messageText = raw_input("Enter the message you want to send: ")
		for follower in followers:
			DirectMessage(follower, messageText) # Send them a dm
			time.sleep(random.randint(1, 3))
	except tweepy.RateLimitError:
		time.sleep(17 * 60)
		print "Too many requests wait 17 minutes..."

def delAllDm(api):
	''' This will delete every DM send and received '''
	try:
		for page in tweepy.Cursor(api.sent_direct_messages, count=100).pages():
			for dm in page:
				#print dm.text #This shows DM's text
				api.destroy_direct_message(dm.id)
	except tweepy.RateLimitError:
		print "Rate limit reached, wait 15 mins..."
		time.sleep(15 * 60)
	except tweepy.TweepError:
		print "Make sure you have a stable connection to Internet..."
