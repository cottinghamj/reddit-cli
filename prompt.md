let's making a planning doc called "plan.md" for the work we're going to do in this project. You're making this doc as your notes docs so that you can come back and implement all of it later. 

I want to build an reddit cli interface so that I can navigate through some of the reddit posts on the cli. I want the interface to be intuitive and very easy to read. 

The core feature is search. When I search, i want it to bring up all the posts that are under that search term. It can just bring up the first 15 results for the first page. Then if I type 'n' it should show the next 15 and so on.

Each post should be numbered. Also have a column in the table with the name of the subreddit and another column with the date the thread was created. 

The user should be able to click one of the numbers of the post and then you should go into the post to view it. 

For the view of a post, you should show the main body of text of the post. If they user would like a summary of the article, they can press 's' to get a summary, then you should send the body of the text and the 100 random comments to the gpt-oss:20b model running on a network server under  ip 192.168.8.223:11434. Ask the ai to give the summary and then present the summary to the user.

When the user is viewing the post, they can click c to see the comments on the post. Each time they press c, let them see each line of comments.
