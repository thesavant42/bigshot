# Story 001
## As a bug bounty hunter, 

As a bug bounty hunter, I want to view an up to date dashbard, with various charts of bounty info over time. A slide-out chat interface allows me to use natural chat with an agentic local Large Laguage Model, hosted "on prem" at `192.168.1.98:1234` . The mcp server is being hosted by a docker container running on the same host as LMStudio, `192.168.1.98`

_I ask the model, which I have nicknamed oso:_ **"oso, who is paying out this week? What else is new?"** _which is a verbal macro to run several queries:_
-- Of my "favorited" (or enrolled) projects, who has paid out the most recently?"
		"recently" in this case is a short hand for :
      -- last 7 days
		  -- 30 days
		  -- 90 days

- The Top 5 programs, divided by project  
 - Top 5 paying programs, with details Per program, (sorted by dollar per recent payout period. will be returned as results:
 	Here is an example first project "Program One - Savants Demo":
 		-- alongside the dollar mount for that pay period:
 		 07 days: $1337 in the last 7 days, 
 		 30 days: $10,000 in the last 30 days, 
 		 90 days: 1 zillion dollars in the last 90 days"

	 - "There are 42 hackers, including you,  engaged in this project."

	 - You are currently ranked at YY/XX hackers in this project
 
		 - Top 10 Scores on the Leeter Board:
		 | Rank  Hacker  					| Rank  hackers				|
		 | 1. 100 points hacker_a 			| 6. 095 points fuzzynop 	|
		 | 2. 099 points charlie_root 		| 7. 094 points christrainor |
		 | 3. 098 points cmienel 			| 8. 093 points phiberoptik |
		 | 4. 097 points drdoom 			| 9. 092 points jeffe |
		 | 5. 096 points zerocool 			| 10.091 points  thesleep |

		You are: NOT on the leeter board
		Your rank: 025. 042 pointa 
		You need AT LEAST: +50 points to break into the Top 10 for Savant's Demo" 
		-- 

		... repeated with information from each of my favorites projects. 

# "What else is new" 
Triggers a function that queries for meaningful updates: 
	- new notifications, 
 	- new invitations, 
  	- changes in status for open items in my hackerone profile), etc...
   OSO reads me a description of these events in summary, and I can ask for more details.
   
"OSO, who are the newest companies to open bug bunty programs with hacker1? I'd like a summary of their names, and the option to learn more"

OSO/LLM uses the mcp to query who the newest companies are, displaays a banner's worth of informatio about each participant.

User asks: "_OSO, check my reputation, how is the trend over time? What actions can I taake to quickly increase my rank? Search the web._"
OSO replies: 
	"**Your score is currently 42 for this period, and is trending UPWARD.** 
        **The next 5 hackers above you are 100 points+ ahead. I am not sure how to increase your rank, let me search the web....**"
 <<searches with bravesearch mcp </searches> 
	**"According to madeup site.com, you can do glalllalallala to quickly gain 100 points"**

_User query to the AI_: "OSO, for each of the Top 5 biggest payts this $PERIOD, 
 1. add them each to my faovrites list, if they are not already there
 2. download and parse the scopes file for that project from hacker1"
 3. parse hosts/domains/IP ranges/ASIN numbers, CIDR notation, and any other possible scope level objects to an "attack surface" overview. 


## On SCOPE, ASSETS, HOSTS and other classifiers

See https://docs.hackerone.com/en/articles/8593105-asset-details-and-scoping for more info on scope, but note that this documentation is for the project admin api, not for the hackers API. This information is purely demonstrational.

 HOSTS are any machines or programs capable of running in-scope services over the Internet, or other inscope fabric. 
 A HOST must always have a unique identifier
 Multiple hosts/vhosts may share the same IP address, or load balancer, or egress, etc, so a guid would be good.
 A HOST may be referred to by: 
 	- Domain/subdomain/hostname
 	- IP Addresses
 	- CIDR Notation(rare, not needed for mvp uless its an easy win)
A HOST can have many attributes
a HOST can have the same attributes as other hosts
 - but not in every case. A guid must be globally unique
A HOST may be "online" but not directly accessible from bigshot's vantage on the netowrk.
